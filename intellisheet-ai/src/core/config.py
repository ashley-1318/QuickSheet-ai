from pydantic import BaseSettings, SecretStr

class Settings(BaseSettings):
    GROQ_API_KEY: SecretStr
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 900
    CHUNK_OVERLAP: int = 150
    TOP_K: int = 5
    MAX_FILES: int = 4

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()