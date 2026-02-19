# QuickSheet AI

QuickSheet AI is a document-to-cheat-sheet generator with a RAG pipeline and a React UI. Upload study materials (PDF/DOCX/PPTX/TXT), get a structured cheat sheet, and optionally flashcards.

## Tech Stack

**Frontend**

- React 18 + TypeScript + Vite
- Tailwind CSS + shadcn-ui + Radix UI
- Framer Motion, Lucide icons
- jsPDF + Markdown export

**Backend**

- FastAPI + Uvicorn
- Groq LLM (default: llama-3.1-8b-instant)
- LangChain + FAISS + Sentence-Transformers embeddings
- pdfplumber, python-docx, python-pptx, text

## Architecture

1. Frontend sends files and options to the RAG endpoint.
2. Backend extracts text, chunks it, embeds, and retrieves top-K relevant chunks.
3. Groq LLM generates structured JSON output.
4. Frontend renders the cheat sheet and flashcards; export options are available.

## End-to-End Workflow

1. Upload 1-4 study files.
2. Choose Advanced Options (exam mode, revision mode, formula-only, flashcards, flashcard count).
3. Backend builds the RAG context and calls the LLM.
4. UI displays sections and flashcards.
5. Export PDF/Markdown or copy to clipboard.

## API

**POST /api/v1/rag/cheatsheet**

Form fields:

- files[] (PDF, DOCX, PPTX, TXT)
- query (optional)
- top_k (optional)
- chunk_size (optional)
- chunk_overlap (optional)
- flashcards (bool)
- flashcard_count (5-10)

Response fields (structured):

- title
- one_line_summary
- definitions
- core_formulas
- key_concepts
- diagrams
- comparison_table
- important_metrics
- mistakes_to_avoid
- flashcards
- original_words
- compressed_words

## Configuration

Environment variables are loaded from .env.

Required:

- GROQ_API_KEY
- SUPABASE_URL
- SUPABASE_SERVICE_ROLE_KEY

Optional (defaults in app/config.py):

- MODEL_NAME
- LLM_TEMPERATURE
- GOOGLE_CLIENT_ID
- MAX_FILE_SIZE_MB
- MAX_PDF_PAGES
- RAG_CHUNK_SIZE
- RAG_CHUNK_OVERLAP
- RAG_TOP_K
- RAG_MAX_FILES
- RAG_EMBEDDING_MODEL

## Run Locally

1. Install dependencies

```bash
npm install
```

2. Create .env

```bash
cp .env.example .env
```

3. Add Groq API key

```bash
GROQ_API_KEY=your_key_here
```

4. Start full app

```bash
npm run dev:all
```

This starts:

- Backend: http://127.0.0.1:8000
- Frontend: http://localhost:8080 (or next available port)

## Troubleshooting

- **Port in use**: stop the process on 8000/8080 and rerun dev:all.
- **Failed to fetch**: backend not running or wrong port.
- **No extractable text**: PDF is scanned image; install OCR tools if needed.
- **Slow first run**: sentence-transformers model downloads on first use.

## Project Structure (High Level)

- app/ (FastAPI backend)
- src/ (React frontend)
- intellisheet-ai/ (legacy backend)
- public/ (static assets)
