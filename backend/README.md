# Paper Research Assistant - Backend

FastAPI-based backend for research paper management and RAG-based Q&A.

## Features

- Semantic search for research papers
- PDF upload and processing
- RAG-based question answering on papers
- Vector database for efficient retrieval

## Setup

### 1. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Variables

```bash
cp .env.example .env
# Edit .env file and add your GEMINI_API_KEY
```

### 3. Start Qdrant

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### 4. Start Server

```bash
uvicorn app.main:app --reload --port 8000
```

The server will run at http://localhost:8000

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Papers

- `POST /api/v1/papers/search` - Search for papers
- `POST /api/v1/papers/upload` - Upload a new paper
- `GET /api/v1/papers` - List all papers
- `GET /api/v1/papers/{paper_id}` - Get paper details
- `DELETE /api/v1/papers/{paper_id}` - Delete a paper

### Chat

- `POST /api/v1/chat/{paper_id}` - Chat with a specific paper

### Health

- `GET /api/v1/health` - Health check

## Architecture

```
app/
├── main.py                          # FastAPI entry point
├── core/                            # Core layer
│   ├── config.py                    # Configuration management
│   ├── exceptions.py                # Custom exceptions
│   └── interfaces/                  # Protocol-based interfaces
├── infrastructure/                  # Infrastructure layer
│   ├── embedding/                   # Gemini embedding implementation
│   ├── llm/                         # Gemini LLM implementation
│   ├── vector_store/                # Qdrant implementation
│   └── pdf_processor/               # PDF processing implementation
├── domain/                          # Domain layer
│   ├── models/                      # Pydantic schemas
│   └── services/                    # Business logic
├── application/                     # Application layer
│   └── dependencies.py              # Dependency injection
└── presentation/                    # Presentation layer
    └── routers/                     # API routers
```

## Development

Run tests:

```bash
pytest
```

## Docker

Build and run with Docker:

```bash
docker build -t paper-chat-backend .
docker run -p 8000:8000 --env-file .env paper-chat-backend
```
