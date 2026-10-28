
# KnowBridge AI

An AI-powered business knowledge assistant that helps
users ask questions about their documents and receive
answers grounded in source material.

## Current Status

Day 1: FastAPI project foundation and health endpoint.

## Technology Stack

- Python
- FastAPI
- Uvicorn
- React and TypeScript (planned)
- LLM and RAG capabilities (planned)

## Run Locally

From the backend directory, activate your virtual
environment and install dependencies:

    python -m pip install -r requirements.txt

Start the API:

    python -m uvicorn app.main:app --reload

## API Endpoints

- GET / — Welcome message
- GET /health — Basic application health check
- GET /docs — Interactive API documentation

## Roadmap

1. Document upload and text extraction
2. Embeddings and semantic retrieval
3. Grounded answers with source citations
4. React frontend
5. Evaluation, security and deployment
