"""Protocol for PDF processing."""

from typing import Protocol, List, Dict, Any


class PDFProcessorProtocol(Protocol):
    """Interface for PDF processing operations."""

    def extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF file.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text
        """
        ...

    def extract_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """Extract metadata from PDF file.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Metadata dictionary
        """
        ...

    def chunk_text(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[Dict[str, Any]]:
        """Split text into chunks with overlap.

        Args:
            text: Text to chunk
            chunk_size: Size of each chunk in characters
            chunk_overlap: Overlap between chunks in characters

        Returns:
            List of chunks with metadata
        """
        ...
