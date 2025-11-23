"""Protocol for embedding models."""

from typing import Protocol, List
import numpy as np


class EmbeddingModelProtocol(Protocol):
    """Interface for embedding models."""

    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts into embeddings.

        Args:
            texts: List of text strings to encode

        Returns:
            Array of embeddings with shape (len(texts), dimension)
        """
        ...

    def get_dimension(self) -> int:
        """Get the dimension of embeddings.

        Returns:
            Embedding dimension
        """
        ...
