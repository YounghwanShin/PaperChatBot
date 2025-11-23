"""PDF processor infrastructure module."""

from .processor import PDFProcessor
from .factory import create_pdf_processor

__all__ = ["PDFProcessor", "create_pdf_processor"]
