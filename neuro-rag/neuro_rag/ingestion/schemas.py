"""
PASHA-NEURO-RAG Ingestion Schemas
Author: Mohammad Subhan Pasha
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import uuid
import time


class DocumentMetadata(BaseModel):
    source_type: str = Field(description="pdf, docx, url, notion, text")
    source_name: str = Field(description="Filename or URL title")
    uri: Optional[str] = None
    author: Optional[str] = "Mohammad Subhan Pasha"
    created_at: float = Field(default_factory=time.time)
    extra: Dict[str, Any] = Field(default_factory=dict)


class Document(BaseModel):
    doc_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    metadata: DocumentMetadata


class ChunkMetadata(BaseModel):
    doc_id: str
    chunk_index: int
    source_type: str
    source_name: str
    uri: Optional[str] = None
    start_char: int = 0
    end_char: int = 0
    token_count: int = 0
    semantic_score: Optional[float] = 1.0


class Chunk(BaseModel):
    chunk_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    metadata: ChunkMetadata
    embedding: Optional[List[float]] = None


class IngestionRequest(BaseModel):
    source_type: str  # pdf, docx, url, notion
    file_path: Optional[str] = None
    url: Optional[str] = None
    notion_token: Optional[str] = None
    notion_page_id: Optional[str] = None


class IngestionResponse(BaseModel):
    status: str
    doc_id: str
    source_name: str
    chunk_count: int
    total_tokens: int
    message: str
