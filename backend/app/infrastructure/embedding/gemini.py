"""Gemini-based embedding model implementation."""

from typing import List
import numpy as np
from google import genai
from google.genai import types

from ...core.exceptions import EmbeddingError


class GeminiEmbedding:
    """Gemini API-based embedding model."""

    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-embedding-001",
        dimension: int = 768
    ):
        """Initialize Gemini embedding model.

        Args:
            api_key: Google API key
            model_name: Gemini model name
            dimension: Embedding dimension
        """
        try:
            self.client = genai.Client(api_key=api_key)
            self.model_name = model_name
            self.dimension = dimension
        except Exception as e:
            raise EmbeddingError(f"Failed to initialize Gemini client: {e}")

    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts using Gemini API.

        Args:
            texts: List of texts to encode

        Returns:
            Array of embeddings

        Raises:
            EmbeddingError: If encoding fails
        """
        try:
            result = self.client.models.embed_content(
                model=self.model_name,
                contents=texts,
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT",
                    output_dimensionality=self.dimension
                )
            )
            embeddings = np.array([np.array(e.values) for e in result.embeddings])
            return embeddings
        except Exception as e:
            raise EmbeddingError(f"Failed to encode texts: {e}")

    def get_dimension(self) -> int:
        """Get embedding dimension.

        Returns:
            Embedding dimension
        """
        return self.dimension
