from pydantic import BaseModel, Field


class DocumentOut(BaseModel):
    id: int
    filename: str
    content_type: str
    characters: int
    chunks: int
    created_at: str


class Source(BaseModel):
    document_id: int
    filename: str
    chunk_index: int
    excerpt: str
    relevance: float


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]
    mode: str
