from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    groq_api_key_cheatsheet: str = Field(..., env="GROQ_API_KEY_CHEATSHEET")
    groq_api_key_chat: str = Field(..., env="GROQ_API_KEY_CHAT")
    google_client_id: str | None = Field(default=None, env="GOOGLE_CLIENT_ID")
    supabase_url: str | None = Field(default=None, env="SUPABASE_URL")
    supabase_service_role_key: str | None = Field(
        default=None, env="SUPABASE_SERVICE_ROLE_KEY"
    )
    allow_dev_auth: bool = Field(default=True, env="ALLOW_DEV_AUTH")
    dev_user_id: str = Field(default="dev-user-test", env="DEV_USER_ID")
    max_file_size_mb: int = 10
    max_pdf_pages: int = 20
    max_tokens_per_chunk: int = 3500
    model_name: str = "llama-3.1-8b-instant"
    llm_temperature: float = 0.2
    llm_max_tokens: int = 1100  # Reduced from 2048 for faster generation
    llm_timeout_seconds: int = 30
    
    # Optimized RAG parameters
    rag_chunk_size: int = 500  # Reduced from 900
    rag_chunk_overlap: int = 75  # Reduced from 150
    rag_top_k: int = 3  # Reduced from 5
    rag_max_files: int = 4
    rag_embedding_model: str = "sentence-transformers/paraphrase-MiniLM-L3-v2"
    
    # Fast mode parameters
    fast_mode_chunk_size: int = 400
    fast_mode_chunk_overlap: int = 50
    fast_mode_top_k: int = 2
    fast_mode_max_tokens: int = 800

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        protected_namespaces=(),
    )


settings = Settings()
