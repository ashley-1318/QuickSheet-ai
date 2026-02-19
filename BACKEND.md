# QuickSheet AI - Backend Setup Guide

## Prerequisites

- Python 3.8+
- Node.js 16+
- Groq API Key (get one at https://console.groq.com/keys)

## Setup

### 1. Copy environment template
```bash
cp .env.example .env
```

### 2. Add your Groq API Key to `.env`
```
GROQ_API_KEY=your_api_key_here
```

### 3. Install dependencies
```bash
# Install Node dependencies (includes backend scripts)
npm install

# Backend dependencies are already in requirements.txt
# They should be installed in your virtual environment
```

## Running the App

### Option 1: Run both frontend + backend together (recommended)
```bash
npm run dev:all
```
This starts:
- **FastAPI backend** on `http://127.0.0.1:8000`
- **Vite dev server** on `http://localhost:8080`

### Option 2: Run individually
```bash
# Terminal 1: Backend API
npm run dev:api

# Terminal 2: Frontend (in another terminal)
npm run dev
```

## Verify Setup

1. **Backend is running:**
   ```bash
   curl http://127.0.0.1:8000/docs
   ```
   Should open Swagger UI.

2. **Frontend is running:**
   Open `http://localhost:8080` in your browser.

3. **Upload a PDF/DOCX:**
   - The frontend now sends files to the backend
   - Backend extracts text and generates cheat sheets
   - Results display in real-time

## Troubleshooting

### "Failed to fetch" error
- Backend is not running. Check `npm run dev:api` output for errors.
- Verify `GROQ_API_KEY` is set in your shell before starting the backend.

### PDFs with scanned images (OCR needed)
If your PDFs are scanned images, install OCR dependencies:
```bash
pip install pdf2image pytesseract
```
Also install Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki

### "No extractable text found"
- The PDF is empty or has no selectable text
- Try a different PDF with actual text content

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Groq API key for LLM service | Yes |
| `MAX_FILE_SIZE_MB` | Max upload size (default: 10) | No |
| `MAX_PDF_PAGES` | Max pages per PDF (default: 20) | No |
| `MAX_TOKENS_PER_CHUNK` | Tokens per API call (default: 3500) | No |
| `MODEL_NAME` | LLM model to use (default: llama-3.1-8b-instant) | No |

## API Endpoints

- **POST /api/generate-cheatsheet** - Generate cheat sheet from file
  - Accepts: PDF or DOCX files
  - Returns: JSON with cheat sheet content, flashcards, stats

- **GET /docs** - Swagger UI documentation
