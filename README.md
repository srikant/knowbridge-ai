# KnowBridge AI

KnowBridge AI is a full-stack document knowledge assistant. Upload PDF, TXT, and Markdown files, search their contents, ask questions, and inspect the passages used as sources. The current retrieval engine is deliberately lightweight lexical search; semantic embeddings and a vector database are a later milestone.

## Current capabilities

- React + TypeScript workspace UI
- FastAPI backend with OpenAPI docs
- PDF, TXT, and Markdown upload with validation and upload-size limits
- SQLite persistence and overlapping text chunks
- Lexical retrieval with source excerpts
- Optional synthesized answers through OpenAI or local Ollama
- Document listing and deletion
- `/api/integrations` reports which optional frameworks are installed/configured without returning secrets
- Automated API tests

> This is an early development MVP, not a production-ready multi-tenant service. Authentication, authorization, tenant isolation, semantic embeddings, OCR, rate limiting, and production observability are not yet implemented. Do not upload confidential data.

## Requirements

- Python 3.11+
- Node.js 20+ and npm
- Git (recommended)

## Run locally

### Backend

```bash
cd backend
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

API: http://localhost:8000 · Health: http://localhost:8000/health · Docs: http://localhost:8000/docs · Integration status: http://localhost:8000/api/integrations

The SQLite database is created in `backend/data/` on first startup.

### Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. If the API uses a different URL, create `frontend/.env.local` with `VITE_API_URL=http://localhost:8000`.

## Configure a model provider

### Hosted OpenAI

Set environment variables in the shell before starting the backend.

PowerShell:

```powershell
$env:KNOWBRIDGE_LLM_PROVIDER="openai"
$env:OPENAI_API_KEY="your-key"
$env:OPENAI_MODEL="gpt-4.1-mini"
python -m uvicorn app.main:app --reload
```

macOS/Linux:

```bash
export KNOWBRIDGE_LLM_PROVIDER=openai
export OPENAI_API_KEY='your-key'
export OPENAI_MODEL=gpt-4.1-mini
python -m uvicorn app.main:app --reload
```

Never commit API keys or place them in frontend variables.

### Local Ollama

Install Ollama from https://ollama.com/download, then pull a model. For a 16 GB RAM machine, start with a small quantized model such as `llama3.2:3b`; actual performance depends on OS, CPU/GPU, and other applications.

```bash
ollama pull llama3.2:3b
```

Set the provider before starting FastAPI.

PowerShell:

```powershell
$env:KNOWBRIDGE_LLM_PROVIDER="ollama"
$env:KNOWBRIDGE_OLLAMA_ENABLED="true"
$env:OLLAMA_MODEL="llama3.2:3b"
python -m uvicorn app.main:app --reload
```

macOS/Linux:

```bash
export KNOWBRIDGE_LLM_PROVIDER=ollama
export KNOWBRIDGE_OLLAMA_ENABLED=true
export OLLAMA_MODEL=llama3.2:3b
python -m uvicorn app.main:app --reload
```

Ollama must be running locally. To switch back to hosted OpenAI, set `KNOWBRIDGE_LLM_PROVIDER=openai` and configure the key. With `auto`, OpenAI is selected when a key is configured; otherwise Ollama is selected only when explicitly enabled. Provider failures fall back to source excerpts.

## Optional AI engineering dependencies

Install only the group you are actively implementing. These are intentionally not included in the base requirements.

```bash
# LangChain, LangGraph, and LlamaIndex
python -m pip install -r requirements-orchestration.txt

# Qdrant client
python -m pip install -r requirements-vector.txt

# Langfuse observability
python -m pip install -r requirements-observability.txt

# RAGAS evaluation
python -m pip install -r requirements-evaluation.txt
```

Ollama runs as a separate application/service. vLLM and Hugging Face Transformers are not installed by default because their hardware and deployment requirements vary. Qdrant and Langfuse are configuration foundations only at this stage; `/api/integrations` reports readiness but does not imply that document vectors or traces are already being written.

## API endpoints

- `GET /` — welcome message
- `GET /health` — basic liveness check
- `GET /api/integrations` — optional integration readiness
- `GET /api/documents` — list uploaded documents
- `POST /api/documents` — upload PDF/TXT/Markdown
- `DELETE /api/documents/{id}` — delete a document
- `POST /api/ask` — retrieve relevant passages and optionally synthesize an answer

## Run tests

From `backend/` with the virtual environment activated:

```bash
python -m pytest -q
```

## Next milestones

1. Semantic embeddings and Qdrant vector retrieval behind a retrieval interface.
2. LlamaIndex ingestion and LangGraph workflow behind service boundaries.
3. Langfuse tracing and a RAGAS evaluation dataset.
4. Authentication and per-user document access control.
5. Background ingestion, CI, deployment, and production hardening.
