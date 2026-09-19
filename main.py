import os
import shutil
from typing import List, Optional, Union

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.agent import run_agent
from tools.rag_tool import ask_academic_rag

load_dotenv(override=True)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== MODELS =====

class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

class Course(BaseModel):
    name: str
    credits: float
    grade: Union[str, float]

class GPARequest(BaseModel):
    courses: List[Course]

class Subject(BaseModel):
    name: str
    exam_date: str
    difficulty: str

class StudyRequest(BaseModel):
    subjects: List[Subject]
    available_hours_per_day: float
    start_date: Optional[str] = None

# ===== HELPERS =====

LETTER_TO_POINTS = {
    "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0,
    "B-": 2.7, "C+": 2.3, "C": 2.0, "C-": 1.7,
    "D+": 1.3, "D": 1.0, "F": 0.0
}

POINTS_TO_LETTER = {v: k for k, v in LETTER_TO_POINTS.items()}

def get_grade_points(grade: Union[str, float]) -> float:
    if isinstance(grade, (int, float)):
        return float(grade)
    grade_str = str(grade).strip().upper()
    if grade_str in LETTER_TO_POINTS:
        return LETTER_TO_POINTS[grade_str]
    try:
        return float(grade_str)
    except ValueError:
        return 0.0

# ===== ENDPOINTS =====

@app.get("/")
def root():
    return {"message": "University Assistant API"}

@app.get("/health")
def health():
    return {"status": "healthy"}

# CHAT
@app.post("/chat/message")
async def chat(request: ChatRequest):
    session_id = request.session_id or "default"
    try:
        answer = run_agent(request.question, session_id=session_id)
        return {"answer": answer, "session_id": session_id}
    except Exception as e:
        return {"answer": f"Error: {str(e)}", "session_id": session_id}

# SYLLABUS
@app.post("/syllabus/upload")
async def upload(file: UploadFile, course_name: str = Form(...)):
    try:
        from tools.rag_tool import update_rag_with_file

        os.makedirs("uploaded_syllabi", exist_ok=True)
        file_path = os.path.join("uploaded_syllabi", f"{course_name}_{file.filename}")

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # ✅ PASS course_name so chunks get tagged
        update_rag_with_file(file_path, course_name=course_name)

        return {
            "success": True,
            "message": f"Syllabus '{course_name}' uploaded successfully!",
            "course_name": course_name
        }
    except Exception as e:
        return {"success": False, "message": str(e), "course_name": course_name}

@app.get("/syllabus/status")
def syllabus_status():
    index_exists = os.path.exists("faiss_index")
    return {
        "syllabus_loaded": index_exists,
        "message": "Syllabus loaded" if index_exists else "No syllabus loaded"
    }

# GPA
@app.post("/gpa/calculate")
def calculate_gpa_endpoint(request: GPARequest):
    total_points = 0.0
    total_credits = 0.0
    course_details = []
    for c in request.courses:
        points = get_grade_points(c.grade)
        total_points += points * c.credits
        total_credits += c.credits
        letter = POINTS_TO_LETTER.get(points, str(c.grade))
        course_details.append({
            "name": c.name,
            "grade": letter,
            "credits": c.credits,
            "quality_points": round(points * c.credits, 2)
        })
    gpa = total_points / total_credits if total_credits > 0 else 0.0
    return {
        "gpa": round(gpa, 2),
        "total_credits": total_credits,
        "total_quality_points": round(total_points, 2),
        "courses": course_details
    }

# STUDY SCHEDULE
@app.post("/study-schedule/generate")
def generate_schedule_endpoint(request: StudyRequest):
    from datetime import datetime, timedelta

    if not request.subjects:
        return {"schedule": [], "total_days": 0}

    start = (
        datetime.strptime(request.start_date, "%Y-%m-%d")
        if request.start_date
        else datetime.now()
    )
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)

    last_exam = max(
        datetime.strptime(s.exam_date, "%Y-%m-%d") for s in request.subjects
    )
    total_days = (last_exam - start).days

    topics_cycle = [
        "Study new topics",
        "Review previous topics",
        "Practice questions and revision",
    ]

    schedule = []
    for i in range(min(total_days, 14)):
        current_date = start + timedelta(days=i)
        active_subjects = [
            s for s in request.subjects
            if datetime.strptime(s.exam_date, "%Y-%m-%d") > current_date
        ]
        if not active_subjects:
            continue
        hours_each = round(request.available_hours_per_day / len(active_subjects), 1)
        sessions = [
            {
                "subject": s.name,
                "hours": hours_each,
                "difficulty": s.difficulty,
                "exam_date": s.exam_date,
                "topic": topics_cycle[i % 3],
            }
            for s in active_subjects
        ]
        schedule.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "formatted_date": current_date.strftime("%a, %b %d"),
            "total_hours": request.available_hours_per_day,
            "sessions": sessions,
        })

    return {"schedule": schedule, "total_days": total_days}