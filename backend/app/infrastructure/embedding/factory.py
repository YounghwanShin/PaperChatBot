"""Factory for creating embedding models."""

from ...core.interfaces import EmbeddingModelProtocol
from .gemini import GeminiEmbedding


def create_embedding_model(
    api_key: str,
    model_name: str = "gemini-embedding-001",
    dimension: int = 768
) -> EmbeddingModelProtocol:
    """Create an embedding model instance.

    Args:
        api_key: API key for the embedding service
        model_name: Model name
        dimension: Embedding dimension

    Returns:
        Embedding model instance
    """
    return GeminiEmbedding(
        api_key=api_key,
        model_name=model_name,
        dimension=dimension
    )
