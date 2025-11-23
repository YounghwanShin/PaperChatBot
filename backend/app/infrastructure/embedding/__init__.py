"""Embedding infrastructure module."""

from .gemini import GeminiEmbedding
from .factory import create_embedding_model

__all__ = ["GeminiEmbedding", "create_embedding_model"]
