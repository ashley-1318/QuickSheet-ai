from __future__ import annotations

import logging
import math
from typing import Any, Dict, List

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.config import settings
from app.services.llm_service import LlmService, LlmServiceError
from app.services.prompt_builder import SYSTEM_PROMPT, build_user_prompt
from app.services.text_cleaner import clean_text
from app.services.text_extractor import FileTooLargeError, UnsupportedFileError, extract_text
from app.utils.metrics import timed_operation

logger = logging.getLogger(__name__)
router = APIRouter()


def _chunk_text(text: str) -> List[str]:
    words = text.split()
    if not words:
        return [""]

    estimated_tokens_per_word = 1.3
    max_words = math.floor(settings.max_tokens_per_chunk / estimated_tokens_per_word)
    max_words = max(max_words, 500)

    chunks = []
    for start in range(0, len(words), max_words):
        chunk_words = words[start : start + max_words]
        chunks.append(" ".join(chunk_words))
    return chunks


def _merge_chunks(results: List[Dict[str, Any]]) -> Dict[str, List[Any]]:
    merged = {
        "key_concepts": [],
        "definitions": [],
        "formulas": [],
        "revision_points": [],
        "flashcards": [],
    }
    for result in results:
        for key in merged:
            value = result.get(key, [])
            if isinstance(value, list):
                merged[key].extend(value)
    return merged


@router.post("/api/generate-cheatsheet")
async def generate_cheatsheet(
    file: UploadFile = File(...),
    revision_mode: str = Form("standard"),
    exam_mode: str = Form("semester"),
    formula_only: bool = Form(False),
    flashcards: bool = Form(True),
) -> Dict[str, Any]:
    if file.content_type not in {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    }:
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, PPT, and PPTX files are supported")

    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)
    logger.info("Uploaded file size: %.2fMB", file_size_mb)
    if file_size_mb > settings.max_file_size_mb:
        raise HTTPException(status_code=413, detail="File size exceeds 10MB limit")

    try:
        raw_text, page_count = extract_text(file.filename or "", content)
    except FileTooLargeError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    except UnsupportedFileError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to extract text") from exc

    cleaned_text = clean_text(raw_text)
    if not cleaned_text:
        raise HTTPException(status_code=400, detail="No extractable text found")

    chunks = _chunk_text(cleaned_text)
    logger.info("Chunk count: %s (pages: %s)", len(chunks), page_count)

    llm = LlmService()
    options = {
        "revision_mode": revision_mode,
        "exam_mode": exam_mode,
        "formula_only": formula_only,
        "flashcards": flashcards,
    }

    responses: List[Dict[str, Any]] = []
    with timed_operation() as timer:
        for chunk in chunks:
            user_prompt = build_user_prompt(chunk, options)
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ]
            try:
                responses.append(llm.generate_cheatsheet(messages))
            except LlmServiceError as exc:
                raise HTTPException(status_code=503, detail=str(exc)) from exc
        processing_seconds = timer()

    merged = _merge_chunks(responses)
    if not flashcards:
        merged["flashcards"] = []

    original_word_count = len(cleaned_text.split())
    compressed_word_count = sum(len(str(item).split()) for item in merged.values())
    compression_ratio = round(compressed_word_count / max(original_word_count, 1), 4)

    logger.info("Processing time: %.2fs", processing_seconds)

    return {
        "original_word_count": original_word_count,
        "compressed_word_count": compressed_word_count,
        "compression_ratio": compression_ratio,
        "processing_time_seconds": round(processing_seconds, 3),
        "cheatsheet": {
            "key_concepts": merged["key_concepts"],
            "definitions": merged["definitions"],
            "formulas": merged["formulas"],
            "revision_points": merged["revision_points"],
        },
        "flashcards": merged["flashcards"],
    }
