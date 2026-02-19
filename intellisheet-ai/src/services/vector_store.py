from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings


def build_vector_store(documents: list[Document], embeddings: Embeddings) -> FAISS:
    return FAISS.from_documents(documents, embeddings)


def retrieve_chunks(store: FAISS, query: str, top_k: int) -> list[Document]:
    return store.similarity_search(query, k=top_k)
