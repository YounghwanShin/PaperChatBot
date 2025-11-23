"""Service for managing papers."""

from typing import List, Dict, Any, Tuple
import uuid
import os
from datetime import datetime

from ...core.interfaces import (
    EmbeddingModelProtocol,
    VectorStoreProtocol,
    PDFProcessorProtocol
)
from ...core.exceptions import PaperNotFoundError, PDFProcessingError, DuplicatePaperError


class PaperService:
    """Service for paper management operations."""

    def __init__(
        self,
        embedding_model: EmbeddingModelProtocol,
        vector_store: VectorStoreProtocol,
        pdf_processor: PDFProcessorProtocol,
        papers_collection: str,
        chunks_collection_prefix: str,
        upload_dir: str
    ):
        """Initialize paper service.

        Args:
            embedding_model: Model for generating embeddings
            vector_store: Vector store for retrieval
            pdf_processor: PDF processing utility
            papers_collection: Name of papers metadata collection
            chunks_collection_prefix: Prefix for paper chunks collections
            upload_dir: Directory for uploaded PDFs
        """
        self.embedding_model = embedding_model
        self.vector_store = vector_store
        self.pdf_processor = pdf_processor
        self.papers_collection = papers_collection
        self.chunks_collection_prefix = chunks_collection_prefix
        self.upload_dir = upload_dir

        # Ensure upload directory exists
        os.makedirs(upload_dir, exist_ok=True)

    def search_papers(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.6
    ) -> List[Dict[str, Any]]:
        """Search for papers using semantic search.

        Args:
            query: Search query
            top_k: Number of results to return
            score_threshold: Minimum similarity threshold

        Returns:
            List of matching papers with scores
        """
        # Encode query
        query_embedding = self.embedding_model.encode([query])[0]

        # Search in papers metadata collection
        results = self.vector_store.search(
            collection_name=self.papers_collection,
            query_embedding=query_embedding,
            top_k=top_k,
            score_threshold=score_threshold
        )

        return results

    def upload_paper(
        self,
        pdf_path: str,
        title: str,
        abstract: str,
        authors: str = "",
        year: int = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> Tuple[str, int]:
        """Upload and process a new paper.

        Args:
            pdf_path: Path to uploaded PDF file
            title: Paper title
            abstract: Paper abstract
            authors: Paper authors
            year: Publication year
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks

        Returns:
            Tuple of (paper_id, number of chunks created)

        Raises:
            PDFProcessingError: If PDF processing fails
            DuplicatePaperError: If paper with same title already exists
        """
        # Check for duplicate paper by title
        existing_papers = self.list_papers()
        for paper in existing_papers:
            if paper.get("title", "").strip().lower() == title.strip().lower():
                raise DuplicatePaperError(f"Paper with title '{title}' already exists")

        # Generate unique paper ID
        paper_id = str(uuid.uuid4())

        # Extract PDF metadata
        pdf_metadata = self.pdf_processor.extract_metadata(pdf_path)

        # Extract full text
        full_text = self.pdf_processor.extract_text(pdf_path)

        # Chunk the text
        chunks = self.pdf_processor.chunk_text(
            text=full_text,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        # Create paper metadata embedding (title + abstract)
        metadata_text = f"{title}\n\n{abstract}"
        metadata_embedding = self.embedding_model.encode([metadata_text])[0]

        # Store paper metadata
        paper_doc = {
            "id": paper_id,
            "paper_id": paper_id,
            "title": title,
            "authors": authors,
            "abstract": abstract,
            "year": year,
            "pdf_path": pdf_path,
            "page_count": pdf_metadata.get("page_count", 0),
            "created_at": datetime.now().isoformat()
        }

        self.vector_store.index_documents(
            collection_name=self.papers_collection,
            embeddings=metadata_embedding.reshape(1, -1),
            documents=[paper_doc]
        )

        # Create collection for paper chunks
        chunks_collection = f"{self.chunks_collection_prefix}_{paper_id}"
        self.vector_store.create_collection(
            collection_name=chunks_collection,
            vector_size=self.embedding_model.get_dimension()
        )

        # Encode and index chunks
        chunk_texts = [chunk["content"] for chunk in chunks]
        chunk_embeddings = self.embedding_model.encode(chunk_texts)

        chunk_docs = [
            {
                "id": str(uuid.uuid4()),
                "chunk_id": chunk["chunk_id"],
                "content": chunk["content"],
                "start_pos": chunk["start_pos"],
                "end_pos": chunk["end_pos"],
                "length": chunk["length"]
            }
            for chunk in chunks
        ]

        self.vector_store.index_documents(
            collection_name=chunks_collection,
            embeddings=chunk_embeddings,
            documents=chunk_docs
        )

        return paper_id, len(chunks)

    def get_paper(self, paper_id: str) -> Dict[str, Any]:
        """Get paper metadata by ID.

        Args:
            paper_id: Paper identifier

        Returns:
            Paper metadata

        Raises:
            PaperNotFoundError: If paper not found
        """
        # Get all papers and find the one with matching ID
        results = self.vector_store.get_all_points(
            collection_name=self.papers_collection,
            limit=1000
        )

        for result in results:
            if result.get("paper_id") == paper_id:
                return result

        raise PaperNotFoundError(f"Paper {paper_id} not found")

    def list_papers(self) -> List[Dict[str, Any]]:
        """List all papers.

        Returns:
            List of all paper metadata
        """
        # Get all papers using scroll
        results = self.vector_store.get_all_points(
            collection_name=self.papers_collection,
            limit=1000
        )

        return results

    def delete_paper(self, paper_id: str) -> bool:
        """Delete a paper and its chunks.

        Args:
            paper_id: Paper identifier

        Returns:
            True if successful

        Raises:
            PaperNotFoundError: If paper not found
        """
        # Verify paper exists
        self.get_paper(paper_id)

        # Delete chunks collection
        chunks_collection = f"{self.chunks_collection_prefix}_{paper_id}"
        self.vector_store.delete_collection(chunks_collection)

        # Note: We cannot easily delete a single point from Qdrant in this implementation
        # In production, you would implement point deletion by ID
        # For now, we'll just delete the chunks collection

        return True