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
    rewritten_query: Optional[str] = Field(
        default=None,
        description="Query rewritten for better retrieval (if query rewrite is enabled)"
    )


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


class ArxivPaperResult(BaseModel):
    """Result for a single fetched paper from arXiv."""
    paper_id: str = Field(..., description="Generated paper ID")
    arxiv_id: str = Field(..., description="arXiv paper ID")
    title: str = Field(..., description="Paper title")
    chunks_created: int = Field(..., description="Number of chunks created")


class ArxivFetchError(BaseModel):
    """Error information for failed paper processing."""
    arxiv_id: str = Field(default="", description="arXiv paper ID")
    title: str = Field(default="", description="Paper title")
    error: str = Field(..., description="Error message")


class ArxivFetchResponse(BaseModel):
    """Response model for arXiv recent fetch."""
    total_found: int = Field(..., description="Total papers found in search")
    successfully_processed: int = Field(..., description="Successfully processed papers")
    skipped_duplicates: int = Field(..., description="Skipped duplicate papers")
    failed: int = Field(..., description="Failed to process papers")
    papers: List[ArxivPaperResult] = Field(default=[], description="Successfully processed papers")
    errors: List[ArxivFetchError] = Field(default=[], description="Processing errors")


class ArxivFetchTaskStart(BaseModel):
    """Response when arXiv fetch task is started."""
    task_id: str = Field(..., description="Unique task identifier")
    message: str = Field(..., description="Status message")
    status: str = Field(default="started", description="Task status")


class ArxivFetchTaskStatus(BaseModel):
    """Status response for arXiv fetch task."""
    task_id: str = Field(..., description="Task identifier")
    status: str = Field(..., description="Task status: 'processing', 'completed', 'failed'")
    progress: Optional[str] = Field(default=None, description="Progress message")
    result: Optional[ArxivFetchResponse] = Field(default=None, description="Final result if completed")
    error: Optional[str] = Field(default=None, description="Error message if failed")
