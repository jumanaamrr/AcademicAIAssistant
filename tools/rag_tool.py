import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from rag.document_loader import load_document
from rag.text_splitter import split_documents
from rag.embeddings import get_embedding_model
from rag.vector_store import create_vector_store, load_vector_store
from rag.retriever import get_rag_chain


load_dotenv()

VECTOR_STORE_PATH = "faiss_index"


def initialize_rag():
    """Initialize the academic RAG system."""

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY is not set.")

    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
        api_key=api_key,
    )

    embedding_model = get_embedding_model()

    if os.path.exists(VECTOR_STORE_PATH):
        vector_store = load_vector_store(
            VECTOR_STORE_PATH,
            embedding_model,
        )
    else:
        syllabus_path = os.getenv(
            "SYLLABUS_PATH",
            "sample_syllabus.txt",
        )

        documents = load_document(syllabus_path)
        chunks = split_documents(documents)

        vector_store = create_vector_store(
            chunks,
            embedding_model,
            VECTOR_STORE_PATH,
        )

    rag_chain, _ = get_rag_chain(
        vector_store,
        llm,
        k=3,
    )

    return rag_chain


def ask_academic_rag(question: str) -> str:
    """Answer academic questions using the syllabus."""

    rag_chain = initialize_rag()

    return rag_chain.invoke(question)
