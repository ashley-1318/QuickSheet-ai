import json
import logging
import re
from typing import Any

from fastapi import UploadFile
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.config import settings
from app.schemas.rag import RagResponse
from app.services.chunker import chunk_text
from app.services.document_loader import load_documents
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import build_vector_store, retrieve_chunks


logger = logging.getLogger(__name__)


class RagPipeline:
    def __init__(self) -> None:
        self._embedding_service = EmbeddingService()
        self._llm = ChatGroq(
            api_key=settings.groq_api_key_cheatsheet,
            model=settings.model_name,
            temperature=settings.llm_temperature,
        )

    async def generate_cheatsheet(
        self,
        files: list[UploadFile],
        query: str | None,
        top_k: int | None,
        chunk_size: int | None,
        chunk_overlap: int | None,
        flashcards: bool,
        flashcard_count: int,
        fast_mode: bool = False,
        mode_instructions: str = ""
    ) -> RagResponse:
        import time
        extraction_start = time.time()
        
        text = await load_documents(files)
        extraction_time = (time.time() - extraction_start) * 1000
        
        # Use fast mode parameters if enabled
        if fast_mode:
            chunk_size = chunk_size or settings.fast_mode_chunk_size
            top_k = top_k or settings.fast_mode_top_k
        else:
            chunk_size = chunk_size or settings.rag_chunk_size
            top_k = top_k or settings.rag_top_k
        
        chunk_overlap = chunk_overlap or (
            settings.fast_mode_chunk_overlap if fast_mode else settings.rag_chunk_overlap
        )
        
        embedding_start = time.time()
        documents = chunk_text(
            text,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        store = build_vector_store(documents, self._embedding_service.embeddings)
        embedding_time = (time.time() - embedding_start) * 1000
        
        search_query = query or "Generate a concise cheat sheet for this document."
        
        retrieval_start = time.time()
        retrieved_docs = retrieve_chunks(store, search_query, top_k=top_k)
        retrieval_time = (time.time() - retrieval_start) * 1000
        
        context = "\n\n".join(doc.page_content for doc in retrieved_docs)

        clamped_count = max(5, min(10, flashcard_count))
        flashcard_rule = f"- Generate exactly {clamped_count} flashcards if requested." if flashcards else ""

        system_prompt = (
            "You are an advanced academic structuring AI.\n\n"
            "Generate a structured, exam-ready cheat sheet from the provided study material.\n\n"
            "The output must adapt based on:\n\n"
            "Revision Mode:\n"
            "- Quick 1-Page -> Highly compressed, ultra concise\n"
            "- Standard -> Balanced depth\n"
            "- Deep Revision -> Technically detailed and research-level\n\n"
            "Exam Mode:\n"
            "- Semester Exam -> Concept clarity + definitions + examples\n"
            "- Competitive Exam -> Shortcuts + tricks + high-yield facts\n"
            "- Interview Prep -> Concept depth + why/how explanations + edge cases\n\n"
            "-----------------------------------\n\n"
            "STRICT RULES:\n"
            "1. Maintain clean academic formatting.\n"
            "2. Remove redundant text.\n"
            "3. Fix corrupted characters and encoding issues.\n"
            "4. Normalize formulas and mathematical symbols.\n"
            "5. Avoid filler content.\n"
            "6. Do NOT hallucinate missing data.\n"
            "7. Use bullet points only.\n"
            "8. Keep sections ordered.\n"
            "9. Do not include citations or references.\n"
            "10. Return valid JSON only.\n\n"
            "-----------------------------------\n\n"
            "OUTPUT STRUCTURE:\n"
            "{\n"
            "  \"title\": \"\",\n"
            "  \"one_line_summary\": \"\",\n"
            "  \"definitions\": [ { \"term\": \"\", \"definition\": \"\" } ],\n"
            "  \"core_formulas\": [ { \"formula\": \"\", \"meaning\": \"\", \"when_to_use\": \"\" } ],\n"
            "  \"key_concepts\": [ { \"concept\": \"\", \"explanation\": \"\", \"importance\": \"\" } ],\n"
            "  \"diagrams\": [],\n"
            "  \"comparison_table\": [],\n"
            "  \"important_metrics\": [],\n"
            "  \"mistakes_to_avoid\": [],\n"
            "  \"shortcuts\": [],\n"
            "  \"quick_revision_points\": [],\n"
            "  \"flashcards\": [ { \"question\": \"\", \"answer\": \"\" } ]\n"
            "}\n\n"
            "-----------------------------------\n\n"
            f"MODE ADAPTATION LOGIC:\n{mode_instructions}\n"
            "-----------------------------------\n\n"
            f"{flashcard_rule}\n"
            "Now generate the cheat sheet from the following content:"
        )
        user_prompt = f"{context}"

        llm_start = time.time()
        # Direct invocation to avoid LangChain prompt template parsing issues with braces
        response = self._llm.invoke(
            [
                ("system", system_prompt),
                ("user", user_prompt),
            ]
        )
        llm_time = (time.time() - llm_start) * 1000
        
        response_text = _normalize_content(response.content)
        logger.info(
            "Cheatsheet generation timings: extraction=%dms, embedding=%dms, retrieval=%dms, llm=%dms, total=%dms",
            int(extraction_time), int(embedding_time), int(retrieval_time), int(llm_time),
            int(extraction_time + embedding_time + retrieval_time + llm_time)
        )
        logger.debug("LLM response preview: %s", _safe_for_log(response_text, limit=500))
        parsed = _safe_parse_json(response_text)
        if parsed is None:
            logger.error("Failed to parse JSON. Response preview: %s", _safe_for_log(response_text))
            parsed = await _repair_json_with_llm(response_text, flashcards)
        if parsed is None:
            original_words = _count_words(text)
            return _build_minimal_response(
                original_words=original_words,
                response_text=response_text,
                context=context,
                query=search_query,
                flashcards=flashcards,
                flashcard_count=clamped_count,
                processing_time_ms=int(extraction_time + embedding_time + retrieval_time + llm_time),
            )
        def _fmt_def(item: dict | str) -> str:
            if isinstance(item, dict): return f"**{item.get('term', '')}**: {item.get('definition', '')}"
            return str(item)
            
        def _fmt_formula(item: dict | str) -> str:
            if isinstance(item, dict):
                return f"**{item.get('formula', '')}**\n*Meaning:* {item.get('meaning', '')}\n*Use:* {item.get('when_to_use', '')}"
            return str(item)
        
        def _fmt_concept(item: dict | str) -> str:
            if isinstance(item, dict):
                return f"**{item.get('concept', '')}**: {item.get('explanation', '')}\n*Importance:* {item.get('importance', '')}"
            return str(item)

        raw_defs = parsed.get("definitions", [])
        definitions = [_fmt_def(item) for item in raw_defs] if isinstance(raw_defs, list) else []
        
        raw_formulas = parsed.get("core_formulas", [])
        core_formulas = [_fmt_formula(item) for item in raw_formulas] if isinstance(raw_formulas, list) else []
        
        raw_concepts = parsed.get("key_concepts", [])
        key_concepts = [_fmt_concept(item) for item in raw_concepts] if isinstance(raw_concepts, list) else []

        response = RagResponse(
            title=str(parsed.get("title", "Cheat Sheet")),
            one_line_summary=str(parsed.get("one_line_summary", "")),
            definitions=definitions,
            core_formulas=core_formulas,
            key_concepts=key_concepts,
            diagrams=_normalize_list(parsed.get("diagrams")),
            comparison_table=_normalize_list(parsed.get("comparison_table")),
            important_metrics=_normalize_list(parsed.get("important_metrics")),
            mistakes_to_avoid=_normalize_list(parsed.get("common_mistakes") or parsed.get("mistakes_to_avoid")),
            shortcuts=_normalize_list(parsed.get("shortcuts")),
            quick_revision_points=_normalize_list(parsed.get("quick_revision_points") or parsed.get("exam_revision_points")),
            flashcards=_normalize_flashcards(parsed.get("flashcards")) if flashcards else [],
            original_words=_count_words(text),
            compressed_words=0,
            raw_response=None,
            processing_time_ms=int(extraction_time + embedding_time + retrieval_time + llm_time),
        )
        try:
            from app.schemas.rag import Flashcard

            if flashcards and not response.flashcards:
                fallback = _fallback_flashcards(
                    response.definitions,
                    response.key_concepts,
                    max_count=clamped_count,
                )
                response.flashcards = [Flashcard(**item) for item in fallback]

            if flashcards and _flashcards_need_answers(response.flashcards):
                regenerated = await _generate_flashcards_with_llm(context, clamped_count)
                if regenerated:
                    response.flashcards = [Flashcard(**item) for item in regenerated]
                
                updated = _ensure_flashcard_answers(response.flashcards)
                response.flashcards = [Flashcard(**item) for item in updated]
        except Exception as exc:
            logger.error("Flashcard processing warning: %s", _safe_for_log(str(exc)))
            # Do not fail the whole request; proceed with whatever flashcards we have (or empty)

        response.compressed_words = _count_words_from_sections(response)
        return response


def _safe_parse_json(content: str) -> dict | None:
    try:
        # Strip markdown code blocks if present
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]  # Remove ```json
        elif content.startswith("```"):
            content = content[3:]  # Remove ```
        if content.endswith("```"):
            content = content[:-3]  # Remove trailing ```
        content = content.strip()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            extracted = _extract_json_object(content)
            if extracted is not None:
                return json.loads(extracted)
            raise
    except json.JSONDecodeError:
        return None


def _normalize_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    return json.dumps(content)


def _safe_for_log(text: str, limit: int = 1000) -> str:
    preview = text[:limit]
    return preview.encode("ascii", "backslashreplace").decode("ascii")


def _extract_json_object(content: str) -> str | None:
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if match:
        return match.group(0)
    return None


async def _repair_json_with_llm(
    response_text: str,
    flashcards: bool,
) -> dict | None:
    repair_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You must output ONLY valid JSON. Do not include markdown or explanations. "
                "Convert the given text into a JSON object with these keys (omit empty arrays): "
                "title, one_line_summary, definitions, core_formulas, key_concepts, diagrams, "
                "comparison_table, important_metrics, mistakes_to_avoid"
                + (", flashcards" if flashcards else "")
                + ".",
            ),
            (
                "user",
                "Text to convert:\n{text}",
            ),
        ]
    )
    try:
        repair_llm = ChatGroq(
            api_key=settings.groq_api_key_cheatsheet,
            model=settings.model_name,
            temperature=0,
            max_tokens=1200,
            model_kwargs={"response_format": {"type": "json_object"}},
        )
        repaired = repair_llm.invoke(
            repair_prompt.format_messages(
                text=_truncate_text(response_text, 4000),
            )
        )
        repaired_text = _normalize_content(repaired.content)
        return _safe_parse_json(repaired_text)
    except Exception as exc:
        logger.error("JSON repair failed: %s", _safe_for_log(str(exc)))
        return None


def _build_minimal_response(
    original_words: int,
    response_text: str,
    context: str,
    query: str,
    flashcards: bool,
    flashcard_count: int,
    processing_time_ms: int = 0,
) -> RagResponse:
    key_concepts = _fallback_key_concepts(context, max_items=8)
    response = RagResponse(
        title=_fallback_title(query),
        one_line_summary="",
        definitions=[],
        core_formulas=[],
        key_concepts=key_concepts,
        diagrams=[],
        comparison_table=[],
        important_metrics=[],
        mistakes_to_avoid=[],
        flashcards=[],
        original_words=original_words,
        compressed_words=0,
        raw_response=response_text,
        processing_time_ms=processing_time_ms,
    )
    if flashcards:
        response.flashcards = _fallback_flashcards([], response.key_concepts, max_count=flashcard_count)
    response.compressed_words = _count_words_from_sections(response)
    return response


def _fallback_title(query: str) -> str:
    cleaned = query.strip() if query else ""
    return cleaned[:80] if cleaned else "Cheat Sheet"


def _fallback_key_concepts(context: str, max_items: int) -> list[str]:
    lines = [line.strip() for line in context.splitlines() if line.strip()]
    seen: set[str] = set()
    concepts: list[str] = []
    for line in lines:
        if line in seen:
            continue
        seen.add(line)
        concepts.append(line)
        if len(concepts) >= max_items:
            break
    return concepts


def _truncate_text(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit]


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


def _fallback_flashcards(
    definitions: list[str],
    key_concepts: list[str],
    max_count: int,
) -> list[dict[str, str]]:
    flashcards: list[dict[str, str]] = []
    for item in definitions:
        if ":" in item:
            term, definition = item.split(":", 1)
            question = f"What is {term.strip()}?"
            answer = definition.strip()
        else:
            question = f"Explain: {item.strip()}"
            answer = ""
        flashcards.append({"question": question, "answer": answer})
        if len(flashcards) >= max_count:
            return flashcards

    for concept in key_concepts:
        question = f"Explain the concept: {concept.strip()}"
        flashcards.append({"question": question, "answer": ""})
        if len(flashcards) >= max_count:
            break
    return flashcards


def _flashcards_need_answers(flashcards: list[Any]) -> bool:
    if not flashcards:
        return True
    for card in flashcards:
        if isinstance(card, dict):
            answer = card.get("answer", "")
        else:
            answer = getattr(card, "answer", "")
        if not str(answer).strip():
            return True
    return False


async def _generate_flashcards_with_llm(
    context: str,
    count: int,
) -> list[dict[str, str]]:
    system_prompt = (
        "Return ONLY valid JSON with key 'flashcards'. Each flashcard must include "
        f"non-empty 'question' and 'answer'. Generate exactly {count} flashcards. "
        "Use only the provided context."
    )
    user_prompt = f"Context:\n{context}"

    try:
        llm = ChatGroq(
            api_key=settings.groq_api_key_cheatsheet,
            model=settings.model_name,
            temperature=0.2,
            max_tokens=800,
            model_kwargs={"response_format": {"type": "json_object"}},
        )
        response = llm.invoke(
            [
                ("system", system_prompt),
                ("user", user_prompt),
            ]
        )
        parsed = _safe_parse_json(_normalize_content(response.content))
        if not parsed:
            return []
        return _normalize_flashcards(parsed.get("flashcards"))
    except Exception as exc:
        logger.error("Flashcard regeneration failed: %s", _safe_for_log(str(exc)))
        return []


def _ensure_flashcard_answers(flashcards: list[Any]) -> list[dict[str, str]]:
    updated: list[dict[str, str]] = []
    for card in flashcards:
        if isinstance(card, dict):
            question = str(card.get("question", "")).strip()
            answer = str(card.get("answer", "")).strip()
        else:
            question = str(getattr(card, "question", "")).strip()
            answer = str(getattr(card, "answer", "")).strip()
        if question and not answer:
            answer = "Review the source material for this answer."
        if question:
            updated.append({"question": question, "answer": answer})
    return updated


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
        if isinstance(card, dict):
            flashcard_parts.extend([card.get("question", ""), card.get("answer", "")])
        else:
            flashcard_parts.extend([getattr(card, "question", ""), getattr(card, "answer", "")])
    parts.extend(flashcard_parts)
    return _count_words(" ".join(p for p in parts if p))
