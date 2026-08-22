from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Friendly Guardrail Prompt
GROUNDED_SYLLABUS_PROMPT = """
You are a friendly and helpful AI University Course Assistant. Use the provided document context below to answer the user's question.

Context:
{context}

Question: {question}

Instructions for a user-friendly answer:
1. Answer the question naturally and directly. DO NOT use phrases like "Based on the provided context" or mention that you are reading from an excerpt. Just give the answer.
2. Keep it conversational, warm, and easy to read. Avoid robotic disclaimers about fragmented text.
3. If the answer is clearly in the context, provide it clearly.
4. If the exact information is completely missing, politely inform the user that it isn't covered in the uploaded document and suggest they reach out to their TA or Course Instructor.
5. If the answer is directly found within the context, give a clear, direct answer.
6. If the policy or information is missing from the syllabus context, DO NOT guess or invent information. Explicitly state that the information is missing from the syllabus and advise the student to contact their Teaching Assistant (TA) or Course Instructor.
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