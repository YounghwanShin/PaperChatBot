# Paper Research Assistant - Frontend

Next.js-based frontend for research paper management and AI-powered Q&A.

## Features

- Semantic search for research papers
- PDF upload with metadata
- Interactive chat interface for paper Q&A
- Modern, responsive UI with Tailwind CSS

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Environment Variables

```bash
cp .env.example .env.local
# Edit .env.local if needed to point to your backend
```

### 3. Start Development Server

```bash
npm run dev
```

The application will run at http://localhost:3000

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Architecture

```
src/
├── app/
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Main application page
│   └── globals.css          # Global styles
├── components/
│   ├── PaperSearch.tsx      # Paper search component
│   ├── PaperUpload.tsx      # Paper upload component
│   └── ChatInterface.tsx    # Chat UI component
└── lib/
    ├── api.ts               # API client
    ├── messageUtils.ts      # Message utilities
    └── constants.ts         # Constants
```

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Markdown**: React Markdown

## Docker

Build and run with Docker:

```bash
docker build -t paper-chat-frontend .
docker run -p 3000:3000 paper-chat-frontend
```
