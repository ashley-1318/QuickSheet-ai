from pydantic import BaseModel


class ChatAskRequest(BaseModel):
    cheatsheet_id: str
    question: str
    exam_mode: str = "Semester Exam"


class ChatAskResponse(BaseModel):
    answer: str
    retrieved_chunks: int
    processing_time_ms: int


class ChatMessage(BaseModel):
    id: str
    user_id: str
    cheatsheet_id: str
    role: str
    message: str
    created_at: str
