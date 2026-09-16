import os
import re
import sys
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()

results = []

def run_check(check_id, name, func):
    try:
        print(f"\n--- Running Check {check_id}: {name} ---")
        func()
        print(f"[PASS] Check {check_id} Passed")
        results.append((check_id, name, True, None))
    except Exception as e:
        print(f"[FAIL] Check {check_id} Failed: {e}")
        results.append((check_id, name, False, str(e)))

# Check 1: Imports
def check_imports():
    import agent.agent
    import main
    import tools.rag_tool
    import tools.gpa_calculator
    import tools.study_scheduler
    print("All modules imported successfully.")

# Check 2: Environment
def check_env():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise ValueError("GROQ_API_KEY is not set in environment or .env file.")
    if len(key) >= 8:
        masked_key = key[:4] + "*" * (len(key) - 8) + key[-4:]
    else:
        masked_key = "****"
    print(f"GROQ_API_KEY found: {masked_key}")

# Check 3: Agent cache
def check_agent_cache():
    from agent.agent import create_agent
    a1 = create_agent()
    a2 = create_agent()
    assert a1 is a2, "create_agent() did not return the cached instance."
    print("Agent cache successfully verified (a1 is a2).")

# Check 4: RAG single-turn
def check_rag_single():
    from agent.agent import run_agent
    res = run_agent("What percentage is the final exam?", session_id="verify_rag_1")
    print(f"RAG response: {res}")
    assert "40" in res or "40%" in res, f"Expected '40' in response, got: {res}"

# Check 5: Memory turn 1 -> 2 -> 3
def check_memory():
    from agent.agent import run_agent
    session_id = "verify_mem_1"
    
    t1 = run_agent("What percentage is the final exam?", session_id=session_id)
    print(f"Turn 1 response:\n{t1}")
    assert "40" in t1 or "40%" in t1, f"Turn 1 expected '40', got: {t1}"

    t2 = run_agent("And what about the midterm?", session_id=session_id)
    print(f"Turn 2 response:\n{t2}")
    assert "30" in t2 or "30%" in t2, f"Turn 2 expected '30', got: {t2}"

    t3 = run_agent("Remind me what I asked first.", session_id=session_id)
    print(f"Turn 3 response:\n{t3}")
    assert "final" in t3.lower() or "exam" in t3.lower() or "40" in t3, f"Turn 3 expected mention of final exam, got: {t3}"

# Check 6: Session isolation
def check_isolation():
    from agent.agent import run_agent
    res = run_agent("Remind me what I asked first.", session_id="verify_isolated_999")
    print(f"Isolated session response: {res}")
    assert "final exam" not in res.lower() or "haven't asked" in res.lower() or "no previous" in res.lower() or "first question" in res.lower(), f"Unexpected context leak in isolated session: {res}"

# Check 7: GPA tool
def check_gpa():
    from agent.agent import run_agent
    res = run_agent("Calculate my GPA: AI A 3 credits, Networks B+ 3 credits, Algorithms A- 2 credits.", session_id="verify_gpa_1")
    print(f"GPA response: {res}")
    numbers = re.findall(r"\b\d+\.\d+\b", res)
    found = any(3.0 <= float(n) <= 4.0 for n in numbers)
    assert found, f"Expected GPA value between 3.0 and 4.0, got: {res}"

# Check 8: Study scheduler
def check_scheduler():
    from agent.agent import run_agent
    res = run_agent("Create a study schedule for AI (hard, exam 2026-08-28) and Networks (medium, exam 2026-08-30). I can study 4 hours per day.", session_id="verify_sched_1")
    print(f"Scheduler response: {res}")
    assert "AI" in res and "Networks" in res, f"Expected AI and Networks in response: {res}"
    assert any(w in res.lower() for w in ["hour", "2026", "august", "day", "schedule", "plan"]), f"Expected hours/date/plan in response: {res}"

# Check 9: FAISS index growth
def check_faiss_growth():
    from tools.rag_tool import update_rag_with_file, VECTOR_STORE_PATH
    pkl_file = os.path.join(VECTOR_STORE_PATH, "index.pkl")
    size_before = os.path.getsize(pkl_file) if os.path.exists(pkl_file) else 0
    print(f"FAISS index size before update: {size_before} bytes")
    
    update_rag_with_file("sample_syllabus.txt")
    
    size_after = os.path.getsize(pkl_file)
    print(f"FAISS index size after update: {size_after} bytes")
    assert size_after > 0 and size_after >= size_before, f"Index size invalid: before={size_before}, after={size_after}"

# Check 10: FastAPI smoke test
def check_fastapi():
    from fastapi.testclient import TestClient
    from main import app
    
    client = TestClient(app)
    
    r_health = client.get("/health")
    print(f"GET /health: {r_health.status_code} - {r_health.json()}")
    assert r_health.status_code == 200
    assert r_health.json() == {"status": "healthy"}
    
    r_chat = client.post("/chat/message", json={"question": "What is the final exam worth?", "session_id": "verify_api_1"})
    print(f"POST /chat/message: {r_chat.status_code} - {r_chat.json()}")
    assert r_chat.status_code == 200
    ans = r_chat.json().get("answer", "")
    assert "40" in ans or "40%" in ans, f"Expected 40 in chat answer, got: {ans}"
    
    r_status = client.get("/syllabus/status")
    print(f"GET /syllabus/status: {r_status.status_code} - {r_status.json()}")
    assert r_status.status_code == 200
    assert r_status.json().get("syllabus_loaded") is True

def main_suite():
    run_check(1, "Imports", check_imports)
    run_check(2, "Environment", check_env)
    run_check(3, "Agent cache", check_agent_cache)
    run_check(4, "RAG single-turn", check_rag_single)
    run_check(5, "Memory (3 turns)", check_memory)
    run_check(6, "Session isolation", check_isolation)
    run_check(7, "GPA tool", check_gpa)
    run_check(8, "Study scheduler", check_scheduler)
    run_check(9, "FAISS index growth", check_faiss_growth)
    run_check(10, "FastAPI endpoints", check_fastapi)

    print("\n" + "=" * 40)
    print(" VERIFICATION SUMMARY")
    print("=" * 40)
    passed_count = sum(1 for _, _, passed, _ in results if passed)
    for check_id, name, passed, err in results:
        status_text = "[PASS]" if passed else "[FAIL]"
        err_msg = f" ({err})" if err else ""
        print(f"{status_text} {check_id}. {name}{err_msg}")
    print("=" * 40)
    print(f"{passed_count} / {len(results)} passed")
    print("=" * 40)

if __name__ == "__main__":
    main_suite()
