from pydantic import BaseModel


class Flashcard(BaseModel):
    question: str
    answer: str


class RagResponse(BaseModel):
    title: str
    one_line_summary: str
    definitions: list[str]
    core_formulas: list[str]
    key_concepts: list[str]
    diagrams: list[str]
    comparison_table: list[str]
    important_metrics: list[str]
    mistakes_to_avoid: list[str]
    flashcards: list[Flashcard]
    original_words: int
    compressed_words: int
    raw_response: str | None = None
