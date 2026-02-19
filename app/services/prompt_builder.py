from typing import Dict

SYSTEM_PROMPT = (
    "You are an expert academic assistant specialized in generating structured, "
    "exam-oriented cheat sheets. Focus on clarity, precision, and structured output. "
    "Do not hallucinate. Extract only from provided content. "
    "Use verbatim text from the material; do not paraphrase or reword."
)

USER_PROMPT_TEMPLATE = (
    "From the following study material:\n\n"
    "1. Extract Key Concepts\n"
    "2. Extract Definitions\n"
    "3. Extract Important Formulas\n"
    "4. Generate Quick Revision Points\n"
    "5. If flashcards=true, generate Q&A flashcards\n"
    "6. Adjust depth based on revision_mode\n"
    "7. Adjust format based on exam_mode\n\n"
    "Rules:\n"
    "- Use only exact wording from the material (verbatim).\n"
    "- Do not paraphrase, summarize, or add new terms.\n"
    "- If a field has no matching content, return an empty array.\n\n"
    "Return strictly in JSON format:\n\n"
    "{{\n"
    "  \"key_concepts\": [],\n"
    "  \"definitions\": [],\n"
    "  \"formulas\": [],\n"
    "  \"revision_points\": [],\n"
    "  \"flashcards\": []\n"
    "}}\n\n"
    "Material:\n"
    "{extracted_text_chunk}"
)


def build_user_prompt(extracted_text_chunk: str, options: Dict[str, str | bool]) -> str:
    header = (
        f"revision_mode={options['revision_mode']}, "
        f"exam_mode={options['exam_mode']}, "
        f"formula_only={options['formula_only']}, "
        f"flashcards={options['flashcards']}\n\n"
    )
    return header + USER_PROMPT_TEMPLATE.format(extracted_text_chunk=extracted_text_chunk)
