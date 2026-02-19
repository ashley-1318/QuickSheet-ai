import logging
import time
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.config import settings
from app.schemas.chat import ChatAskRequest, ChatAskResponse
from app.services.chat_llm_service import get_chat_client
from app.services.chunker import chunk_text
from app.services.embedding_service import EmbeddingService
from app.services.supabase_client import supabase
from app.services.vector_store import build_vector_store, retrieve_chunks
from app.utils.auth import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/chat")


@router.post("/ask", response_model=ChatAskResponse)
def ask_chat(
    payload: ChatAskRequest,
    user_id: str = Depends(get_current_user_id),
) -> ChatAskResponse:
    start_time = time.perf_counter()
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    if not settings.groq_api_key_chat:
        raise HTTPException(status_code=500, detail="Missing GROQ_API_KEY_CHAT")

    cheatsheet = _fetch_cheatsheet(payload.cheatsheet_id, user_id)
    if not cheatsheet:
        raise HTTPException(status_code=404, detail="Cheatsheet not found")

    context_text = _serialize_structured_json(cheatsheet)
    if not context_text.strip():
        answer = "Not found in uploaded material."
        _save_chat_messages(user_id, payload.cheatsheet_id, payload.question, answer)
        return ChatAskResponse(
            answer=answer,
            retrieved_chunks=0,
            processing_time_ms=_elapsed_ms(start_time),
        )

    logger.info("Serialized context: %d characters", len(context_text))

    embed_start = time.perf_counter()
    documents = chunk_text(
        context_text,
        chunk_size=settings.rag_chunk_size,
        chunk_overlap=settings.rag_chunk_overlap,
    )
    logger.info("Created %d chunks from context", len(documents))
    if documents:
        logger.debug("First chunk preview: %s...", documents[0].page_content[:200])
    
    store = build_vector_store(documents, EmbeddingService().embeddings)
    embed_elapsed = _elapsed_ms(embed_start)

    retrieval_start = time.perf_counter()
    retrieved_docs = retrieve_chunks(store, payload.question, top_k=5)
    retrieval_elapsed = _elapsed_ms(retrieval_start)
    
    logger.info("Retrieved %d chunks for question: '%s'", len(retrieved_docs), payload.question)
    if retrieved_docs:
        logger.debug("Retrieved chunks: %s", [doc.page_content[:100] for doc in retrieved_docs])
        for i, doc in enumerate(retrieved_docs[:3]):  # Log first 3 chunks in detail
            logger.info(f"  Chunk {i}: {doc.page_content[:200]}")

    if not retrieved_docs:
        answer = "Not found in uploaded material."
        _save_chat_messages(user_id, payload.cheatsheet_id, payload.question, answer)
        return ChatAskResponse(
            answer=answer,
            retrieved_chunks=0,
            processing_time_ms=_elapsed_ms(start_time),
        )

    context = "\n\n".join(doc.page_content for doc in retrieved_docs)
    context = _truncate_text(context, 12000)  # Increased from 6000 to ensure full context
    
    logger.info(f"Context being sent to LLM: {len(context)} characters")
    logger.debug(f"Context preview:\n{context[:500]}")

    llm_start = time.perf_counter()
    try:
        # Clean up context to remove any problematic characters
        clean_context = context.encode('utf-8', errors='replace').decode('utf-8')
        
        logger.debug(f"Sending to Groq - context length: {len(clean_context)}, question: {payload.question}")
        
        completion = get_chat_client().chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0.3,
            max_tokens=1500,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful study assistant. Your job is to answer questions about the provided material. "
                        "Use the context provided to answer the user's question as accurately as possible. "
                        "If the answer is not in the provided context, say 'This information is not in the provided material.' "
                        "Always try to provide useful information if you can find any relevant content."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Based on the following material, answer this question: {payload.question}\n\nMaterial:\n{clean_context}",
                },
            ],
        )
        
        logger.debug(f"Groq response status: {completion.model_dump_json()[:200]}")
        
    except Exception as exc:
        logger.error(f"Chat LLM request failed: {exc}", exc_info=True)
        _save_chat_messages(user_id, payload.cheatsheet_id, payload.question, "Error generating response")
        raise HTTPException(status_code=500, detail="Chat generation failed") from exc

    llm_elapsed = _elapsed_ms(llm_start)
    
    try:
        answer = completion.choices[0].message.content.strip() if completion.choices else ""
    except (IndexError, AttributeError) as exc:
        logger.error(f"Failed to extract answer from Groq response: {exc}")
        answer = ""
    
    if not answer or answer.lower() == "not found in uploaded material.":
        # Only use fallback if truly no answer
        logger.warning("Empty or fallback answer from LLM, returning error message")
        answer = "I couldn't find information about this in the material."
    
    logger.info(f"LLM answer: {answer[:100]}...")

    _save_chat_messages(user_id, payload.cheatsheet_id, payload.question, answer)

    logger.info(
        "Chat timings: embed=%sms, retrieval=%sms, llm=%sms, total=%sms",
        embed_elapsed,
        retrieval_elapsed,
        llm_elapsed,
        _elapsed_ms(start_time),
    )

    try:
        response = ChatAskResponse(
            answer=answer,
            retrieved_chunks=len(retrieved_docs),
            processing_time_ms=_elapsed_ms(start_time),
        )
        logger.info(f"Chat response created: answer_length={len(answer)}, chunks={len(retrieved_docs)}")
        return response
    except Exception as exc:
        logger.error(f"Failed to create response: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create response") from exc



@router.get("/history/{cheatsheet_id}")
def get_chat_history(
    cheatsheet_id: str,
    user_id: str = Depends(get_current_user_id),
) -> list[dict]:
    try:
        result = (
            supabase.table("chat_messages")
            .select("id, user_id, cheatsheet_id, role, message, created_at")
            .eq("cheatsheet_id", cheatsheet_id)
            .eq("user_id", user_id)
            .order("created_at", desc=False)
            .execute()
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to fetch chat history") from exc

    return result.data or []


@router.delete("/clear/{cheatsheet_id}")
def clear_chat_history(
    cheatsheet_id: str,
    user_id: str = Depends(get_current_user_id),
) -> dict:
    try:
        result = (
            supabase.table("chat_messages")
            .delete()
            .eq("cheatsheet_id", cheatsheet_id)
            .eq("user_id", user_id)
            .execute()
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to clear chat history") from exc

    if result.data is None:
        return {"status": "ok"}
    return {"status": "ok"}


def _fetch_cheatsheet(cheatsheet_id: str, user_id: str) -> dict | None:
    try:
        result = (
            supabase.table("cheatsheets")
            .select("structured_json")
            .eq("id", cheatsheet_id)
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to fetch cheatsheet") from exc

    if not result.data:
        return None
    return result.data[0].get("structured_json") or {}


def _serialize_structured_json(data: dict[str, Any]) -> str:
    """Serialize cheatsheet data into semantically rich text for FAISS indexing.
    
    Focus on extracting actual content from the structured data, avoiding
    excessive markup that would dilute semantic similarity.
    """
    parts: list[str] = []
    
    # These are the actual content fields from RagResponse
    content_fields = {
        "title": 3,  # weight - appears 3 times
        "one_line_summary": 3,
        "definitions": 2,
        "core_formulas": 2,
        "key_concepts": 2,
        "diagrams": 1,
        "comparison_table": 1,
        "important_metrics": 1,
        "mistakes_to_avoid": 1,
    }
    
    for field, weight in content_fields.items():
        value = data.get(field)
        if not value:
            continue
        
        # Add field as context (helps with semantic search)
        for _ in range(weight):
            if isinstance(value, str):
                if value.strip():
                    parts.append(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and item.strip():
                        parts.append(item)
                    elif isinstance(item, dict):
                        for k, v in item.items():
                            if isinstance(v, str) and v.strip():
                                parts.append(f"{k}: {v}")
    
    # Add flashcards if present
    flashcards = data.get("flashcards", [])
    if flashcards:
        for fc in flashcards:
            if isinstance(fc, dict):
                q = fc.get("question") or fc.get("prompt")
                a = fc.get("answer")
                if q and isinstance(q, str):
                    parts.append(q)
                if a and isinstance(a, str):
                    parts.append(a)
    
    serialized = "\n\n".join(parts)
    logger.info("Serialized context: %d characters, %d lines", len(serialized), len(parts))
    if serialized and logger.isEnabledFor(logging.DEBUG):
        logger.debug("Content sample:\n%s", serialized[:500])
    return serialized


def _save_chat_messages(user_id: str, cheatsheet_id: str, question: str, answer: str) -> None:
    try:
        supabase.table("chat_messages").insert(
            [
                {
                    "user_id": user_id,
                    "cheatsheet_id": cheatsheet_id,
                    "role": "user",
                    "message": question,
                },
                {
                    "user_id": user_id,
                    "cheatsheet_id": cheatsheet_id,
                    "role": "assistant",
                    "message": answer,
                },
            ]
        ).execute()
    except Exception as exc:
        logger.error("Failed to save chat messages: %s", exc)


def _truncate_text(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit]


def _elapsed_ms(start_time: float) -> int:
    return int((time.perf_counter() - start_time) * 1000)
