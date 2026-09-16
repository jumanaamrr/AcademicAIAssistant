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

# Module-level cache so agent and memory persist across requests
_agent = None


# Tool 1: GPA Calculator

@tool(
    description="Calculate a student's GPA from a list of courses. "
                "Each course must contain a letter grade and credit hours."
)
def gpa_calculator(courses: list) -> float:
    return calculate_gpa(courses)



# Tool 2: Study Scheduler

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


# Tool 3: Academic RAG
@tool(
    description="Answer questions about university courses, syllabi, "
                "course policies, assessments, attendance, topics, "
                "office hours, and other information contained in "
                "academic documents."
)
def academic_rag(question: str) -> str:
    """Answer academic questions using the uploaded syllabus or academic documents."""
    return ask_academic_rag(question)


# Agent configuration

SYSTEM_PROMPT = """
You are an Academic AI Assistant.

Your job is to help university students with academic tasks.

You have access to the following tools:

1. gpa_calculator
   Use this whenever the student asks you to calculate,
   estimate, or recalculate GPA.

2. study_scheduler
   Use this whenever the student asks for a study plan,
   study schedule, or exam preparation schedule.

3. academic_rag
   Use this whenever the student asks about information that
   should come from a syllabus or academic document, such as
   course policies, assessment percentages, attendance,
   office hours, topics, or late submission rules.

Important rules:

- Use tools when a tool can perform the requested task.
- Do not manually calculate GPA when the GPA calculator can
  do it.
- Do not invent academic policies or syllabus information.
- Keep answers clear and useful for university students.
- When the user asks a follow-up question that references prior context (e.g., 'what about the midterm?', 'and the other one?'), rewrite the query into a standalone question before calling academic_rag or any tool.
- You have access to the full conversation history for this session. Use it to resolve pronouns, ellipses, and implicit references.
- Always consult the academic_rag tool to answer questions about course policies, syllabus content, exams, or grading weights.
"""


def create_agent():
    global _agent

    if _agent is not None:
        return _agent

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not set. "
            "Add it to your .env file."
        )

    model_name = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    llm = ChatGroq(
        model=model_name,
        temperature=0,
        api_key=api_key,
    )

    tools = [
        gpa_calculator,
        study_scheduler,
        academic_rag,
    ]

    memory = MemorySaver()

    # Note: On older LangGraph versions (< 0.2.44), use prompt=SYSTEM_PROMPT instead of state_modifier
    _agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=SYSTEM_PROMPT,
        checkpointer=memory,
    )

    return _agent


def run_agent(user_input: str, session_id: str = "default") -> str:
    global _agent
    agent = create_agent()

    config = {"configurable": {"thread_id": session_id}}

    try:
        response = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": user_input,
                    }
                ]
            },
            config=config,
        )
        return response["messages"][-1].content
    except Exception as e:
        err_msg = str(e).lower()
        if "rate_limit" in err_msg or "413" in err_msg or "tpm" in err_msg or "tokens per minute" in err_msg:
            logging.warning("openai/gpt-oss-120b rate limit exceeded. Falling back to llama-3.1-8b-instant.")
            os.environ["GROQ_MODEL"] = "llama-3.1-8b-instant"
            _agent = None
            fallback_agent = create_agent()
            response = fallback_agent.invoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": user_input,
                        }
                    ]
                },
                config=config,
            )
            return response["messages"][-1].content
        raise e