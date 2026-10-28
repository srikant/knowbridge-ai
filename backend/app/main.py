from contextlib import asynccontextmanager
from datetime import datetime, timezone
from io import BytesIO
import logging
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader

from .config import MAX_UPLOAD_BYTES
from .integrations.status import integration_status
from .services.llm import generate_answer
from .database import connection, init_db
from .retrieval import chunk_text, search_chunks
from .schemas import AskRequest, AskResponse, DocumentOut, Source

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("knowbridge")
ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf"}


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="KnowBridge AI API",
    description="An AI-powered business knowledge assistant for your documents.",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


def extract_text(filename: str, raw: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix in {".txt", ".md"}:
        try:
            return raw.decode("utf-8-sig").strip()
        except UnicodeDecodeError as exc:
            raise HTTPException(status_code=400, detail="Text files must use UTF-8 encoding.") from exc
    if suffix == ".pdf":
        try:
            reader = PdfReader(BytesIO(raw))
            return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
        except Exception as exc:
            logger.exception("PDF extraction failed")
            raise HTTPException(status_code=400, detail="Could not read this PDF. Please check that it is a valid, text-based PDF.") from exc
    raise HTTPException(status_code=415, detail="Unsupported file type. Upload a PDF, TXT, or Markdown file.")


@app.get("/")
def root():
    return {"message": "Welcome to KnowBridge AI", "docs": "/docs"}


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "knowbridge-ai-api", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/api/integrations", tags=["System"] )
def get_integrations():
    """Report optional integration readiness without exposing credentials."""
    return integration_status()


@app.get("/api/documents", response_model=list[DocumentOut], tags=["Documents"])
def list_documents():
    with connection() as conn:
        rows = conn.execute("""SELECT d.id, d.filename, d.content_type, length(d.content) AS characters,
            (SELECT COUNT(*) FROM chunks c WHERE c.document_id = d.id) AS chunks, d.created_at
            FROM documents d ORDER BY d.id DESC""").fetchall()
    return [dict(row) for row in rows]


@app.post("/api/documents", response_model=DocumentOut, status_code=201, tags=["Documents"])
async def upload_document(file: UploadFile = File(...)):
    filename = Path(file.filename or "").name
    if not filename:
        raise HTTPException(status_code=400, detail="A filename is required.")
    if Path(filename).suffix.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Unsupported file type. Upload a PDF, TXT, or Markdown file.")
    raw = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail=f"File exceeds the {MAX_UPLOAD_BYTES // (1024 * 1024)} MB upload limit.")
    if not raw:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    content = extract_text(filename, raw)
    if not content:
        raise HTTPException(status_code=422, detail="No readable text was found in this file. Scanned PDFs need OCR, which is not included yet.")
    chunks = chunk_text(content)
    with connection() as conn:
        cursor = conn.execute("INSERT INTO documents (filename, content_type, content) VALUES (?, ?, ?)", (filename, file.content_type or "application/octet-stream", content))
        document_id = cursor.lastrowid
        conn.executemany("INSERT INTO chunks (document_id, chunk_index, content) VALUES (?, ?, ?)", [(document_id, i, chunk) for i, chunk in enumerate(chunks)])
        row = conn.execute("""SELECT d.id, d.filename, d.content_type, length(d.content) AS characters,
            (SELECT COUNT(*) FROM chunks c WHERE c.document_id = d.id) AS chunks, d.created_at
            FROM documents d WHERE d.id = ?""", (document_id,)).fetchone()
    logger.info("Stored document id=%s filename=%s chunks=%s", document_id, filename, len(chunks))
    return dict(row)


@app.delete("/api/documents/{document_id}", status_code=204, tags=["Documents"])
def delete_document(document_id: int):
    with connection() as conn:
        exists = conn.execute("SELECT id FROM documents WHERE id = ?", (document_id,)).fetchone()
        if exists is None:
            raise HTTPException(status_code=404, detail="Document not found.")
        conn.execute("DELETE FROM chunks WHERE document_id = ?", (document_id,))
        conn.execute("DELETE FROM documents WHERE id = ?", (document_id,))
    return None


@app.post("/api/ask", response_model=AskResponse, tags=["Knowledge Assistant"])
def ask_documents(request: AskRequest):
    matches = search_chunks(request.question)
    if not matches:
        return AskResponse(answer="I couldn't find relevant information in your uploaded documents. Try rephrasing your question or upload a document that covers this topic.", sources=[], mode="retrieval-only")
    sources = [Source(document_id=m["document_id"], filename=m["filename"], chunk_index=m["chunk_index"], excerpt=m["content"][:360] + ("…" if len(m["content"]) > 360 else ""), relevance=m["score"]) for m in matches]
    answer, mode = generate_answer(request.question, matches)
    if answer is not None:
        return AskResponse(answer=answer, sources=sources, mode=mode)
    answer = "I found the following potentially relevant passages. Configure KNOWBRIDGE_LLM_PROVIDER with a hosted or local model to enable synthesized answers; for now, review these source excerpts directly.\n\n" + "\n\n".join(f"**{m['filename']} (chunk {m['chunk_index'] + 1})**\n{m['content'][:700]}" for m in matches[:3])
    return AskResponse(answer=answer, sources=sources, mode="retrieval-only")
