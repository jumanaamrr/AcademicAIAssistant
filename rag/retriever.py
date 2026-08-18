from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Strict Guardrail Prompt
GROUNDED_SYLLABUS_PROMPT = """
You are an AI University Course Assistant. Use ONLY the provided syllabus context below to answer the user's question.

Context:
{context}

Question: {question}

Guardrail Rules:
1. If the answer is directly found within the context, give a clear, direct answer.
2. If the policy or information is missing from the syllabus context, DO NOT guess or invent information. Explicitly state that the information is missing from the syllabus and advise the student to contact their Teaching Assistant (TA) or Course Instructor.

Answer:
"""


def get_rag_chain(vector_store, llm, k: int = 3):
    """Connects FAISS retriever and LLM into a grounded RAG pipeline."""
    retriever = vector_store.as_retriever(search_kwargs={"k": k})
    prompt = ChatPromptTemplate.from_template(GROUNDED_SYLLABUS_PROMPT)

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
    )
    return rag_chain, retriever