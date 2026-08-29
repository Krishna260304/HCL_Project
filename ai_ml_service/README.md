# LearnPath AI - AI/ML Microservice

Autonomous, high-performance AI/ML microservice for the **LearnPath AI** platform.

This service is completely decoupled from the Django application backend and provides core intelligence including:
- **Qwen LLM Inference** (4-bit/8-bit memory-aware local loading, vLLM/Ollama OpenAI-compatible endpoints, and Mock mode)
- **BAAI/bge-m3 Embeddings** (Singleton provider with dynamic chunk batching)
- **Qdrant Vector Database Retrieval** (Remote cluster or local in-memory fallback)
- **Hybrid Retrieval & Reranking** (Reciprocal Rank Fusion and Cross-Encoder ranking)
- **LangGraph Workflows** (Typed state graphs for Goal Analysis, Assessment Generation, Skill Estimation, Learning Path Synthesis, RAG, and Adaptive Learning)

---

## 1. System Architecture

```
Frontend (React/TypeScript)
      |
      | WebSocket
      v
Django Backend (Central Authority: Users, Auth, DB, Scoring, Progress)
      |
      | HTTP (Bearer Token Authenticated)
      v
AI/ML Microservice (FastAPI on Port 8001)
      |
      +-----------------------------+
      |              |              |
      v              v              v
  Qwen LLM      BGE-M3 Embeds   Qdrant Vectors
 (4-bit NF4)    (1024-dim)      (Cosine Index)
      |              |              |
      +--------------+--------------+
                     |
                     v
             LangGraph Workflows
                     |
                     v
             Structured Results -> Django Backend
```

---

## 2. Hardware & VRAM Optimization (RTX 5050 ~8 GB VRAM)

The service is specifically optimized for limited VRAM environments:
- **4-bit NF4 Quantization**: By default loads Qwen 8B-class models using `bitsandbytes` NF4 quantization with double quantization, consuming ~4.8 GB VRAM.
- **Singleton Embedding Service**: BAAI/bge-m3 model is loaded once at startup and shared across all request lifecycles.
- **CPU Fallback**: Automatic graceful fallback to CPU float32 if CUDA or `bitsandbytes` is not available.
- **Mock Mode**: Set `AI_MOCK_MODE=true` to develop and run the complete API test suite with 0 GPU consumption.

---

## 3. API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Service status, model status, and GPU memory diagnostics |
| `POST` | `/v1/goal/analyze` | Decompose natural language goals into domains, skills, and timelines |
| `POST` | `/v1/assessment/generate` | Generate diagnostic MCQ questions with deterministic psychometric validation |
| `POST` | `/v1/skills/analyze` | Compute verified skill levels vs self-reported data and identify gaps |
| `POST` | `/v1/resources/analyze` | Extract skills, difficulty, prerequisites, and quality signals |
| `POST` | `/v1/resources/batch-ingest`| Batch embed and store resources in Qdrant |
| `POST` | `/v1/recommendations/generate` | Multi-factor hybrid ranking with grounded explanations |
| `POST` | `/v1/learning-path/generate` | Multi-phase DAG-validated personalized learning roadmap |
| `POST` | `/v1/rag/query` | Citation-grounded RAG answers from verified knowledge documents |
| `POST` | `/v1/assistant/chat` | Context-aware AI tutor chat |
| `POST` | `/v1/assistant/stream` | Token streaming endpoint for conversational assistance |
| `POST` | `/v1/adaptive/update` | Ingest new assessment scores and adapt learning roadmaps |

*(Legacy root aliases e.g. `/goal-analysis`, `/assessment-generation`, `/learning-path` are also supported for direct Django backward compatibility).*

---

## 4. Getting Started

### Local Development (Python 3.11+)

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   ```

3. **Run Dev Server**:
   ```bash
   # Linux/macOS:
   ./scripts/run_dev.sh

   # Windows / Direct:
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
   ```

### Docker Deployment

```bash
docker compose up -d --build
```

---

## 5. Running Tests & Benchmarks

```bash
# Run full pytest test suite
pytest tests/ -v

# Run offline evaluation metrics (NDCG@K, Recall@K, Precision@K)
python scripts/evaluate_all.py

# Run component latency benchmark
python scripts/benchmark.py
```
