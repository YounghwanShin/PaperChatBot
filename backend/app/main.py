"""FastAPI main application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .domain.models import HealthResponse
from .application.dependencies import get_vector_store
from .presentation.routers import papers_router, chat_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Research paper assistant with semantic search and RAG-based Q&A"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(papers_router, prefix=settings.api_prefix)
app.include_router(chat_router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    """Root endpoint.

    Returns:
        Application information
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }


@app.get(f"{settings.api_prefix}/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint.

    Returns:
        Health status response
    """
    try:
        vector_store = get_vector_store()
        qdrant_connected = vector_store.health_check()
        papers_collection_exists = vector_store.collection_exists(settings.papers_collection)

        return HealthResponse(
            status="healthy" if qdrant_connected else "degraded",
            version=settings.app_version,
            qdrant_connected=qdrant_connected,
            papers_collection_exists=papers_collection_exists
        )
    except Exception:
        return HealthResponse(
            status="unhealthy",
            version=settings.app_version,
            qdrant_connected=False,
            papers_collection_exists=False
        )


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Qdrant: {settings.qdrant_host}:{settings.qdrant_port}")
    print(f"Papers Collection: {settings.papers_collection}")
    
    try:
        vector_store = get_vector_store()
        if vector_store.health_check():
            print("Qdrant connection successful")
            
            # Create papers collection if it doesn't exist
            if not vector_store.collection_exists(settings.papers_collection):
                vector_store.create_collection(
                    collection_name=settings.papers_collection,
                    vector_size=settings.embedding_dimension
                )
                print(f"Created papers collection: {settings.papers_collection}")
            else:
                info = vector_store.get_collection_info(settings.papers_collection)
                print(f"Papers Collection: {info.get('name')} | Points: {info.get('points_count')}")
        else:
            print("Warning: Qdrant connection failed")
    except Exception as e:
        print(f"Error connecting to Qdrant: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    print(f"Shutting down {settings.app_name}")
