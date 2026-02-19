from langchain_community.embeddings import HuggingFaceEmbeddings

from src.core.config import settings


class EmbeddingService:
    def __init__(self) -> None:
        self._embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)

    @property
    def embeddings(self) -> HuggingFaceEmbeddings:
        return self._embeddings
