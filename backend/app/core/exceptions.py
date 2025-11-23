"""Custom exceptions for the application."""


class ApplicationError(Exception):
    """Base exception for application errors."""
    pass


class EmbeddingError(ApplicationError):
    """Exception raised for embedding operations."""
    pass


class VectorStoreError(ApplicationError):
    """Exception raised for vector store operations."""
    pass


class LLMError(ApplicationError):
    """Exception raised for LLM operations."""
    pass


class PDFProcessingError(ApplicationError):
    """Exception raised for PDF processing operations."""
    pass


class PaperNotFoundError(ApplicationError):
    """Exception raised when paper is not found."""
    pass


class InvalidFileError(ApplicationError):
    """Exception raised for invalid file uploads."""
    pass


class DuplicatePaperError(ApplicationError):
    """Exception raised when attempting to upload a duplicate paper."""
    pass
