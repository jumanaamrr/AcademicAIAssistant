from tools.rag_tool import _get_vector_store

vs = _get_vector_store()
docs = [vs.docstore.search(i) for i in vs.index_to_docstore_id.values()]

# Test 1: Do MATH101 chunks with GRADING exist?
math_chunks = [d for d in docs if d.metadata.get("course") == "MATH101"]
print("Total MATH101 chunks:", len(math_chunks))

grading_chunks = [d for d in math_chunks if "GRADING" in d.page_content.upper()]
print("MATH101 chunks containing 'GRADING':", len(grading_chunks))

for i, m in enumerate(grading_chunks[:3], 1):
    print(f"--- GRADING chunk {i} ---")
    print(m.page_content[:300])
    print()

# Test 2: Does retrieval find it?
print("=" * 40)
print("Retrieval test: 'grading policy'")
r = vs.as_retriever(search_kwargs={"k": 3, "filter": {"course": "MATH101"}})
retrieved = r.invoke("grading policy")
for i, d in enumerate(retrieved, 1):
    print(f"--- Retrieved {i} ---")
    print(d.page_content[:200])
    print()

# Test 3: Direct RAG
print("=" * 40)
print("Direct RAG test")
from tools.rag_tool import ask_academic_rag
print(ask_academic_rag("What is the grading policy in MATH101?"))