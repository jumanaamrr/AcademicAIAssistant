import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from tools.rag_tool import ask_academic_rag
from tools.gpa_calculator import calculate_gpa
from tools.study_scheduler import create_study_schedule


load_dotenv()


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
    start_date: str | None = None,) -> list:
   
    return create_study_schedule(subjects=subjects,available_hours_per_day=available_hours_per_day,start_date=start_date,)

#Tool 3:Academic RAG
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
"""


def create_agent():
  
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not set. "
            "Add it to your .env file."
        )

    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
        api_key=api_key,
    )

    tools = [gpa_calculator,study_scheduler,academic_rag,
]

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=SYSTEM_PROMPT,
    )

    return agent


def run_agent(user_input: str) -> str:
 
    agent = create_agent()

    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_input,
                }
            ]
        }
    )

    return response["messages"][-1].content