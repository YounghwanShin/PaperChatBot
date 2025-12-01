"""Application configuration management."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Paper Research Assistant"
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: Optional[str] = None
    papers_collection: str = "papers_metadata"
    chunks_collection_prefix: str = "paper_chunks"

    # Embedding
    embedding_model: str = "gemini-embedding-001"
    embedding_dimension: int = 768

    # LLM
    gemini_api_key: str
    llm_model: str = "gemini-2.0-flash"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 1024

    # Retrieval
    search_top_k: int = 5
    similarity_threshold: float = 0.6
    chunk_top_k: int = 5
    chunk_threshold: float = 0.5

    # PDF Processing
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_upload_size: int = 50 * 1024 * 1024  # 50MB
    upload_dir: str = "uploads"

    # arXiv Settings
    arxiv_category: str = "cs.CL"  # NLP category
    arxiv_max_results: int = 20  # Reduced to avoid quota issues
    arxiv_delay_seconds: float = 3.0  # API rate limit compliance
    arxiv_num_retries: int = 3

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
