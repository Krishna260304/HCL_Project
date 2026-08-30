from typing import Any, Dict, List
from ai_integrations.client import BaseAIClient
from ai_integrations.exceptions import ExternalAIServiceUnavailableError

class AssessmentGenerationClient:
    endpoint = 'assessment-generation'

    @classmethod
    def generate_assessment(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        payload = dict(payload)
        payload['num_questions'] = max(5, min(10, int(payload.get('num_questions', 5))))
        try:
            raw_response = BaseAIClient.post(cls.endpoint, payload, timeout=120)
            return cls.normalize_response(raw_response)
        except Exception:
            return cls.fallback_response(payload)

    @classmethod
    def normalize_response(cls, response: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'title': response.get('title', 'AI Diagnostic Assessment'),
            'description': response.get('description', 'AI generated assessment tailored to your background'),
            'difficulty': response.get('difficulty', 'intermediate'),
            'duration': response.get('duration', 20),
            'skill_ids': response.get('skill_ids', []),
            'topic_ids': response.get('topic_ids', []),
            'questions': response.get('questions', []),
        }

    @classmethod
    def fallback_response(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        difficulty = payload.get('difficulty', payload.get('experience_level', 'intermediate')).lower()
        skills = payload.get('skills', []) or ['General Programming']
        goal = payload.get('goal', 'Software Engineer')
        question_count = max(5, min(10, int(payload.get('num_questions', 5))))

        # Domain-aware diagnostic question bank
        question_bank: Dict[str, List[Dict[str, Any]]] = {
            'python': [
                {
                    'question': 'How does Python handle memory management for objects under the hood?',
                    'options': [
                        'Reference counting combined with a generational cyclic garbage collector',
                        'Manual allocate and deallocate syscalls',
                        'Pure mark-and-sweep garbage collection exclusively',
                        'Compile-time static stack allocation only'
                    ],
                    'correct_answer': 'Reference counting combined with a generational cyclic garbage collector',
                    'explanation': 'CPython utilizes reference counting as its primary memory management mechanism along with generational garbage collection to resolve reference cycles.',
                    'skill_id': 'Python',
                    'topic': 'Memory Management & Garbage Collection',
                    'learning_objective': 'Understand Python memory management and cyclic GC architecture.',
                    'difficulty': difficulty
                },
                {
                    'question': 'What is the purpose of Python generators and the yield statement?',
                    'options': [
                        'Produce an iterator that lazily yields values one at a time to optimize memory usage',
                        'Enforce compile-time type safety across functions',
                        'Spawn asynchronous OS-level background threads',
                        'Prevent race conditions on global shared state'
                    ],
                    'correct_answer': 'Produce an iterator that lazily yields values one at a time to optimize memory usage',
                    'explanation': 'Generators enable lazy evaluation, computing values on-the-fly without holding the entire sequence in memory.',
                    'skill_id': 'Python',
                    'topic': 'Iterators & Generators',
                    'learning_objective': 'Leverage generator functions for memory-efficient data streaming.',
                    'difficulty': difficulty
                }
            ],
            'statistics': [
                {
                    'question': 'In hypothesis testing, what is a Type I error (False Positive)?',
                    'options': [
                        'Rejecting the null hypothesis when it is actually true',
                        'Failing to reject the null hypothesis when it is false',
                        'Having insufficient sample size for statistical significance',
                        'Selecting an unrepresentative sample distribution'
                    ],
                    'correct_answer': 'Rejecting the null hypothesis when it is actually true',
                    'explanation': 'A Type I error occurs when the true null hypothesis is incorrectly rejected (denoted by alpha).',
                    'skill_id': 'Statistics',
                    'topic': 'Hypothesis Testing',
                    'learning_objective': 'Distinguish Type I and Type II statistical errors in empirical analysis.',
                    'difficulty': difficulty
                },
                {
                    'question': 'What does the Central Limit Theorem state regarding the sample mean distribution?',
                    'options': [
                        'As sample size increases, the sampling distribution of the mean approaches normality regardless of the population distribution',
                        'All populations become normally distributed when normalized',
                        'The variance of the sample mean is equal to the population variance',
                        'The mean and median of any distribution are equal given sufficient samples'
                    ],
                    'correct_answer': 'As sample size increases, the sampling distribution of the mean approaches normality regardless of the population distribution',
                    'explanation': 'The Central Limit Theorem guarantees that the distribution of sample means converges to a Gaussian distribution as sample size grows large.',
                    'skill_id': 'Statistics',
                    'topic': 'Distribution Theory',
                    'learning_objective': 'Apply the Central Limit Theorem to inferential statistics.',
                    'difficulty': difficulty
                }
            ],
            'machine_learning': [
                {
                    'question': 'How does L2 regularization (Ridge) reduce overfitting in linear regression models?',
                    'options': [
                        'Penalizes the sum of squared weights, shrinking coefficients toward zero without setting them to exact zero',
                        'Forces non-essential feature weights to exactly zero for feature selection',
                        'Randomly drops neurons during training iterations',
                        'Increases the learning rate dynamically to escape local minima'
                    ],
                    'correct_answer': 'Penalizes the sum of squared weights, shrinking coefficients toward zero without setting them to exact zero',
                    'explanation': 'L2 adds the squared magnitude of coefficients to the loss function, smoothing variance and penalizing excessive weights.',
                    'skill_id': 'Machine Learning',
                    'topic': 'Regularization Techniques',
                    'learning_objective': 'Understand how regularization reduces model variance and prevents overfitting.',
                    'difficulty': difficulty
                },
                {
                    'question': 'When evaluating a model on an imbalanced classification dataset, which metric is generally preferred over standard accuracy?',
                    'options': [
                        'Precision-Recall AUC (PR-AUC) or F1-Score',
                        'Raw accuracy percentage',
                        'Mean Squared Error (MSE)',
                        'R-squared goodness of fit'
                    ],
                    'correct_answer': 'Precision-Recall AUC (PR-AUC) or F1-Score',
                    'explanation': 'In highly skewed class distributions, standard accuracy gives a misleading sense of performance; PR-AUC and F1 account for minority class recall and precision.',
                    'skill_id': 'Machine Learning',
                    'topic': 'Model Evaluation & Metrics',
                    'learning_objective': 'Select appropriate evaluation metrics for skewed classification problems.',
                    'difficulty': difficulty
                }
            ],
            'deep_learning': [
                {
                    'question': 'Why is Scaled Dot-Product Attention scaled by the square root of the key dimension (sqrt(d_k)) in Transformers?',
                    'options': [
                        'To prevent large dot products from pushing softmax into regions with vanishingly small gradients',
                        'To normalize the output vector length to unit variance',
                        'To reduce the computational time complexity from O(N^2) to O(N)',
                        'To enforce causality and mask out future tokens'
                    ],
                    'correct_answer': 'To prevent large dot products from pushing softmax into regions with vanishingly small gradients',
                    'explanation': 'For large d_k, dot products grow large in magnitude, causing softmax to yield steep peaks with tiny gradients; dividing by sqrt(d_k) stabilizes backpropagation.',
                    'skill_id': 'Deep Learning',
                    'topic': 'Transformers & Attention Mechanisms',
                    'learning_objective': 'Understand self-attention mathematical formulation and gradient stabilization.',
                    'difficulty': difficulty
                },
                {
                    'question': 'What problem does Residual Connections (Skip Connections) solve in deep neural network architectures like ResNet?',
                    'options': [
                        'Vanishing and exploding gradient problem during backpropagation through very deep layers',
                        'High inference latency on mobile CPU architectures',
                        'Overfitting due to excessive parameter count',
                        'Non-deterministic weight initialization'
                    ],
                    'correct_answer': 'Vanishing and exploding gradient problem during backpropagation through very deep layers',
                    'explanation': 'Residual shortcuts allow gradient flow directly across layers via identity mappings, enabling training of networks with hundreds of layers.',
                    'skill_id': 'Deep Learning',
                    'topic': 'Neural Network Architectures',
                    'learning_objective': 'Explain the structural benefits of residual skip connections.',
                    'difficulty': difficulty
                }
            ],
            'web_development': [
                {
                    'question': 'What is the primary benefit of utilizing React Server Components (RSC)?',
                    'options': [
                        'Zero client-side JavaScript bundle footprint for server-only components while retaining interactive client leaves',
                        'Eliminates the need for CSS styling files',
                        'Replaces REST APIs with direct WebSocket sockets automatically',
                        'Runs asynchronous code directly on the GPU'
                    ],
                    'correct_answer': 'Zero client-side JavaScript bundle footprint for server-only components while retaining interactive client leaves',
                    'explanation': 'Server components execute exclusively on the server, avoiding sending component code or server-side dependencies to the client bundle.',
                    'skill_id': 'Web Development',
                    'topic': 'Frontend Architecture & Rendering',
                    'learning_objective': 'Understand hybrid server/client component execution models.',
                    'difficulty': difficulty
                },
                {
                    'question': 'What does Cross-Origin Resource Sharing (CORS) enforce in browser web security?',
                    'options': [
                        'A browser mechanism allowing servers to specify which origins are permitted to access their resources',
                        'An encryption protocol replacing TLS/SSL',
                        'A firewall rule restricting private subnets',
                        'A database transaction isolation level'
                    ],
                    'correct_answer': 'A browser mechanism allowing servers to specify which origins are permitted to access their resources',
                    'explanation': 'CORS is a browser-enforced security standard that controls cross-origin HTTP requests via specialized HTTP response headers.',
                    'skill_id': 'Web Development',
                    'topic': 'Web Security & Network Protocols',
                    'learning_objective': 'Diagnose and implement secure cross-origin communication policies.',
                    'difficulty': difficulty
                }
            ],
            'cloud_devops': [
                {
                    'question': 'What is the key principle of Infrastructure as Code (IaC) with tools like Terraform?',
                    'options': [
                        'Managing and provisioning compute infrastructure through machine-readable definition files with declarative state',
                        'Compiling microservice source code into assembly binaries',
                        'Automating continuous manual SSH server configuration',
                        'Encrypting hard drives at the BIOS level'
                    ],
                    'correct_answer': 'Managing and provisioning compute infrastructure through machine-readable definition files with declarative state',
                    'explanation': 'IaC enables reproducible, version-controlled infrastructure definitions that prevent configuration drift across environments.',
                    'skill_id': 'DevOps & Cloud',
                    'topic': 'Infrastructure as Code & CI/CD',
                    'learning_objective': 'Apply declarative state management to automated cloud provisioning.',
                    'difficulty': difficulty
                },
                {
                    'question': 'In Kubernetes, what is the role of an Ingress Controller?',
                    'options': [
                        'Manage external HTTP/HTTPS routing, SSL termination, and load balancing to internal ClusterIP services',
                        'Schedule container pods to worker nodes based on CPU usage',
                        'Store persistent volume data on distributed block storage',
                        'Compile Dockerfiles into OCI-compliant container images'
                    ],
                    'correct_answer': 'Manage external HTTP/HTTPS routing, SSL termination, and load balancing to internal ClusterIP services',
                    'explanation': 'An Ingress Controller acts as an edge reverse proxy and traffic router for Kubernetes services.',
                    'skill_id': 'DevOps & Cloud',
                    'topic': 'Container Orchestration',
                    'learning_objective': 'Design scalable traffic ingress and routing for microservices.',
                    'difficulty': difficulty
                }
            ],
            'system_design': [
                {
                    'question': 'What trade-off does the CAP theorem describe for distributed data stores?',
                    'options': [
                        'Under network partitions (P), a distributed system can guarantee either Consistency (C) or Availability (A), but not both',
                        'Trade-off between CPU speed and Memory throughput',
                        'Trade-off between Query latency and Compression ratio',
                        'Trade-off between Read replicas and Write concurrency'
                    ],
                    'correct_answer': 'Under network partitions (P), a distributed system can guarantee either Consistency (C) or Availability (A), but not both',
                    'explanation': 'When network partitions occur, distributed data systems must either reject requests (sacrificing Availability) or return stale data (sacrificing strict Consistency).',
                    'skill_id': 'System Design',
                    'topic': 'Distributed Consensus & CAP Theorem',
                    'learning_objective': 'Evaluate distributed architectural constraints and consistency trade-offs.',
                    'difficulty': difficulty
                }
            ]
        }

        # Select domain questions matching skills & goal
        selected_questions: List[Dict[str, Any]] = []
        normalized_skills = [s.lower() for s in skills]
        goal_lower = goal.lower()

        for domain_key, q_list in question_bank.items():
            domain_name = domain_key.replace('_', ' ')
            is_relevant = any(
                domain_name in s or s in domain_name
                for s in normalized_skills
            ) or (domain_name in goal_lower)

            if is_relevant:
                selected_questions.extend(q_list)

        # Always return the requested 5–10 questions. When the selected domain
        # has too few questions, complete the diagnostic from the broad bank.
        seen_stems = {q['question'] for q in selected_questions}
        if len(selected_questions) < question_count:
            for q_list in question_bank.values():
                for question in q_list:
                    if question['question'] not in seen_stems:
                        selected_questions.append(question)
                        seen_stems.add(question['question'])
                    if len(selected_questions) >= question_count:
                        break
                if len(selected_questions) >= question_count:
                    break

        selected_questions = selected_questions[:question_count]
        for q in selected_questions:
            q['type'] = 'single_select'

        return {
            'title': f'Personalized Diagnostic Assessment · {goal}',
            'description': f'Adaptive diagnostic benchmark evaluating your core competencies across {len(selected_questions)} focused questions.',
            'difficulty': difficulty,
            'duration': max(10, len(selected_questions) * 2),
            'skill_ids': list({q.get('skill_id', '') for q in selected_questions}),
            'topic_ids': list({q.get('topic', '') for q in selected_questions}),
            'questions': selected_questions,
        }
