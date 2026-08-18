from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def split_documents(
    documents: List[Document],
    chunk_size: int = 800,
    chunk_overlap: int = 150
) -> List[Document]:
    """Splits full document text into smaller chunks for vector indexing."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    return text_splitter.split_documents(documents)
