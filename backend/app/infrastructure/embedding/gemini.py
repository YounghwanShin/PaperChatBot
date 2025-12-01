"""Gemini-based embedding model implementation."""

from typing import List
import numpy as np
import time
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

    def encode(
        self,
        texts: List[str],
        task_type: str = "RETRIEVAL_DOCUMENT"
    ) -> np.ndarray:
        """Encode texts using Gemini API with batching.

        Args:
            texts: List of texts to encode
            task_type: Embedding task type.
                      "RETRIEVAL_DOCUMENT" for indexing documents,
                      "RETRIEVAL_QUERY" for search queries

        Returns:
            Array of embeddings

        Raises:
            EmbeddingError: If encoding fails
        """
        try:
            # Gemini API limit: max 100 texts per batch
            batch_size = 100
            all_embeddings = []

            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]

                # Add delay between batches to avoid rate limiting (except first batch)
                if i > 0:
                    time.sleep(1.0)  # 1 second between batches (유료 티어)

                # Retry logic for transient errors
                max_retries = 3
                for retry in range(max_retries):
                    try:
                        result = self.client.models.embed_content(
                            model=self.model_name,
                            contents=batch,
                            config=types.EmbedContentConfig(
                                task_type=task_type,
                                output_dimensionality=self.dimension
                            )
                        )

                        batch_embeddings = [np.array(e.values) for e in result.embeddings]
                        all_embeddings.extend(batch_embeddings)
                        break  # Success, exit retry loop

                    except Exception as e:
                        error_msg = str(e)
                        if retry < max_retries - 1 and ("RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg):
                            # Transient error, wait and retry
                            wait_time = 2 ** retry  # 1, 2, 4 seconds
                            time.sleep(wait_time)
                        else:
                            # Final retry or non-retryable error
                            raise e

            return np.array(all_embeddings)
        except Exception as e:
            raise EmbeddingError(f"Failed to encode texts: {e}")

    def get_dimension(self) -> int:
        """Get embedding dimension.

        Returns:
            Embedding dimension
        """
        return self.dimension
