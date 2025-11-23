"""PDF processing implementation using PyMuPDF."""

from typing import List, Dict, Any
import fitz  # PyMuPDF
import re

from ...core.exceptions import PDFProcessingError


class PDFProcessor:
    """PDF processor using PyMuPDF."""

    def __init__(self):
        """Initialize PDF processor."""
        pass

    def extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF file.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text

        Raises:
            PDFProcessingError: If extraction fails
        """
        try:
            doc = fitz.open(pdf_path)
            text_parts = []

            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                text_parts.append(text)

            doc.close()

            full_text = "\n\n".join(text_parts)
            # Clean up excessive whitespace
            full_text = re.sub(r'\n{3,}', '\n\n', full_text)
            full_text = re.sub(r' {2,}', ' ', full_text)

            return full_text.strip()

        except Exception as e:
            raise PDFProcessingError(f"Failed to extract text from PDF: {e}")

    def extract_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """Extract metadata from PDF file.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Metadata dictionary

        Raises:
            PDFProcessingError: If extraction fails
        """
        try:
            doc = fitz.open(pdf_path)
            metadata = doc.metadata

            result = {
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "subject": metadata.get("subject", ""),
                "keywords": metadata.get("keywords", ""),
                "creator": metadata.get("creator", ""),
                "producer": metadata.get("producer", ""),
                "page_count": len(doc)
            }

            doc.close()
            return result

        except Exception as e:
            raise PDFProcessingError(f"Failed to extract metadata from PDF: {e}")

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> List[Dict[str, Any]]:
        """Split text into chunks with overlap.

        Args:
            text: Text to chunk
            chunk_size: Size of each chunk in characters
            chunk_overlap: Overlap between chunks in characters

        Returns:
            List of chunks with metadata

        Raises:
            PDFProcessingError: If chunking fails
        """
        try:
            if chunk_overlap >= chunk_size:
                raise PDFProcessingError("Chunk overlap must be less than chunk size")

            chunks = []
            start = 0
            chunk_id = 0

            while start < len(text):
                end = start + chunk_size

                # Try to find a good break point (sentence end)
                if end < len(text):
                    # Look for sentence endings
                    next_period = text.find('.', end - 100, end + 100)
                    next_newline = text.find('\n', end - 100, end + 100)

                    # Use the closest sentence boundary
                    boundaries = [b for b in [next_period, next_newline] if b != -1]
                    if boundaries:
                        end = min(boundaries) + 1

                chunk_text = text[start:end].strip()

                if chunk_text:
                    chunks.append({
                        "chunk_id": chunk_id,
                        "content": chunk_text,
                        "start_pos": start,
                        "end_pos": end,
                        "length": len(chunk_text)
                    })
                    chunk_id += 1

                # Move to next chunk with overlap
                start = end - chunk_overlap

            return chunks

        except Exception as e:
            raise PDFProcessingError(f"Failed to chunk text: {e}")
