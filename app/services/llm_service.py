from __future__ import annotations

import importlib
import json
import logging
import re
from typing import Any, Dict, List

from app.config import settings

logger = logging.getLogger(__name__)


class LlmServiceError(Exception):
    pass


class LlmService:
    def __init__(self) -> None:
        try:
            groq_module = importlib.import_module("groq")
            Groq = getattr(groq_module, "Groq")
        except (ImportError, AttributeError) as exc:
            raise LlmServiceError(
                "Missing dependency: groq. Install it with 'pip install groq'."
            ) from exc
        self.client = Groq(api_key=settings.groq_api_key_cheatsheet)

    def _extract_json(self, content: str) -> Dict[str, Any]:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if not match:
            raise LlmServiceError("LLM response did not contain JSON")
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise LlmServiceError("LLM response contained invalid JSON") from exc

    def generate_cheatsheet(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        for attempt in range(2):
            try:
                response = self.client.chat.completions.create(
                    messages=messages,
                    model=settings.model_name,
                    temperature=settings.llm_temperature,
                    max_tokens=settings.llm_max_tokens,
                    timeout=settings.llm_timeout_seconds,
                )
                content = response.choices[0].message.content or ""
                return self._extract_json(content)
            except Exception as exc:
                logger.exception("Groq request failed (attempt %s)", attempt + 1)
                if attempt == 1:
                    raise LlmServiceError("Groq request failed") from exc
        raise LlmServiceError("Groq request failed")
