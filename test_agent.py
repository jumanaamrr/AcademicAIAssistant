from agent.agent import run_agent


questions = [
    """
    Calculate my GPA for:
    AI: A, 3 credits
    Networks: B+, 3 credits
    Algorithms: A-, 2 credits
    """,

    """
    Create a study schedule for:
    AI - hard - exam on 2026-08-28
    Networks - medium - exam on 2026-08-30
    I can study 4 hours per day.
    """,

    "What percentage is the final exam?",

    "What are the office hours for the AI course?",

    "What happens if I submit an assignment more than 48 hours late?",
]


for i, question in enumerate(questions, 1):
    print("\n" + "=" * 60)
    print(f"TEST {i}")
    print("=" * 60)
    print(f"Question:\n{question.strip()}")

    try:
        result = run_agent(question)
        print(f"\nAgent response:\n{result}")

    except Exception as e:
        print(f"\nERROR:\n{type(e).__name__}: {e}")


def test_memory():
    session = "test_memory_session_" + str(int(__import__("time").time()))
    print("\n" + "=" * 60)
    print("MEMORY TEST")
    print("=" * 60)

    q1 = "What percentage is the final exam?"
    q2 = "And what about the midterm?"
    q3 = "Remind me what I asked first."

    print(f"\nTurn 1: {q1}\n-> {run_agent(q1, session_id=session)}")
    print(f"\nTurn 2: {q2}\n-> {run_agent(q2, session_id=session)}")
    print(f"\nTurn 3: {q3}\n-> {run_agent(q3, session_id=session)}")


if __name__ == "__main__":
    test_memory()