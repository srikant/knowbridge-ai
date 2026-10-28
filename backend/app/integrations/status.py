"""Safe integration diagnostics; reports configuration, never secret values."""
from importlib.util import find_spec
from .. import config


def _installed(module: str) -> bool:
    try:
        return find_spec(module) is not None
    except (ImportError, ValueError, ModuleNotFoundError):
        return False


def integration_status() -> dict:
    provider = config.LLM_PROVIDER
    llm_selected = "none"
    if provider == "openai" and config.OPENAI_API_KEY:
        llm_selected = "openai"
    elif provider == "ollama" and config.OLLAMA_ENABLED:
        llm_selected = "ollama"
    elif provider == "auto":
        if config.OPENAI_API_KEY:
            llm_selected = "openai"
        elif config.OLLAMA_ENABLED:
            llm_selected = "ollama"

    return {
        "llm": {
            "configured_mode": provider,
            "selected_provider": llm_selected,
            "openai_configured": bool(config.OPENAI_API_KEY),
            "ollama_enabled": config.OLLAMA_ENABLED,
            "ollama_model": config.OLLAMA_MODEL if config.OLLAMA_ENABLED else None,
        },
        "vector_store": {
            "provider": "qdrant",
            "configured_url": config.QDRANT_URL,
            "client_installed": _installed("qdrant_client"),
            "enabled": _installed("qdrant_client"),
        },
        "orchestration": {
            "langchain_installed": _installed("langchain"),
            "langgraph_installed": _installed("langgraph"),
            "llama_index_installed": _installed("llama_index"),
        },
        "observability": {
            "langfuse_configured": bool(config.LANGFUSE_PUBLIC_KEY and config.LANGFUSE_SECRET_KEY),
            "langfuse_installed": _installed("langfuse"),
        },
        "evaluation": {
            "ragas_installed": _installed("ragas"),
        },
    }
