import logging

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

logger = logging.getLogger(__name__)


def build_vector_store(documents: list[Document], embeddings: Embeddings) -> FAISS:
    """Build a FAISS vector store from documents with robust error handling."""
    if not documents:
        raise ValueError("Cannot build vector store from empty document list")
    
    logger.info(f"Building vector store from {len(documents)} documents")
    
    try:
        store = FAISS.from_documents(documents, embeddings)
        logger.info("Vector store created successfully")
        return store
    except Exception as exc:
        logger.error(f"Failed to build vector store: {exc}", exc_info=True)
        raise


def retrieve_chunks(store: FAISS, query: str, top_k: int) -> list[Document]:
    """Retrieve chunks with robust error handling."""
    if not query.strip():
        logger.warning("Query is empty")
        return []
    
    try:
        logger.debug(f"Retrieving {top_k} chunks for query: {query[:100]}")
        results = store.similarity_search(query, k=top_k)
        logger.info(f"Retrieved {len(results)} chunks")
        
        if results:
            for i, doc in enumerate(results[:3]):  # Log first 3
                logger.debug(f"  Chunk {i} (score unknown): {doc.page_content[:100]}...")
        
        return results
    except Exception as exc:
        logger.error(f"Failed to retrieve chunks: {exc}", exc_info=True)
        return []

