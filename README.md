# Paper Research Assistant
(영어데이터처리를 위한 프로그래밍 과제)

AI-powered research paper management system with semantic search and interactive Q&A.

## Overview

This application helps researchers manage, search, and interact with academic papers.

It provides
- **Semantic Search**: Find papers using natural language queries based on title and abstract
- **PDF Upload**: Upload and process research papers with automatic text extraction
- **Interactive Q&A**: Chat with papers using RAG (Retrieval-Augmented Generation)
- **arXiv Integration**: Automatically fetch and process recent NLP papers from arXiv
- **Vector Database**: Efficient similarity search using Qdrant

## Features

### Paper Management
- Upload PDF papers with metadata (title, authors, abstract, year)
- Automatic text extraction and chunking
- Store papers in vector database for semantic search

### Semantic Search
- Search papers by natural language queries
- Ranked results based on similarity scores
- Filter by relevance threshold

### RAG-based Chat
- Ask questions about specific papers
- Answers grounded in paper content
- Confidence scores for responses
- Context-aware conversations

### arXiv Integration
- Automatic paper collection from arXiv (cs.CL category)
- Background processing for batch imports
- Task status tracking and progress monitoring
- Duplicate detection and skipping

## Tech Stack

### Backend
- **Framework**: FastAPI
- **Vector DB**: Qdrant
- **Embedding**: Google Gemini Embedding API (768-dim)
- **LLM**: Google Gemini 2.0 Flash
- **PDF Processing**: PyMuPDF
- **arXiv Integration**: arxiv Python library
- **Language**: Python 3.11

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Database**: Qdrant (Vector Database)

## Architecture

```
┌─────────────┐
│   Frontend  │  Next.js UI
│  (Next.js)  │
└──────┬──────┘
       │
       │ HTTP/REST
       │
┌──────▼──────┐
│   Backend   │  FastAPI Server
│  (FastAPI)  │
└──────┬──────┘
       │
       ├─────────────┐
       │             │
┌──────▼──────┐ ┌───▼────────┐
│   Qdrant    │ │   Gemini   │
│ Vector DB   │ │    API     │
└─────────────┘ └────────────┘
```

### Data Collections

1. **papers_metadata**: Paper search
   - Vector: title + abstract embedding
   - Payload: paper_id, title, authors, abstract, year, pdf_path

2. **paper_chunks_{paper_id}**: Per-paper Q&A
   - Vector: text chunk embedding
   - Payload: chunk_id, content, position

## Setup

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- Google Gemini API key

### Quick Start with Docker

1. Clone the repository:
```bash
git clone https://github.com/YounghwanShin/PaperChatBot.git
cd PaperChatBot
```

2. Set up environment variables:
```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env and add your GEMINI_API_KEY

# Frontend
cp frontend/.env.example frontend/.env.local
```

3. Start all services:
```bash
docker-compose up -d
```

4. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local Development

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add GEMINI_API_KEY
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

#### Qdrant
```bash
docker run -p 6333:6333 qdrant/qdrant
```

## Usage

### 1. Upload a Paper
- Click "Upload Paper" tab
- Select PDF file
- Fill in metadata (title, abstract, authors, year)
- Click "Upload Paper"

### 2. Search Papers
- Click "Search Papers" tab
- Enter search query
- Click "Search" or press Enter
- Select a paper from results

### 3. Chat with Paper
- After selecting a paper, click "Chat" tab
- Ask questions about the paper
- Receive answers grounded in paper content

### 4. Fetch Papers from arXiv (API)
- Use `POST /api/v1/papers/fetch-recent?days_ago=7` to start fetching recent papers
- Get task_id in response
- Poll `GET /api/v1/papers/fetch-status/{task_id}` to check progress
- Papers are automatically processed and added to the database

## API Documentation

### Papers Endpoints
- `POST /api/v1/papers/search` - Search papers
- `POST /api/v1/papers/upload` - Upload paper
- `GET /api/v1/papers` - List all papers
- `GET /api/v1/papers/{paper_id}` - Get paper details
- `DELETE /api/v1/papers/{paper_id}` - Delete paper
- `POST /api/v1/papers/fetch-recent` - Fetch recent papers from arXiv (background task)
- `GET /api/v1/papers/fetch-status/{task_id}` - Check arXiv fetch task status

### Chat Endpoints
- `POST /api/v1/chat/{paper_id}` - Chat with paper

### Health Check
- `GET /api/v1/health` - System health status

## Configuration

### Backend Settings (.env)
```
# Application
app_name=Paper Research Assistant
app_version=1.0.0
debug=False

# Server
host=0.0.0.0
port=8000

# CORS (comma-separated)
cors_origins=http://localhost:3000,http://127.0.0.1:3000

# Qdrant
qdrant_host=localhost
qdrant_port=6333
papers_collection=papers_metadata
chunks_collection_prefix=paper_chunks

# Embedding
embedding_model=gemini-embedding-001
embedding_dimension=768

# LLM
gemini_api_key=your_gemini_api_key_here
llm_model=gemini-2.0-flash
llm_temperature=0.1
llm_max_tokens=1024

# Retrieval
search_top_k=5
similarity_threshold=0.6
chunk_top_k=5
chunk_threshold=0.5

# PDF Processing
chunk_size=1000
chunk_overlap=200
max_upload_size=52428800  # 50MB
upload_dir=uploads
```

### Frontend Settings (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Project Structure

```
paper-chat-bot/
├── backend/
│   ├── app/
│   │   ├── core/              # Configuration, interfaces
│   │   ├── infrastructure/    # Gemini, Qdrant, PDF processor
│   │   ├── domain/            # Business logic, models
│   │   ├── application/       # Dependency injection
│   │   └── presentation/      # API routers
│   ├── uploads/               # Uploaded PDF files
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── app/               # Next.js pages
│       ├── components/        # React components
│       └── lib/               # Utilities, API client
├── docker-compose.yml
└── README.md
```

## Development

### Running Tests
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

### Code Style
- Backend: Follow PEP 8 guidelines
- Frontend: ESLint with Next.js config

## Deployment

### Production Build

Backend:
```bash
cd backend
docker build -t paper-chat-backend .
docker run -p 8000:8000 --env-file .env paper-chat-backend
```

Frontend:
```bash
cd frontend
npm run build
npm start
```

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please open an issue on GitHub.
