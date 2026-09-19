import logging
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from tools.rag_tool import ask_academic_rag
from tools.gpa_calculator import calculate_gpa
from tools.study_scheduler import create_study_schedule


load_dotenv()

_agent = None


@tool(
    description="Calculate a student's GPA from a list of courses. "
                "Each course must contain a letter grade and credit hours."
)
def gpa_calculator(courses: list) -> float:
    return calculate_gpa(courses)


@tool(
    description="Create a study schedule based on subjects, exam dates, "
                "difficulty, available study hours, and start date."
)
def study_scheduler(
    subjects: list,
    available_hours_per_day: float,
    start_date: str | None = None,
) -> list:
    return create_study_schedule(
        subjects=subjects,
        available_hours_per_day=available_hours_per_day,
        start_date=start_date,
    )


@tool(
    description="Answer questions about university courses, syllabi, "
                "course policies, assessments, attendance, topics, "
                "office hours, and other information contained in "
                "academic documents. Pass the user's question verbatim, "
                "including any course name they mention (e.g., CS101)."
)
def academic_rag(question: str) -> str:
    """Answer academic questions using the uploaded syllabus or academic documents."""
    return ask_academic_rag(question)


SYSTEM_PROMPT = """
You are an Academic AI Assistant helping university students.

You have three tools:

1. gpa_calculator — for GPA calculations.
2. study_scheduler — for study plans and exam prep schedules.
3. academic_rag — for questions about courses, syllabi, policies,
   grading, exams, attendance, office hours, and topics.

Important rules:

- When the user asks about a course's content, policy, or numbers,
  ALWAYS call academic_rag. Do NOT answer from general knowledge.
- When calling academic_rag, pass the user's question VERBATIM,
  including any course name they mention (e.g., "CS101", "AI301").
  Do not paraphrase or omit the course name.
- If the user asks a vague question that could apply to multiple
  courses (e.g., "what's the final exam worth?") and they haven't
  named a course, ask them which course they mean before calling
  academic_rag. Example reply: "Which course — CS101 or CS201?"
- If the user asks a follow-up with pronouns ("and the midterm?",
  "what about it?"), rewrite it into a standalone question that
  includes the course name from earlier in the conversation, then
  call academic_rag.
- Do not invent syllabus information.
- Keep answers clear and conversational.
- ALWAYS write in plain text. Never use **bold**, *italic*, markdown
  headers, tables, bullet points, LaTeX ($...$), or em-dashes (—).
  Write in natural sentences with normal punctuation.
"""


def create_agent():
    global _agent

    if _agent is not None:
        return _agent

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set. Add it to your .env file.")

    model_name = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    llm = ChatGroq(
        model=model_name,
        temperature=0,
        api_key=api_key,
    )

    tools = [gpa_calculator, study_scheduler, academic_rag]

    memory = MemorySaver()

    _agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=SYSTEM_PROMPT,
        checkpointer=memory,
    )

    return _agent


import re  # add at the top if not already there

def _clean_final_answer(text: str) -> str:
    """Strip markdown from the agent's final response."""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)          # **bold**
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\1", text)  # *italic*
    text = re.sub(r"__(.+?)__", r"\1", text)              # __bold__
    text = re.sub(r"\$([^\$]+)\$", r"\1", text)           # $math$
    text = text.replace("—", ",").replace("–", "-")       # dashes
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE) # headings
    text = text.replace("`", "")                          # backticks
    text = re.sub(r" {2,}", " ", text)                    # extra spaces
    return text.strip()


def run_agent(user_input: str, session_id: str = "default") -> str:
    global _agent
    agent = create_agent()

    config = {"configurable": {"thread_id": session_id}}

    try:
        response = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config,
        )
        raw = response["messages"][-1].content
        return _clean_final_answer(raw)   # ← apply cleanup

    except Exception as e:
        err_msg = str(e).lower()
        if "rate_limit" in err_msg or "413" in err_msg or "tpm" in err_msg or "tokens per minute" in err_msg:
            logging.warning("Rate limit. Falling back to llama-3.1-8b-instant.")
            os.environ["GROQ_MODEL"] = "llama-3.1-8b-instant"
            _agent = None
            fallback_agent = create_agent()
            response = fallback_agent.invoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config=config,
            )
            raw = response["messages"][-1].content
            return _clean_final_answer(raw)
        raise e