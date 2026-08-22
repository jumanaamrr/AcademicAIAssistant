import os
import re
import shutil
import requests
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from rag.document_loader import load_document
from rag.text_splitter import split_documents
from rag.embeddings import get_embedding_model
from rag.vector_store import create_vector_store, load_vector_store
from rag.retriever import get_rag_chain

load_dotenv(override=True)

VECTOR_STORE_PATH = "faiss_index"

def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set.")
        
    # Dynamically find a valid chat model for the given key
    headers = {'Authorization': f'Bearer {api_key}'}
    try:
        r = requests.get('https://api.groq.com/openai/v1/models', headers=headers)
        if r.status_code == 200:
            models = [m['id'] for m in r.json().get('data', [])]
            # Filter out whisper, prompt guards
            chat_models = [m for m in models if 'whisper' not in m and 'guard' not in m]
            # Prefer standard models if available, otherwise pick the first valid one
            model_name = next((m for m in chat_models if 'qwen' in m or 'llama' in m or 'mixtral' in m), chat_models[0] if chat_models else "llama3-8b-8192")
        else:
            model_name = "llama-3.1-8b-instant"
    except Exception:
        model_name = "llama-3.1-8b-instant" # Fallback
    
    return ChatGroq(
        model=model_name,
        temperature=0,
        api_key=api_key,
    )

def initialize_rag():
    """Initialize the RAG system."""
    llm = get_llm()
    embedding_model = get_embedding_model()
    
    # Check if vector store exists
    if os.path.exists(VECTOR_STORE_PATH):
        vector_store = load_vector_store(VECTOR_STORE_PATH, embedding_model)
    else:
        # Try to load sample syllabus
        syllabus_path = os.getenv("SYLLABUS_PATH", "sample_syllabus.txt")
        
        if not os.path.exists(syllabus_path):
            raise FileNotFoundError(f"Syllabus file not found: {syllabus_path}")
        
        documents = load_document(syllabus_path)
        chunks = split_documents(documents)
        vector_store = create_vector_store(chunks, embedding_model, VECTOR_STORE_PATH)
    
    rag_chain, _ = get_rag_chain(vector_store, llm, k=3)
    return rag_chain

# Global variable to cache the RAG chain
_rag_chain = None

def ask_academic_rag(question: str) -> str:
    """Answer academic questions using the syllabus."""
    global _rag_chain
    
    try:
        if _rag_chain is None:
            _rag_chain = initialize_rag()
        
        answer = _rag_chain.invoke(question)
        
        # Remove <think>...</think> blocks from reasoning models
        answer = re.sub(r'<think>.*?</think>\s*', '', answer, flags=re.DOTALL)
        
        return answer.strip()
    except Exception as e:
        return f"Error: {str(e)}. Please make sure a syllabus is uploaded."

def update_rag_with_file(file_path: str):
    """Updates the FAISS index with a new syllabus file."""
    global _rag_chain
    
    embedding_model = get_embedding_model()
    
    # If the vector store already exists, delete it so we can create a fresh one
    if os.path.exists(VECTOR_STORE_PATH):
        shutil.rmtree(VECTOR_STORE_PATH)
        
    documents = load_document(file_path)
    chunks = split_documents(documents)
    
    # Create and save a new vector store
    create_vector_store(chunks, embedding_model, VECTOR_STORE_PATH)
    
    # Invalidate current RAG chain so it reloads on next question
    _rag_chain = None