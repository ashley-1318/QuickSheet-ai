# QuickSheet AI - Backend Guide

This guide covers the FastAPI backend for QuickSheet AI, including setup, environment variables, and deployment.

## Prerequisites

- Python 3.8+
- Node.js 16+
- Groq API keys (https://console.groq.com/keys)

## Setup

1. Copy the environment template

```bash
cp .env.example .env
```

2. Add required keys to `.env`

```bash
GROQ_API_KEY_CHEATSHEET=your_key_here
GROQ_API_KEY_CHAT=your_key_here
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
GOOGLE_CLIENT_ID=your_google_oauth_client_id
```

3. Install dependencies

```bash
npm install
```

## Running Locally

**Option 1: Run frontend + backend together**

```bash
npm run dev:all
```

This starts:

- FastAPI backend: http://127.0.0.1:8000
- Vite dev server: http://localhost:8080

**Option 2: Run backend only**

```bash
npm run dev:api
```

## Verify Setup

- Open Swagger UI: http://127.0.0.1:8000/docs
- Make a test request to `/api/v1/rag/cheatsheet` using the frontend UI

## Environment Variables

Required:

- `GROQ_API_KEY_CHEATSHEET`
- `GROQ_API_KEY_CHAT`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

Auth (recommended):

- `GOOGLE_CLIENT_ID`

Dev auth (optional):

- `ALLOW_DEV_AUTH` (set to `true` to bypass OAuth in dev)
- `DEV_USER_ID` (default: `dev-user-test`)

Tuning (optional):

- `MODEL_NAME`
- `LLM_TEMPERATURE`
- `MAX_FILE_SIZE_MB`
- `MAX_PDF_PAGES`
- `MAX_TOKENS_PER_CHUNK`
- `RAG_CHUNK_SIZE`
- `RAG_CHUNK_OVERLAP`
- `RAG_TOP_K`
- `RAG_MAX_FILES`
- `RAG_EMBEDDING_MODEL`

## API Endpoints

- **POST /api/v1/rag/cheatsheet**
  - Accepts multipart form data with `files[]` and options
  - Returns structured cheat sheet JSON

- **POST /api/v1/chat/ask**
  - Ask follow-up questions using the extracted context

- **GET /api/v1/history**
  - Returns past generated cheat sheets

- **GET /health**
  - Health check endpoint

## Deployment (Railway)

- Uses `railway.json` with:
  - `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Set the same environment variables in Railway
- If you see 401 errors in production, verify `GOOGLE_CLIENT_ID` or set `ALLOW_DEV_AUTH=true`

## Troubleshooting

- **401 Unauthorized**: missing/invalid OAuth token or `ALLOW_DEV_AUTH` not set
- **500 error on cheatsheet**: missing env vars, auth failure, or LLM errors
- **No extractable text**: scanned PDFs need OCR (pdf2image + tesseract)
