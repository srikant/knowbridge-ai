"""Environment-backed configuration for KnowBridge AI.

Optional integrations are disabled unless explicitly configured. This keeps the
base install lightweight and lets the app boot without external AI services.
"""
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("KNOWBRIDGE_DATA_DIR", BASE_DIR / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "knowbridge.db"
MAX_UPLOAD_BYTES = int(os.getenv("KNOWBRIDGE_MAX_UPLOAD_BYTES", 10 * 1024 * 1024))

# LLM provider: auto, openai, ollama, or none. `auto` prefers hosted OpenAI
# when a key exists, then uses Ollama only when KNOWBRIDGE_OLLAMA_ENABLED=true.
LLM_PROVIDER = os.getenv("KNOWBRIDGE_LLM_PROVIDER", "auto").strip().lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip()
OLLAMA_ENABLED = os.getenv("KNOWBRIDGE_OLLAMA_ENABLED", "false").lower() in {"1", "true", "yes", "on"}
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b").strip()

# Optional integrations: configuration only; packages are installed separately.
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333").rstrip("/")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "").strip()
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "").strip()
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "").strip()
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com").rstrip("/")
