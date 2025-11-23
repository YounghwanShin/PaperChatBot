"""Vector store implementation using Qdrant."""

from typing import List, Optional, Dict, Any
import logging
import numpy as np
import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from ...core.exceptions import VectorStoreError

logger = logging.getLogger(__name__)


class QdrantVectorStore:
    """Qdrant vector store implementation."""

    def __init__(
        self,
        host: str,
        port: int,
        embedding_dimension: int,
        api_key: Optional[str] = None
    ):
        """Initialize Qdrant vector store.

        Args:
            host: Qdrant server host
            port: Qdrant server port
            embedding_dimension: Dimension of embedding vectors
            api_key: Optional API key for Qdrant Cloud
        """
        self.embedding_dimension = embedding_dimension

        # Remove port from host if it's already included
        if ":" in host:
            host = host.split(":")[0]

        try:
            if api_key:
                self.client = QdrantClient(url=f"https://{host}:{port}", api_key=api_key)
            else:
                self.client = QdrantClient(host=host, port=port)
            logger.info(f"Qdrant client initialized: {host}:{port}")
        except Exception as e:
            logger.error(f"Error initializing Qdrant client: {e}")
            raise VectorStoreError(f"Failed to initialize Qdrant: {e}")

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
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]

            if collection_name in collection_names:
                if recreate:
                    logger.info(f"Deleting existing collection: {collection_name}")
                    self.client.delete_collection(collection_name=collection_name)
                else:
                    logger.info(f"Collection already exists: {collection_name}")
                    return True

            logger.info(f"Creating collection: {collection_name}")
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Collection created: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise VectorStoreError(f"Failed to create collection: {e}")

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
        try:
            if len(embeddings) != len(documents):
                raise VectorStoreError("Mismatch between embeddings and documents count")

            points = []
            for i, (embedding, doc) in enumerate(zip(embeddings, documents)):
                point = PointStruct(
                    id=doc.get("id", str(uuid.uuid4())),
                    vector=embedding.tolist() if isinstance(embedding, np.ndarray) else embedding,
                    payload=doc
                )
                points.append(point)

            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            logger.info(f"Indexed {len(points)} documents to {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error indexing documents: {e}")
            raise VectorStoreError(f"Failed to index documents: {e}")

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
        try:
            query_vector = query_embedding.tolist() if isinstance(query_embedding, np.ndarray) else query_embedding

            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=top_k,
                score_threshold=score_threshold
            )

            results = []
            for scored_point in search_result:
                result = {
                    "id": scored_point.id,
                    "score": scored_point.score,
                    **scored_point.payload
                }
                results.append(result)

            logger.info(f"Found {len(results)} similar documents in {collection_name}")
            return results
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []

    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection.

        Args:
            collection_name: Name of the collection

        Returns:
            True if successful
        """
        try:
            self.client.delete_collection(collection_name=collection_name)
            logger.info(f"Deleted collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            return False

    def collection_exists(self, collection_name: str) -> bool:
        """Check if collection exists.

        Args:
            collection_name: Name of the collection

        Returns:
            True if collection exists
        """
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            return collection_name in collection_names
        except Exception as e:
            logger.error(f"Error checking collection existence: {e}")
            return False

    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get information about the collection.

        Args:
            collection_name: Name of the collection

        Returns:
            Collection metadata
        """
        try:
            info = self.client.get_collection(collection_name=collection_name)
            return {
                "name": collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": str(info.status)
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {}

    def health_check(self) -> bool:
        """Check if the vector store is accessible.

        Returns:
            True if healthy
        """
        try:
            self.client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
