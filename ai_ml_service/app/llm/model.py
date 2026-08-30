"""
LLM Provider Abstraction and Implementations.
Supports Local Transformers (4-bit/8-bit Qwen with CPU fallback), OpenAI-compatible (vLLM/Ollama), and Mock Mode.
"""

from abc import ABC, abstractmethod
import asyncio
import json
import logging
from typing import Any, AsyncIterator, Dict, Optional, Type, TypeVar
from pydantic import BaseModel
from app.core.config import Settings, get_settings
from app.core.exceptions import ModelInferenceError, ModelUnavailableError
from app.utils.json import extract_json_from_text

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class LLMProvider(ABC):
    """Abstract base class for swappable LLM inference engines."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> str:
        """Generate unstructured text completion."""
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema_cls: Type[T],
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> T:
        """Generate structured completion adhering strictly to a Pydantic schema."""
        pass

    @abstractmethod
    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Stream generated text chunks asynchronously."""
        pass

    @abstractmethod
    def is_ready(self) -> bool:
        """Check if provider and model weights are initialized and ready to serve."""
        pass


class LocalTransformersProvider(LLMProvider):
    """
    Local PyTorch/Transformers inference provider optimized for 8GB VRAM RTX GPUs.
    Applies 4-bit NF4 quantization and keeps inference on the configured CUDA device.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.model_name = settings.LLM_MODEL_PATH or settings.LLM_MODEL_NAME
        self.tokenizer = None
        self.model = None
        self._initialized = False
        self._lock = asyncio.Lock()

    def _load_model_sync(self) -> None:
        if self._initialized:
            return

        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        logger.info(f"Initializing Local LLM: {self.model_name}")
        has_cuda = torch.cuda.is_available()

        # Tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True,
        )

        load_kwargs: Dict[str, Any] = {
            "trust_remote_code": True,
            "low_cpu_mem_usage": True,
        }

        if has_cuda and self.settings.LLM_LOAD_IN_4BIT:
            try:
                from transformers import BitsAndBytesConfig
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_use_double_quant=True,
                )
                load_kwargs["quantization_config"] = bnb_config
                load_kwargs["device_map"] = self.settings.LLM_DEVICE_MAP
                logger.info("Using 4-bit BitsAndBytes quantization on CUDA")
            except ImportError:
                logger.warning("bitsandbytes not available, loading in float16")
                load_kwargs["torch_dtype"] = torch.float16
                load_kwargs["device_map"] = self.settings.LLM_DEVICE_MAP
        elif has_cuda and self.settings.LLM_LOAD_IN_8BIT:
            load_kwargs["load_in_8bit"] = True
            load_kwargs["device_map"] = self.settings.LLM_DEVICE_MAP
        elif has_cuda:
            load_kwargs["torch_dtype"] = torch.float16
            load_kwargs["device_map"] = self.settings.LLM_DEVICE_MAP
        else:
            raise RuntimeError("CUDA is required for the local Transformers LLM; CPU fallback is disabled.")

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            **load_kwargs
        )
        self.model.eval()
        self._initialized = True
        logger.info(f"Local LLM {self.model_name} successfully loaded.")

    async def ensure_loaded(self) -> None:
        if not self._initialized:
            async with self._lock:
                if not self._initialized:
                    await asyncio.to_thread(self._load_model_sync)

    def is_ready(self) -> bool:
        return self._initialized

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> str:
        await self.ensure_loaded()
        import torch

        max_new_tokens = max_tokens or self.settings.LLM_MAX_TOKENS
        temp = temperature if temperature is not None else self.settings.LLM_TEMPERATURE

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        def _run_inference():
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
            model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

            with torch.no_grad():
                generated_ids = self.model.generate(
                    **model_inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=max(temp, 0.01) if temp > 0 else None,
                    do_sample=temp > 0,
                    pad_token_id=self.tokenizer.eos_token_id,
                )
            generated_ids = [
                output_ids[len(input_ids) :]
                for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]
            response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            return response

        try:
            return await asyncio.to_thread(_run_inference)
        except Exception as exc:
            logger.error(f"Local LLM inference error: {str(exc)}", exc_info=True)
            raise ModelInferenceError(f"Local inference failure: {str(exc)}")

    async def generate_structured(
        self,
        prompt: str,
        schema_cls: Type[T],
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> T:
        schema_json = json.dumps(schema_cls.model_json_schema(), indent=2)
        augmented_system = (
            (system_prompt or "You are an expert AI system for personalized learning.")
            + f"\n\nCRITICAL INSTRUCTION: You MUST respond ONLY with valid JSON conforming to this JSON Schema:\n```json\n{schema_json}\n```\nDo not include any preamble or extra text outside the JSON."
        )

        response_text = await self.generate(
            prompt=prompt,
            system_prompt=augmented_system,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        )

        parsed_dict = extract_json_from_text(response_text)
        if parsed_dict is not None:
            try:
                return schema_cls.model_validate(parsed_dict)
            except Exception as e:
                logger.warning(f"Schema validation error on extracted JSON: {e}. Retrying repair...")

        # Repair attempt
        repair_prompt = f"The previous output was not valid for the schema.\nSchema:\n{schema_json}\n\nInvalid output:\n{response_text}\n\nProvide the corrected JSON only:"
        repaired_text = await self.generate(
            prompt=repair_prompt,
            system_prompt="You are a strict JSON repair engine. Output ONLY valid JSON matching the schema.",
            max_tokens=max_tokens,
            temperature=0.0,
        )
        repaired_dict = extract_json_from_text(repaired_text)
        if repaired_dict is not None:
            return schema_cls.model_validate(repaired_dict)

        raise ModelInferenceError(f"Failed to generate structured output for {schema_cls.__name__}")

    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        # Full text fallback generator for streaming
        full_text = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        )
        words = full_text.split(" ")
        for word in words:
            yield word + " "
            await asyncio.sleep(0.02)


class OpenAICompatibleProvider(LLMProvider):
    """Provider connecting to vLLM, Ollama, or OpenAI-compatible local server."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_url = settings.LLM_OPENAI_BASE_URL.rstrip("/")
        self.api_key = settings.LLM_OPENAI_API_KEY
        self.model_name = settings.LLM_MODEL_NAME

    def is_ready(self) -> bool:
        return True

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> str:
        import httpx

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tokens or self.settings.LLM_MAX_TOKENS,
            "temperature": temperature if temperature is not None else self.settings.LLM_TEMPERATURE,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}

        async with httpx.AsyncClient(timeout=self.settings.LLM_TIMEOUT) as client:
            try:
                resp = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
                if resp.status_code != 200:
                    raise ModelUnavailableError(f"OpenAI server returned status {resp.status_code}: {resp.text}")
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                raise ModelInferenceError(f"HTTP LLM Provider error: {str(e)}")

    async def generate_structured(
        self,
        prompt: str,
        schema_cls: Type[T],
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> T:
        schema_json = json.dumps(schema_cls.model_json_schema(), indent=2)
        augmented_system = (
            (system_prompt or "You are an expert AI system for personalized learning.")
            + f"\n\nRespond ONLY with valid JSON matching:\n```json\n{schema_json}\n```"
        )
        response_text = await self.generate(prompt, augmented_system, max_tokens, temperature, **kwargs)
        parsed = extract_json_from_text(response_text)
        if parsed:
            return schema_cls.model_validate(parsed)
        raise ModelInferenceError(f"Failed to parse structured response from endpoint for {schema_cls.__name__}")

    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        full_text = await self.generate(prompt, system_prompt, max_tokens, temperature, **kwargs)
        for chunk in full_text.split(" "):
            yield chunk + " "
            await asyncio.sleep(0.01)


class MockLLMProvider(LLMProvider):
    """
    Deterministic Mock LLM Provider for zero-GPU development, CI/CD, and offline testing.
    Produces high-fidelity, schema-valid synthetic responses.
    """

    def __init__(self, settings: Settings):
        self.settings = settings

    def is_ready(self) -> bool:
        return True

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> str:
        prompt_lower = prompt.lower()
        if "question" in prompt_lower or "assessment" in prompt_lower:
            return "Generated diagnostic assessment question evaluating memory management and data structures."
        elif "goal" in prompt_lower:
            return "Goal analyzed: Machine Learning Engineer with focus on Python, PyTorch, and MLOps."
        elif "explain" in prompt_lower:
            return "This resource is recommended because it closes your identified skill gap in Deep Learning."
        return "LearnPath AI Mock LLM response processed successfully."

    async def generate_structured(
        self,
        prompt: str,
        schema_cls: Type[T],
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> T:
        schema_name = schema_cls.__name__

        if "GoalAnalysisData" in schema_name:
            data = {
                "goal": "Machine Learning Engineer",
                "goal_type": "career_advancement",
                "target_outcome": "Employment as a Production ML Engineer",
                "timeline": "12-16 weeks",
                "required_domains": ["Machine Learning", "Deep Learning", "MLOps", "Software Engineering"],
                "recommended_domains": ["Machine Learning", "Deep Learning", "MLOps"],
                "required_skills": ["Python", "PyTorch", "Data Structures", "Docker", "Model Deployment"],
                "possible_roles": ["ML Engineer", "Data Scientist", "AI Engineer"],
                "confidence": 0.95,
            }
            return schema_cls.model_validate(data)

        elif "AssessmentData" in schema_name or "MCQQuestion" in schema_name:
            if "MCQQuestion" in schema_name:
                data = {
                    "id": "q_diag_mock_1",
                    "question": "What is the primary advantage of residual connections in deep ResNet architectures?",
                    "options": [
                        "They mitigate the vanishing gradient problem in very deep networks",
                        "They reduce the number of parameters by half",
                        "They eliminate the need for activation functions",
                        "They guarantee 100% training accuracy in fewer than 5 epochs",
                    ],
                    "correct_answer": "They mitigate the vanishing gradient problem in very deep networks",
                    "skill": "Deep Learning",
                    "skill_id": "deep_learning",
                    "topic": "ResNet Architectures",
                    "difficulty": "intermediate",
                    "learning_objective": "Understand vanishing gradient mitigation via skip connections",
                    "explanation": "Residual connections allow gradients to flow directly through skip connections without attenuation.",
                }
                return schema_cls.model_validate(data)
            else:
                data = {
                    "title": "Machine Learning Diagnostic Assessment",
                    "description": "Comprehensive diagnostic evaluation of ML foundations and practical concepts",
                    "difficulty": "intermediate",
                    "duration": 25,
                    "skill_ids": ["Python", "Machine Learning", "Deep Learning"],
                    "topic_ids": ["Loss Functions", "Backpropagation", "Gradient Descent", "Model Evaluation"],
                    "questions": [
                        {
                            "id": "q_1",
                            "question": "Which loss function is most suitable for multi-class classification with one-hot encoded targets?",
                            "options": [
                                "Categorical Cross-Entropy",
                                "Mean Squared Error",
                                "Binary Cross-Entropy",
                                "Hinge Loss",
                            ],
                            "correct_answer": "Categorical Cross-Entropy",
                            "skill": "Machine Learning",
                            "skill_id": "machine_learning",
                            "topic": "Loss Functions",
                            "difficulty": "intermediate",
                            "learning_objective": "Select appropriate loss functions for classification tasks",
                            "explanation": "Categorical Cross-Entropy measures the dissimilarity between predicted probability distributions and one-hot labels.",
                        },
                        {
                            "id": "q_2",
                            "question": "How does L2 regularization (Ridge) prevent overfitting in linear models?",
                            "options": [
                                "Penalizes the sum of squared weight coefficients to shrink weights towards zero",
                                "Sets arbitrary coefficients strictly to zero for sparse feature selection",
                                "Increases the learning rate dynamically on validation plateau",
                                "Duplicates dataset samples with random Gaussian noise",
                            ],
                            "correct_answer": "Penalizes the sum of squared weight coefficients to shrink weights towards zero",
                            "skill": "Machine Learning",
                            "skill_id": "machine_learning",
                            "topic": "Regularization",
                            "difficulty": "intermediate",
                            "learning_objective": "Understand mathematical impact of L2 weight penalty",
                            "explanation": "L2 regularization adds a penalty proportional to the square of the magnitude of coefficients, preventing weights from growing too large.",
                        },
                        {
                            "id": "q_3",
                            "question": "In PyTorch, what is the purpose of calling optimizer.zero_grad() before loss.backward()?",
                            "options": [
                                "Clears accumulated gradients from previous iterations to prevent gradient accumulation",
                                "Resets model weights to their initial random seeds",
                                "Zeroes out the computed loss tensor to save GPU memory",
                                "Freezes dropout and batch normalization layers",
                            ],
                            "correct_answer": "Clears accumulated gradients from previous iterations to prevent gradient accumulation",
                            "skill": "Deep Learning",
                            "skill_id": "deep_learning",
                            "topic": "PyTorch Training Loop",
                            "difficulty": "intermediate",
                            "learning_objective": "Master standard PyTorch gradient management",
                            "explanation": "By default in PyTorch, gradients accumulate in buffers during backward passes. zero_grad() resets them before each new step.",
                        },
                    ],
                    "confidence": 0.94,
                }
                return schema_cls.model_validate(data)

        elif "SkillAnalysisData" in schema_name:
            data = {
                "skills": {
                    "Python": 0.91,
                    "Machine Learning": 0.82,
                    "Statistics": 0.74,
                    "Deep Learning": 0.43,
                    "MLOps": 0.20,
                },
                "verified_scores": {
                    "Python": 0.91,
                    "Machine Learning": 0.82,
                    "Deep Learning": 0.43,
                },
                "estimated_skill_levels": {
                    "Python": 91.0,
                    "Machine Learning": 82.0,
                    "Statistics": 74.0,
                    "Deep Learning": 43.0,
                    "MLOps": 20.0,
                },
                "strengths": ["Python", "Machine Learning"],
                "weaknesses": ["Deep Learning", "MLOps"],
                "skill_gaps": [
                    {
                        "skill": "Deep Learning",
                        "current_score": 0.43,
                        "target_score": 0.80,
                        "gap_magnitude": 0.37,
                        "priority": "high",
                    },
                    {
                        "skill": "MLOps",
                        "current_score": 0.20,
                        "target_score": 0.75,
                        "gap_magnitude": 0.55,
                        "priority": "high",
                    },
                ],
                "recommended_next_skills": ["Deep Learning Foundations", "Docker for ML Engineers"],
                "confidence": 0.92,
            }
            return schema_cls.model_validate(data)

        elif "ResourceAnalysisData" in schema_name:
            data = {
                "skills": ["Deep Learning", "PyTorch"],
                "topics": ["Neural Networks", "Backpropagation", "Tensors"],
                "difficulty": "intermediate",
                "prerequisites": ["Python", "Linear Algebra"],
                "quality_score": 0.89,
                "estimated_duration": 45,
                "learning_format": "video",
                "quality_signals": {"relevance": 0.9, "clarity": 0.88},
                "summary": "Deep dive into building neural networks from scratch using PyTorch.",
                "semantic_text": "Building neural networks with PyTorch, backpropagation and tensor operations.",
                "confidence": 0.91,
            }
            return schema_cls.model_validate(data)

        elif "LearningPathData" in schema_name:
            data = {
                "title": "Machine Learning Engineer Career Acceleration",
                "description": "Systematic progression from core ML foundations to production deep learning and MLOps.",
                "goal": "Machine Learning Engineer",
                "estimated_duration_weeks": 8,
                "target_role": "ML Engineer",
                "validation_status": "validated",
                "confidence": 0.93,
                "phases": [
                    {
                        "phase_id": "phase_1",
                        "title": "Phase 1: Deep Learning & Neural Network Foundations",
                        "description": "Bridge deep learning fundamentals, backprop, and PyTorch architectures.",
                        "objective": "Build and train multi-layer perceptrons and CNNs in PyTorch",
                        "order": 1,
                        "skills": ["Deep Learning", "PyTorch"],
                        "prerequisites": ["Python", "Linear Algebra"],
                        "resources": [
                            {
                                "resource_id": "res_dl_01",
                                "title": "PyTorch for Deep Learning Complete Course",
                                "resource_type": "video",
                                "duration_minutes": 120,
                                "skills": ["Deep Learning", "PyTorch"],
                                "is_mandatory": True,
                            }
                        ],
                        "projects": [
                            {
                                "project_id": "proj_01",
                                "title": "Image Classifier with PyTorch & Transfer Learning",
                                "description": "Train and evaluate a ResNet classifier on custom image datasets.",
                                "difficulty": "intermediate",
                                "estimated_hours": 6,
                                "deliverables": ["GitHub repository", "Model weights checkpoint", "Confusion matrix report"],
                            }
                        ],
                        "milestone": "Custom PyTorch model trained with >85% validation accuracy",
                        "estimated_duration_weeks": 4,
                        "explanation": "Targeted specifically to close the verified Deep Learning skill gap (0.43 -> 0.80).",
                    },
                    {
                        "phase_id": "phase_2",
                        "title": "Phase 2: Production MLOps & Model Deployment",
                        "description": "Containerize models, construct CI/CD pipelines, and deploy FastAPI inference endpoints.",
                        "objective": "Deploy scalable ML inference microservice with Docker and monitoring",
                        "order": 2,
                        "skills": ["MLOps", "Docker", "FastAPI"],
                        "prerequisites": ["Deep Learning", "Python"],
                        "resources": [
                            {
                                "resource_id": "res_mlops_01",
                                "title": "End-to-End MLOps: Packaging and Serving Models",
                                "resource_type": "documentation",
                                "duration_minutes": 90,
                                "skills": ["MLOps", "Docker"],
                                "is_mandatory": True,
                            }
                        ],
                        "projects": [
                            {
                                "project_id": "proj_02",
                                "title": "Production Model Serving Microservice",
                                "description": "Build Dockerized FastAPI inference service with Prometheus metrics.",
                                "difficulty": "advanced",
                                "estimated_hours": 8,
                                "deliverables": ["Dockerfile", "API routes", "Load testing script"],
                            }
                        ],
                        "milestone": "Production inference API operational and containerized",
                        "estimated_duration_weeks": 4,
                        "explanation": "Closes the critical MLOps skill gap (0.20 -> 0.75) completing employability criteria.",
                    },
                ],
            }
            return schema_cls.model_validate(data)

        # Generic fallback
        return schema_cls.model_construct()

    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        text = await self.generate(prompt, system_prompt, max_tokens, temperature, **kwargs)
        for token in text.split(" "):
            yield token + " "
            await asyncio.sleep(0.01)


class LLMFactory:
    """Factory and registry for instantiating LLM providers."""

    _instance: Optional[LLMProvider] = None

    @classmethod
    def get_provider(cls, settings: Optional[Settings] = None) -> LLMProvider:
        if cls._instance is not None:
            return cls._instance

        cfg = settings or get_settings()

        if cfg.AI_MOCK_MODE or cfg.LLM_PROVIDER == "mock":
            logger.info("Instantiating MockLLMProvider (AI_MOCK_MODE=True)")
            cls._instance = MockLLMProvider(cfg)
        elif cfg.LLM_PROVIDER == "openai_compatible":
            logger.info(f"Instantiating OpenAICompatibleProvider ({cfg.LLM_OPENAI_BASE_URL})")
            cls._instance = OpenAICompatibleProvider(cfg)
        else:
            logger.info(f"Instantiating LocalTransformersProvider ({cfg.LLM_MODEL_NAME})")
            cls._instance = LocalTransformersProvider(cfg)

        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset singleton for testing."""
        cls._instance = None
