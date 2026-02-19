import logging

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[Document]:
    """Split text into chunks using RecursiveCharacterTextSplitter with error handling."""
    if not text.strip():
        logger.error("Document is empty after extraction")
        raise ValueError("Document is empty after extraction.")

    logger.info(
        f"Chunking text: {len(text)} chars with chunk_size={chunk_size}, overlap={chunk_overlap}"
    )
    
    try:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        chunks = splitter.split_text(text)
        logger.info(f"Created {len(chunks)} chunks")
        
        if chunks:
            logger.debug(f"First chunk ({len(chunks[0])} chars): {chunks[0][:100]}...")
            logger.debug(f"Last chunk ({len(chunks[-1])} chars): {chunks[-1][:100]}...")
        
        documents = [Document(page_content=chunk, metadata={"chunk": idx}) for idx, chunk in enumerate(chunks)]
        return documents
    except Exception as exc:
        logger.error(f"Failed to chunk text: {exc}", exc_info=True)
        raise

