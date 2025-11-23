"""Dependency injection container for the application."""

from functools import lru_cache

from ..core.config import settings
from ..core.interfaces import (
    EmbeddingModelProtocol,
    VectorStoreProtocol,
    LLMClientProtocol,
    PDFProcessorProtocol
)
from ..infrastructure.embedding import create_embedding_model
from ..infrastructure.vector_store import create_vector_store
from ..infrastructure.llm import create_llm_client
from ..infrastructure.pdf_processor import create_pdf_processor
from ..domain.services import PaperService, RAGService


@lru_cache()
def get_embedding_model() -> EmbeddingModelProtocol:
    """Get or create embedding model singleton.

    Returns:
        Embedding model instance
    """
    return create_embedding_model(
        api_key=settings.gemini_api_key,
        model_name=settings.embedding_model,
        dimension=settings.embedding_dimension
    )


@lru_cache()
def get_vector_store() -> VectorStoreProtocol:
    """Get or create vector store singleton.

    Returns:
        Vector store instance
    """
    return create_vector_store(
        host=settings.qdrant_host,
        port=settings.qdrant_port,
        embedding_dimension=settings.embedding_dimension,
        api_key=settings.qdrant_api_key
    )


@lru_cache()
def get_llm_client() -> LLMClientProtocol:
    """Get or create LLM client singleton.

    Returns:
        LLM client instance
    """
    return create_llm_client(
        api_key=settings.gemini_api_key,
        model_name=settings.llm_model,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens
    )


@lru_cache()
def get_pdf_processor() -> PDFProcessorProtocol:
    """Get or create PDF processor singleton.

    Returns:
        PDF processor instance
    """
    return create_pdf_processor()


@lru_cache()
def get_paper_service() -> PaperService:
    """Get or create paper service singleton.

    Returns:
        Paper service instance
    """
    embedding_model = get_embedding_model()
    vector_store = get_vector_store()
    pdf_processor = get_pdf_processor()

    return PaperService(
        embedding_model=embedding_model,
        vector_store=vector_store,
        pdf_processor=pdf_processor,
        papers_collection=settings.papers_collection,
        chunks_collection_prefix=settings.chunks_collection_prefix,
        upload_dir=settings.upload_dir
    )


@lru_cache()
def get_rag_service() -> RAGService:
    """Get or create RAG service singleton.

    Returns:
        RAG service instance
    """
    embedding_model = get_embedding_model()
    vector_store = get_vector_store()
    llm_client = get_llm_client()

    return RAGService(
        embedding_model=embedding_model,
        vector_store=vector_store,
        llm_client=llm_client,
        chunks_collection_prefix=settings.chunks_collection_prefix
    )
