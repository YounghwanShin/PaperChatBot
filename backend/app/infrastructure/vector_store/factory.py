"""Factory for creating vector store instances."""

from typing import Optional

from ...core.interfaces import VectorStoreProtocol
from .qdrant import QdrantVectorStore


def create_vector_store(
    host: str,
    port: int,
    embedding_dimension: int,
    api_key: Optional[str] = None
) -> VectorStoreProtocol:
    """Create a vector store instance.

    Args:
        host: Vector store host
        port: Vector store port
        embedding_dimension: Dimension of embedding vectors
        api_key: Optional API key for cloud services

    Returns:
        Vector store instance
    """
    return QdrantVectorStore(
        host=host,
        port=port,
        embedding_dimension=embedding_dimension,
        api_key=api_key
    )
