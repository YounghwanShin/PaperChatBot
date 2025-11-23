"""Papers API router for search, upload, and management."""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import Optional
import os
import uuid
import shutil

from ...domain.models import (
    PaperSearchRequest,
    PaperSearchResponse,
    PaperSearchResult,
    PaperUploadResponse,
    PaperListResponse,
    PaperMetadata
)
from ...domain.services import PaperService
from ...application.dependencies import get_paper_service
from ...core.config import settings
from ...core.exceptions import PaperNotFoundError, InvalidFileError, DuplicatePaperError

router = APIRouter(prefix="/papers", tags=["papers"])


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
