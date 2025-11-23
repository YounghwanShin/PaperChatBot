"""Pydantic models for request/response validation."""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class PaperMetadata(BaseModel):
    """Paper metadata model."""
    paper_id: str = Field(..., description="Unique paper identifier")
    title: str = Field(..., description="Paper title")
    authors: str = Field(default="", description="Paper authors")
    abstract: str = Field(..., description="Paper abstract")
    year: Optional[int] = Field(default=None, description="Publication year")
    pdf_path: str = Field(..., description="Path to PDF file")
    page_count: int = Field(default=0, description="Number of pages")
    created_at: datetime = Field(default_factory=datetime.now, description="Upload timestamp")


class PaperSearchRequest(BaseModel):
    """Request model for paper search."""
    query: str = Field(..., min_length=1, description="Search query")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results")
    score_threshold: float = Field(default=0.6, ge=0.0, le=1.0, description="Minimum similarity score")


class PaperSearchResult(BaseModel):
    """Search result for a paper."""
    paper_id: str
    title: str
    authors: str
    abstract: str
    score: float
    year: Optional[int] = None


class PaperSearchResponse(BaseModel):
    """Response model for paper search."""
    results: List[PaperSearchResult]
    total: int


class PaperUploadResponse(BaseModel):
    """Response model for paper upload."""
    paper_id: str
    title: str
    message: str
    chunks_created: int


class ChatMessage(BaseModel):
    """Single chat message."""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., min_length=1, description="User's question")
    conversation_history: List[ChatMessage] = Field(
        default=[],
        description="Previous conversation history"
    )


class RetrievedChunk(BaseModel):
    """Retrieved chunk with metadata."""
    content: str = Field(..., description="Chunk content")
    score: float = Field(..., description="Similarity score")
    chunk_id: int = Field(..., description="Chunk identifier")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    answer: str = Field(..., description="Generated answer")
    retrieved_chunks: List[RetrievedChunk] = Field(
        default=[],
        description="Retrieved chunks used"
    )
    confidence: float = Field(..., description="Response confidence score")


class PaperListResponse(BaseModel):
    """Response model for listing papers."""
    papers: List[PaperMetadata]
    total: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    qdrant_connected: bool
    papers_collection_exists: bool


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None
