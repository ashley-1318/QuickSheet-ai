from pydantic import BaseModel


class Flashcard(BaseModel):
    question: str
    answer: str


class RagResponse(BaseModel):
    cheatsheet_id: str | None = None
    title: str
    one_line_summary: str
    definitions: list[str]
    core_formulas: list[str]
    key_concepts: list[str]
    diagrams: list[str]
    comparison_table: list[str]
    important_metrics: list[str]
    mistakes_to_avoid: list[str]
    shortcuts: list[str] = []
    quick_revision_points: list[str] = []
    flashcards: list[Flashcard]
    original_words: int
    compressed_words: int
    raw_response: str | None = None
    processing_time_ms: int | None = None
