from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from src.core.config import settings
from src.schemas.rag import RagResponse
from src.services.rag_pipeline import RagPipeline

router = APIRouter()


@router.post("/rag/cheatsheet", response_model=RagResponse)
async def generate_cheatsheet(
    files: list[UploadFile] = File(...),
    query: str | None = Form(None),
    top_k: int | None = Form(None),
    chunk_size: int | None = Form(None),
    chunk_overlap: int | None = Form(None),
    flashcard_count: int = Form(8),
) -> RagResponse:
    try:
        if not 1 <= len(files) <= settings.MAX_FILES:
            raise ValueError(f"Upload between 1 and {settings.MAX_FILES} files.")
        pipeline = RagPipeline()
        return await pipeline.generate_cheatsheet(
            files=files,
            query=query,
            top_k=top_k,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            flashcard_count=flashcard_count,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
