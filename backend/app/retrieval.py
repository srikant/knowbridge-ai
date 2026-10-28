import re
from collections import Counter
from .database import connection

STOP_WORDS = {"the", "and", "for", "are", "was", "were", "with", "that", "this", "from", "you", "your", "what", "how", "when", "where", "why", "can", "could", "would", "should", "about", "into", "have", "has", "had", "does", "did", "not", "but", "our", "their", "they", "them", "its", "a", "an", "to", "of", "in", "on", "is", "it", "as", "at", "be", "or", "by"}


def tokenize(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", text.lower()) if w not in STOP_WORDS and len(w) > 1]


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> list[str]:
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return []
    chunks = []
    start = 0
    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        if end < len(normalized):
            boundary = normalized.rfind(" ", start + chunk_size // 2, end)
            if boundary > start:
                end = boundary
        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(normalized):
            break
        start = max(end - overlap, start + 1)
    return chunks


def search_chunks(question: str, limit: int = 5) -> list[dict]:
    q_terms = Counter(tokenize(question))
    if not q_terms:
        return []
    with connection() as conn:
        rows = conn.execute("""SELECT c.id, c.document_id, c.chunk_index, c.content, d.filename
            FROM chunks c JOIN documents d ON d.id = c.document_id""").fetchall()
    scored = []
    for row in rows:
        terms = Counter(tokenize(row["content"]))
        overlap = sum(min(count, terms.get(term, 0)) for term, count in q_terms.items())
        coverage = overlap / max(sum(q_terms.values()), 1)
        density = overlap / max(len(terms) ** 0.5, 1)
        score = coverage * 0.7 + min(density / 10, 0.3)
        if score > 0:
            scored.append({**dict(row), "score": round(score, 4)})
    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:limit]
