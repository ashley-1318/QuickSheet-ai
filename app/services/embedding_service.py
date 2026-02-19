import logging
from langchain_huggingface import HuggingFaceEmbeddings

from app.config import settings

logger = logging.getLogger(__name__)

# Global singleton instance
_embedding_service_instance = None


class EmbeddingService:
    """Singleton embedding service that loads model once at startup."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        if self._initialized:
            return
        
        try:
            logger.info(f"Initializing embeddings with model: {settings.rag_embedding_model}")
            self._embeddings = HuggingFaceEmbeddings(
                model_name=settings.rag_embedding_model,
                encode_kwargs={"normalize_embeddings": True},
                model_kwargs={"device": "cpu"},
            )
            logger.info("Embeddings initialized successfully (singleton)")
            self._initialized = True
        except Exception as exc:
            logger.error(f"Failed to initialize embeddings: {exc}", exc_info=True)
            raise

    @property
    def embeddings(self) -> HuggingFaceEmbeddings:
        return self._embeddings


