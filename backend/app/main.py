
from fastapi import FastAPI
from datetime import datetime, timezone

app = FastAPI(
    title="KnowBridge AI API",
    description="AI-powered business document assistant",
    version="0.1.0",
)


@app.get("/health", tags=["Health"])
async def health_check():
    """Return the basic health status of the API."""
    return {
        "status": "healthy",
        "service": "knowbridge-ai-api",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/", tags=["General"])
async def root():
    """Return a welcome message."""
    return {
        "message": "Welcome to KnowBridge AI",
        "docs": "/docs",
    }
