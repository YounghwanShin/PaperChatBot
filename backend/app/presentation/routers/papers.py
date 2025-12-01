"""Papers API router for search, upload, and management."""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from typing import Optional
import os
import uuid
import shutil
import logging

from ...domain.models import (
    PaperSearchRequest,
    PaperSearchResponse,
    PaperSearchResult,
    PaperUploadResponse,
    PaperListResponse,
    PaperMetadata,
    ArxivFetchResponse,
    ArxivPaperResult,
    ArxivFetchError,
    ArxivFetchTaskStart,
    ArxivFetchTaskStatus
)
from ...domain.services import PaperService, ArxivService
from ...application.dependencies import get_paper_service, get_arxiv_service
from ...core.config import settings
from ...core.exceptions import PaperNotFoundError, InvalidFileError, DuplicatePaperError
from ...infrastructure.task_store import task_store

router = APIRouter(prefix="/papers", tags=["papers"])
logger = logging.getLogger(__name__)


@router.post("/search", response_model=PaperSearchResponse)
async def search_papers(
    request: PaperSearchRequest,
    paper_service: PaperService = Depends(get_paper_service)
) -> PaperSearchResponse:
    """Search for papers using semantic search.

    Args:
        request: Search request with query and parameters
        paper_service: Paper service dependency

    Returns:
        Search results with matching papers

    Raises:
        HTTPException: If search fails
    """
    try:
        results = paper_service.search_papers(
            query=request.query,
            top_k=request.top_k,
            score_threshold=request.score_threshold
        )

        search_results = [
            PaperSearchResult(
                paper_id=result["paper_id"],
                title=result["title"],
                authors=result.get("authors", ""),
                abstract=result.get("abstract", ""),
                score=result["score"],
                year=result.get("year")
            )
            for result in results
        ]

        return PaperSearchResponse(
            results=search_results,
            total=len(search_results)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching papers: {str(e)}"
        )


@router.post("/upload", response_model=PaperUploadResponse)
async def upload_paper(
    file: UploadFile = File(...),
    title: str = Form(...),
    abstract: str = Form(...),
    authors: str = Form(""),
    year: Optional[int] = Form(None),
    paper_service: PaperService = Depends(get_paper_service)
) -> PaperUploadResponse:
    """Upload a new paper PDF.

    Args:
        file: PDF file to upload
        title: Paper title
        abstract: Paper abstract
        authors: Paper authors
        year: Publication year
        paper_service: Paper service dependency

    Returns:
        Upload response with paper ID and status

    Raises:
        HTTPException: If upload or processing fails
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise InvalidFileError("Only PDF files are allowed")

        # Validate file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset

        if file_size > settings.max_upload_size:
            raise InvalidFileError(
                f"File size exceeds maximum allowed size of {settings.max_upload_size} bytes"
            )

        # Save uploaded file
        file_id = str(uuid.uuid4())
        file_path = os.path.join(settings.upload_dir, f"{file_id}.pdf")

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process paper
        paper_id, chunks_count = paper_service.upload_paper(
            pdf_path=file_path,
            title=title,
            abstract=abstract,
            authors=authors,
            year=year,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )

        return PaperUploadResponse(
            paper_id=paper_id,
            title=title,
            message="Paper uploaded and processed successfully",
            chunks_created=chunks_count
        )

    except InvalidFileError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DuplicatePaperError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading paper: {str(e)}"
        )


@router.get("/", response_model=PaperListResponse)
async def list_papers(
    paper_service: PaperService = Depends(get_paper_service)
) -> PaperListResponse:
    """List all papers.

    Args:
        paper_service: Paper service dependency

    Returns:
        List of all papers

    Raises:
        HTTPException: If listing fails
    """
    try:
        papers = paper_service.list_papers()

        paper_list = [
            PaperMetadata(
                paper_id=paper["paper_id"],
                title=paper["title"],
                authors=paper.get("authors", ""),
                abstract=paper.get("abstract", ""),
                year=paper.get("year"),
                pdf_path=paper["pdf_path"],
                page_count=paper.get("page_count", 0),
                created_at=paper.get("created_at")
            )
            for paper in papers
        ]

        return PaperListResponse(
            papers=paper_list,
            total=len(paper_list)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing papers: {str(e)}"
        )


@router.get("/{paper_id}", response_model=PaperMetadata)
async def get_paper(
    paper_id: str,
    paper_service: PaperService = Depends(get_paper_service)
) -> PaperMetadata:
    """Get paper details by ID.

    Args:
        paper_id: Paper identifier
        paper_service: Paper service dependency

    Returns:
        Paper metadata

    Raises:
        HTTPException: If paper not found or retrieval fails
    """
    try:
        paper = paper_service.get_paper(paper_id)

        return PaperMetadata(
            paper_id=paper["paper_id"],
            title=paper["title"],
            authors=paper.get("authors", ""),
            abstract=paper.get("abstract", ""),
            year=paper.get("year"),
            pdf_path=paper["pdf_path"],
            page_count=paper.get("page_count", 0),
            created_at=paper.get("created_at")
        )

    except PaperNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving paper: {str(e)}"
        )


@router.delete("/{paper_id}")
async def delete_paper(
    paper_id: str,
    paper_service: PaperService = Depends(get_paper_service)
):
    """Delete a paper.

    Args:
        paper_id: Paper identifier
        paper_service: Paper service dependency

    Returns:
        Success message

    Raises:
        HTTPException: If paper not found or deletion fails
    """
    try:
        paper_service.delete_paper(paper_id)

        return {"message": f"Paper {paper_id} deleted successfully"}

    except PaperNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting paper: {str(e)}"
        )


def _background_arxiv_fetch(
    task_id: str,
    days_ago: int,
    arxiv_service: ArxivService
):
    """Background task for fetching and processing arXiv papers.

    Args:
        task_id: Task identifier
        days_ago: Number of days to look back
        arxiv_service: arXiv service instance
    """
    try:
        logger.info(f"Starting background arXiv fetch task {task_id}")
        task_store.update_progress(task_id, f"Searching arXiv for papers from last {days_ago} days...")

        # Fetch and process papers
        results = arxiv_service.fetch_and_process_papers(
            days_ago=days_ago,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )

        logger.info(f"Task {task_id} completed: {results['successfully_processed']} papers processed")
        task_store.set_completed(task_id, results)

    except Exception as e:
        logger.error(f"Task {task_id} failed: {str(e)}")
        task_store.set_failed(task_id, str(e))


@router.post("/fetch-recent", response_model=ArxivFetchTaskStart, status_code=202)
async def fetch_recent_papers(
    background_tasks: BackgroundTasks,
    days_ago: int = 7,
    arxiv_service: ArxivService = Depends(get_arxiv_service)
) -> ArxivFetchTaskStart:
    """Start background task to fetch and process recent NLP papers from arXiv.

    Args:
        background_tasks: FastAPI background tasks
        days_ago: Number of days to look back (default: 7)
        arxiv_service: arXiv service dependency

    Returns:
        Task start response with task ID for status polling

    Raises:
        HTTPException: If task creation fails
    """
    try:
        # Create task
        task_id = task_store.create_task()

        # Add background task
        background_tasks.add_task(
            _background_arxiv_fetch,
            task_id=task_id,
            days_ago=days_ago,
            arxiv_service=arxiv_service
        )

        logger.info(f"Created arXiv fetch task {task_id}")

        return ArxivFetchTaskStart(
            task_id=task_id,
            message=f"Started fetching papers from arXiv (last {days_ago} days). Use /papers/fetch-status/{task_id} to check progress.",
            status="started"
        )

    except Exception as e:
        logger.error(f"Failed to start arXiv fetch task: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error starting fetch task: {str(e)}"
        )


@router.get("/fetch-status/{task_id}", response_model=ArxivFetchTaskStatus)
async def get_fetch_status(task_id: str) -> ArxivFetchTaskStatus:
    """Get status of an arXiv fetch task.

    Args:
        task_id: Task identifier

    Returns:
        Task status with progress or result

    Raises:
        HTTPException: If task not found
    """
    status = task_store.get_status(task_id)

    if status is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    # Convert result to response model if completed
    result_response = None
    if status["status"] == "completed" and status["result"]:
        results = status["result"]
        papers = [ArxivPaperResult(**paper) for paper in results["papers"]]
        errors = [ArxivFetchError(**error) for error in results["errors"]]

        result_response = ArxivFetchResponse(
            total_found=results["total_found"],
            successfully_processed=results["successfully_processed"],
            skipped_duplicates=results["skipped_duplicates"],
            failed=results["failed"],
            papers=papers,
            errors=errors
        )

    return ArxivFetchTaskStatus(
        task_id=task_id,
        status=status["status"],
        progress=status.get("progress"),
        result=result_response,
        error=status.get("error")
    )
