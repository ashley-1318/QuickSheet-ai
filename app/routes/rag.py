import logging

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile

from app.config import settings
from app.schemas.rag import RagResponse
from app.services.rag_pipeline import RagPipeline
from app.services.supabase_client import supabase
from app.utils.auth import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1")


def _save_cheatsheet_to_db(user_id: str, result: RagResponse) -> str | None:
    """Save cheatsheet to database and return ID."""
    try:
        insert_result = (
            supabase.table("cheatsheets")
            .insert(
                {
                    "user_id": user_id,
                    "title": result.title,
                    "one_line_summary": result.one_line_summary,
                    "structured_json": result.model_dump(),
                }
            )
            .execute()
        )
        if insert_result.data:
            cheatsheet_id = insert_result.data[0].get("id")
            logger.info(f"Cheatsheet saved with ID: {cheatsheet_id}")
            return cheatsheet_id
    except Exception as exc:
        logger.error("DB save failed: %s", _safe_for_log(str(exc)))
    return None


@router.post("/rag/cheatsheet", response_model=RagResponse)
async def generate_cheatsheet(
    files: list[UploadFile] = File(...),
    query: str | None = Form(None),
    top_k: int | None = Form(None),
    chunk_size: int | None = Form(None),
    chunk_overlap: int | None = Form(None),
    flashcards: bool = Form(True),
    flashcard_count: int = Form(8),
    fast_mode: bool = Form(False),
    revision_mode: str = Form("Standard"),
    exam_mode: str = Form("Semester Exam"),
    user_id: str = Depends(get_current_user_id),
    
) -> RagResponse:
    try:
        logger.debug("Received %s files (fast_mode=%s)", len(files), fast_mode)
        for f in files:
            logger.debug("File: %s, size: %s", _safe_for_log(str(f.filename)), f.size)
        
        if not 1 <= len(files) <= settings.rag_max_files:
            raise ValueError(f"Upload between 1 and {settings.rag_max_files} files.")
        
        pipeline = RagPipeline()
        mode_instructions = f"Revision Mode: {revision_mode}\nExam Mode: {exam_mode}"
        logger.info(f"Generating cheat sheet with modes: {mode_instructions.replace('\n', ', ')}")

        result = await pipeline.generate_cheatsheet(
            files=files,
            query=query,
            top_k=top_k,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            flashcards=flashcards,
            flashcard_count=flashcard_count,
            fast_mode=fast_mode,
            mode_instructions=mode_instructions,
        )
        
        # Save to DB synchronously to get ID for chat
        cheatsheet_id = _save_cheatsheet_to_db(user_id, result)
        if cheatsheet_id:
            result.cheatsheet_id = cheatsheet_id
        
        logger.debug(
            "Result - title: %s, definitions: %s, key_concepts: %s",
            _safe_for_log(result.title),
            len(result.definitions),
            len(result.key_concepts),
        )
        return result
    except ValueError as exc:
        logger.error("ValueError: %s", _safe_for_log(str(exc)))
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        import traceback
        error_trace = traceback.format_exc()
        logger.error("Unexpected error: %s\n%s", _safe_for_log(str(exc)), error_trace)
        # Return the actual error message to help debugging
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(exc)}") from exc


def _safe_for_log(text: str) -> str:
    return text.encode("ascii", "backslashreplace").decode("ascii")
