import os
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

def create_vector_store(documents: List[Document], embedding_model, save_path: str = "faiss_index") -> FAISS:
    """Builds a FAISS vector store from document chunks and saves it locally."""
    vector_store = FAISS.from_documents(documents, embedding_model)
    vector_store.save_local(save_path)
    return vector_store

def load_vector_store(save_path: str, embedding_model) -> FAISS:
    """Loads an existing FAISS index from local disk."""
    if not os.path.exists(save_path):
        raise FileNotFoundError(f"FAISS index path '{save_path}' does not exist.")
    return FAISS.load_local(
        save_path,
        embedding_model,
        allow_dangerous_deserialization=True
    )