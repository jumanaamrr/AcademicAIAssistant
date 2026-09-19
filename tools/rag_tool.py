import os
import re
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
def _clean_answer(text: str) -> str:
    """Strip markdown bold/italic, LaTeX math, and em-dashes from LLM output."""
    # Remove **bold** and *italic*
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\1", text)
    # Remove __bold__ and _italic_
    text = re.sub(r"__(.+?)__", r"\1", text)
    text = re.sub(r"(?<!_)_(?!_)(.+?)(?<!_)_(?!_)", r"\1", text)
    # Remove $...$ LaTeX math (keep the content)
    text = re.sub(r"\$([^\$]+)\$", r"\1", text)
    # Remove em-dash and en-dash, replace with comma or space
    text = text.replace("—", ",").replace("–", "-")
    # Remove markdown headings
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    # Remove backticks
    text = text.replace("`", "")
    # Collapse multiple spaces
    text = re.sub(r" {2,}", " ", text)
    return text.strip()

def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set.")

    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        r = requests.get("https://api.groq.com/openai/v1/models", headers=headers)
        if r.status_code == 200:
            models = [m["id"] for m in r.json().get("data", [])]
            chat_models = [m for m in models if "whisper" not in m and "guard" not in m]
            model_name = next(
                (m for m in chat_models if "qwen" in m or "llama" in m or "mixtral" in m),
                chat_models[0] if chat_models else "llama-3.1-8b-instant",
            )
        else:
            model_name = "llama-3.1-8b-instant"
    except Exception:
        model_name = "llama-3.1-8b-instant"

    return ChatGroq(model=model_name, temperature=0.3, api_key=api_key)


# Global cache
_vector_store = None
_llm = None
_rag_chain = None
_retriever = None


def _get_vector_store():
    """Load or build the FAISS vector store."""
    global _vector_store
    if _vector_store is not None:
        return _vector_store

    embedding_model = get_embedding_model()

    if os.path.exists(VECTOR_STORE_PATH):
        _vector_store = load_vector_store(VECTOR_STORE_PATH, embedding_model)
    else:
        syllabus_path = os.getenv("SYLLABUS_PATH", "sample_syllabus.txt")
        if not os.path.exists(syllabus_path):
            raise FileNotFoundError(f"Syllabus file not found: {syllabus_path}")
        documents = load_document(syllabus_path)
        chunks = split_documents(documents)
        for chunk in chunks:
            chunk.metadata["course"] = "Sample"
        _vector_store = create_vector_store(chunks, embedding_model, VECTOR_STORE_PATH)

    return _vector_store


def initialize_rag():
    """Initialize the RAG chain (default, unfiltered)."""
    global _llm, _rag_chain

    if _rag_chain is not None:
        return _rag_chain

    _llm = get_llm()
    vector_store = _get_vector_store()
    _rag_chain, _ = get_rag_chain(vector_store, _llm, k=3)
    return _rag_chain


def _detect_course(question: str) -> str | None:
    """Extract a course code from the question.
    Requires either:
      - Letters + digits (e.g., CS101, AI301, MATH201)
      - OR an exact match against courses already in the index.
    """
    upper_q = question.upper()

    # Get all course names actually in the index
    known_courses = _list_uploaded_courses()

    # 1. Check if any known course name appears in the question
    for course in known_courses:
        if course.upper() in upper_q:
            return course

    # 2. Fall back to pattern: letters + digits (CS101, AI301, etc.)
    match = re.search(r"\b([A-Z]{2,5}[\s\-]?\d{2,4})\b", upper_q)
    if match:
        return match.group(1).replace(" ", "").replace("-", "")

    return None

def _list_uploaded_courses() -> list[str]:
    """List all course names currently in the FAISS index."""
    try:
        vector_store = _get_vector_store()
        course_names = set()
        for doc_id in vector_store.index_to_docstore_id.values():
            doc = vector_store.docstore.search(doc_id)
            if doc and "course" in doc.metadata:
                course_names.add(doc.metadata["course"])
        return sorted(course_names)
    except Exception:
        return []


def ask_academic_rag(question: str) -> str:
    """Answer using course-filtered retrieval when a course is detected."""
    global _llm

    try:
        vector_store = _get_vector_store()
        if _llm is None:
            _llm = get_llm()

        course = _detect_course(question)

        if course:
            # Filter by course metadata
            retriever = vector_store.as_retriever(
                search_kwargs={"k": 3, "filter": {"course": course}}
            )
            docs = retriever.invoke(question)

            # If nothing found for that course, fall back to unfiltered
            if not docs:
                all_courses = _list_uploaded_courses()
                return (
                    f"I don't have a syllabus for '{course}'. "
                    f"Available courses: {', '.join(all_courses) if all_courses else 'none'}."
                )

            # Build context
            context = "\n\n".join(d.page_content for d in docs)
            prompt = (
                f"Use the following syllabus context to answer the student's question. "
                f"Answer conversationally in a few sentences. Do not use markdown tables.\n\n"
                f"Context:\n{context}\n\n"
                f"Question: {question}\n\nAnswer:"
            )
            answer = _llm.invoke(prompt).content
        else:
            # No course mentioned — check how many courses exist
            all_courses = _list_uploaded_courses()

            if len(all_courses) > 1:
                # Ambiguous — ask user which course
                return (
                    f"Which course are you asking about? "
                    f"I have syllabi for: {', '.join(all_courses)}."
                )

            # Only one course — answer directly
            rag_chain = initialize_rag()
            answer = rag_chain.invoke(question)

        answer = re.sub(r"<think>.*?</think>\s*", "", answer, flags=re.DOTALL)
        return _clean_answer(answer)

    except Exception as e:
        return f"Error: {str(e)}. Please make sure a syllabus is uploaded."


def update_rag_with_file(file_path: str, course_name: str = "Unknown"):
    """Adds a new syllabus to the existing FAISS index with course metadata."""
    global _rag_chain, _vector_store

    embedding_model = get_embedding_model()
    documents = load_document(file_path)
    chunks = split_documents(documents)
    course_key = course_name.strip().upper()
    for chunk in chunks:
        chunk.metadata["course"] = course_key
        chunk.metadata["source"] = file_path

    if os.path.exists(VECTOR_STORE_PATH):
        vector_store = load_vector_store(VECTOR_STORE_PATH, embedding_model)
        vector_store.add_documents(chunks)
        vector_store.save_local(VECTOR_STORE_PATH)
        _vector_store = vector_store
    else:
        _vector_store = create_vector_store(chunks, embedding_model, VECTOR_STORE_PATH)

    _rag_chain = None