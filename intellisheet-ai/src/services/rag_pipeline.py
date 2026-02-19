import json
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from fastapi import UploadFile

from src.core.config import settings
from src.schemas.rag import RagResponse
from src.services.chunker import chunk_text
from src.services.document_loader import load_documents
from src.services.embedding_service import EmbeddingService
from src.services.vector_store import build_vector_store, retrieve_chunks


class RagPipeline:
    def __init__(self) -> None:
        self._embedding_service = EmbeddingService()
        self._llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
            temperature=0.2,
        )

    async def generate_cheatsheet(
        self,
        files: list[UploadFile],
        query: str | None,
        top_k: int | None,
        chunk_size: int | None,
        chunk_overlap: int | None,
        flashcard_count: int,
    ) -> RagResponse:
        text = await load_documents(files)
        documents = chunk_text(
            text,
            chunk_size=chunk_size or settings.CHUNK_SIZE,
            chunk_overlap=chunk_overlap or settings.CHUNK_OVERLAP,
        )
        store = build_vector_store(documents, self._embedding_service.embeddings)
        search_query = query or "Generate a concise cheat sheet for this document."
        retrieved_docs = retrieve_chunks(store, search_query, top_k=top_k or settings.TOP_K)
        context = "\n\n".join(doc.page_content for doc in retrieved_docs)

        clamped_count = max(5, min(10, flashcard_count))
        flashcard_instruction = (
            "- flashcards: array of objects with keys 'question' and 'answer'\n"
            f"- flashcards_count: generate exactly {clamped_count} flashcards\n"
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an expert study assistant. Prioritize accuracy and use only information grounded in the provided context. "
                    "Use precise terminology and avoid speculation. "
                    "Produce a highly structured cheat sheet. "
                    "Return ONLY valid JSON with these keys (only include keys with content, omit empty arrays): \n"
                    "- title: concise title\n"
                    "- one_line_summary: single sentence overview\n"
                    "- definitions: array of 'Term: definition' strings (must include a colon and a definition sentence; no bare terms)\n"
                    "- core_formulas: array of essential formulas/equations\n"
                    "- key_concepts: array of main ideas and principles\n"
                    "- diagrams: array of diagram descriptions or ASCII representations\n"
                    "- comparison_table: array of comparison entries (e.g. 'X vs Y: differences')\n"
                    "- important_metrics: array of key metrics, benchmarks, or numbers\n"
                    "- mistakes_to_avoid: array of common pitfalls and errors\n"
                    f"{flashcard_instruction}",
                ),
                (
                    "user",
                    "Context:\n{context}\n\nInstruction:\n{instruction}",
                ),
            ]
        )

        response = self._llm.invoke(
            prompt.format_messages(
                context=context,
                instruction=search_query,
            )
        )

        response_text = _normalize_content(response.content)
        parsed = _safe_parse_json(response_text)
        if parsed is None:
            return RagResponse(
                title="Cheat Sheet",
                one_line_summary="",
                definitions=[],
                core_formulas=[],
                key_concepts=[],
                diagrams=[],
                comparison_table=[],
                important_metrics=[],
                mistakes_to_avoid=[],
                flashcards=[],
                original_words=_count_words(text),
                compressed_words=0,
                raw_response=response_text,
            )

        response = RagResponse(
            title=str(parsed.get("title", "Cheat Sheet")),
            one_line_summary=str(parsed.get("one_line_summary", "")),
            definitions=_normalize_list(parsed.get("definitions")),
            core_formulas=_normalize_list(parsed.get("core_formulas")),
            key_concepts=_normalize_list(parsed.get("key_concepts")),
            diagrams=_normalize_list(parsed.get("diagrams")),
            comparison_table=_normalize_list(parsed.get("comparison_table")),
            important_metrics=_normalize_list(parsed.get("important_metrics")),
            mistakes_to_avoid=_normalize_list(parsed.get("mistakes_to_avoid")),
            flashcards=_normalize_flashcards(parsed.get("flashcards")),
            original_words=_count_words(text),
            compressed_words=0,
            raw_response=None,
        )
        response.compressed_words = _count_words_from_sections(response)
        return response


def _safe_parse_json(content: str) -> dict | None:
    try:
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        return json.loads(content)
    except json.JSONDecodeError:
        return None


def _normalize_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    return json.dumps(content)


def _normalize_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, dict):
        return [f"{key}: {val}" for key, val in value.items()]
    return [str(value)]


def _normalize_flashcards(value: Any) -> list[dict[str, str]]:
    if value is None:
        return []
    if isinstance(value, list):
        normalized = []
        for item in value:
            if isinstance(item, dict):
                question = str(item.get("question", "")).strip()
                answer = str(item.get("answer", "")).strip()
                if question or answer:
                    normalized.append({"question": question, "answer": answer})
            else:
                text = str(item).strip()
                if text:
                    normalized.append({"question": text, "answer": ""})
        return normalized
    if isinstance(value, dict):
        question = str(value.get("question", "")).strip()
        answer = str(value.get("answer", "")).strip()
        return [{"question": question, "answer": answer}] if (question or answer) else []
    return []


def _count_words(text: str) -> int:
    return len(text.split())


def _count_words_from_sections(response: RagResponse) -> int:
    parts = [
        response.title,
        response.one_line_summary,
        *response.definitions,
        *response.core_formulas,
        *response.key_concepts,
        *response.diagrams,
        *response.comparison_table,
        *response.important_metrics,
        *response.mistakes_to_avoid,
    ]
    flashcard_parts = []
    for card in response.flashcards:
        flashcard_parts.extend([card.question, card.answer])
    parts.extend(flashcard_parts)
    return _count_words(" ".join(p for p in parts if p))
