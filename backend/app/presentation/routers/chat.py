"""Chat API router for paper-based Q&A."""

from fastapi import APIRouter, HTTPException, Depends

from ...domain.models import ChatRequest, ChatResponse, RetrievedChunk
from ...domain.services import RAGService
from ...application.dependencies import get_rag_service
from ...core.config import settings

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/{paper_id}", response_model=ChatResponse)
async def chat_with_paper(
    paper_id: str,
    request: ChatRequest,
    rag_service: RAGService = Depends(get_rag_service)
) -> ChatResponse:
    """Chat with a specific paper using RAG.

    Args:
        paper_id: Paper identifier
        request: Chat request with message and history
        rag_service: RAG service dependency

    Returns:
        Chat response with answer and retrieved chunks

    Raises:
        HTTPException: If chat processing fails
    """
    try:
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.conversation_history
        ]

        result = rag_service.chat(
            paper_id=paper_id,
            query=request.message,
            conversation_history=conversation_history,
            top_k=settings.chunk_top_k,
            score_threshold=settings.chunk_threshold
        )

        retrieved_chunks = [
            RetrievedChunk(
                content=chunk["content"],
                score=chunk["score"],
                chunk_id=chunk["chunk_id"]
            )
            for chunk in result["retrieved_chunks"]
        ]

        response = ChatResponse(
            answer=result["answer"],
            retrieved_chunks=retrieved_chunks,
            confidence=result["confidence"]
        )

        return response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )
