from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[Document]:
    if not text.strip():
        raise ValueError("Document is empty after extraction.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = splitter.split_text(text)
    return [Document(page_content=chunk, metadata={"chunk": idx}) for idx, chunk in enumerate(chunks)]
