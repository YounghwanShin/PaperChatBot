"""Factory for creating PDF processor instances."""

from ...core.interfaces import PDFProcessorProtocol
from .processor import PDFProcessor


def create_pdf_processor() -> PDFProcessorProtocol:
    """Create a PDF processor instance.

    Returns:
        PDF processor instance
    """
    return PDFProcessor()
