"""Protocol for vector store operations."""

from typing import Protocol, List, Dict, Any
import numpy as np


class VectorStoreProtocol(Protocol):
    """Interface for vector store operations."""

    def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        recreate: bool = False
    ) -> bool:
        """Create a new collection.

        Args:
            collection_name: Name of the collection
            vector_size: Size of the vector embeddings
            recreate: Whether to recreate if exists

        Returns:
            True if successful
        """
        ...

    def index_documents(
        self,
        collection_name: str,
        embeddings: np.ndarray,
        documents: List[Dict[str, Any]]
    ) -> bool:
        """Index documents into the vector store.

        Args:
            collection_name: Name of the collection
            embeddings: Document embeddings
            documents: Document data with metadata

        Returns:
            True if successful
        """
        ...

    def search(
        self,
        collection_name: str,
        query_embedding: np.ndarray,
        top_k: int = 5,
        score_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Search for similar documents.

        Args:
            collection_name: Name of the collection
            query_embedding: Query embedding vector
            top_k: Number of results to return
            score_threshold: Minimum similarity score

        Returns:
            List of search results with scores and metadata
        """
        ...

    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection.

        Args:
            collection_name: Name of the collection

        Returns:
            True if successful
        """
        ...

    def collection_exists(self, collection_name: str) -> bool:
        """Check if collection exists.

        Args:
            collection_name: Name of the collection

        Returns:
            True if collection exists
        """
        ...

    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get information about the collection.

        Args:
            collection_name: Name of the collection

        Returns:
            Collection metadata
        """
        ...

    def get_all_points(
        self,
        collection_name: str,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Get all points from a collection.

        Args:
            collection_name: Name of the collection
            limit: Maximum number of points to retrieve

        Returns:
            List of all points with their payloads
        """
        ...

    def health_check(self) -> bool:
        """Check if the vector store is accessible.

        Returns:
            True if healthy
        """
        ...
