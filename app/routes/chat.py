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
        
        exam_instructions = (
            f"Adapt your response style based on Exam Mode: {payload.exam_mode}\n"
            "- Semester Exam -> Clear explanation with examples\n"
            "- Competitive Exam -> Short, precise, high-yield\n"
            "- Interview Prep -> Deep conceptual explanation with edge cases\n"
        )

        completion = get_chat_client().chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0.3,
            max_tokens=1500,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a document-grounded AI study assistant. "
                        "Answer strictly based on the retrieved context. "
                        f"{exam_instructions}"
                        "Rules:\n"
                        "1. Use only retrieved context.\n"
                        "2. If answer not found, respond: 'This is not covered in the uploaded material.'\n"
                        "3. Be concise but technically correct.\n"
                        "4. Avoid hallucination.\n"
                        "5. Format in bullet points where possible.\n"
                        "6. If formula involved, format clearly."
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
    """Serialize cheatsheet data into text for RAG."""
    parts = []
    
    # Priority fields
    if title := data.get("title"):
        parts.append(f"Title: {title}")
    if summary := data.get("one_line_summary"):
        parts.append(f"Summary: {summary}")
        
    # List fields
    for field in ["definitions", "core_formulas", "key_concepts", "important_metrics", "mistakes_to_avoid"]:
        if items := data.get(field):
            if isinstance(items, list):
                parts.extend([str(item) for item in items if item])
                
    # Flashcards
    if flashcards := data.get("flashcards"):
        for card in flashcards:
            if isinstance(card, dict):
                q = card.get("question", "")
                a = card.get("answer", "")
                if q or a:
                    parts.append(f"Q: {q}\nA: {a}")
                    
    return "\n\n".join(parts)


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
