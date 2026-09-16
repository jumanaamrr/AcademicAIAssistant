# Academic AI Assistant

Academic AI Assistant is an intelligent university companion that assists students with academic tasks using a Retrieval-Augmented Generation (RAG) pipeline over uploaded course syllabi, automated GPA calculation, personalized study plan scheduling, and a LangGraph ReAct agent with persistent conversational memory.

## Features

- **RAG over Syllabi**: Upload course syllabi (PDF, DOCX, TXT) and retrieve accurate answers grounded in academic course policies, grading breakdowns, office hours, and deadlines.
- **GPA Calculator**: Calculate semester and cumulative GPA dynamically from letter grades or grade points and credit hours.
- **Study Scheduler**: Generate structured, day-by-day study schedules balanced across subjects, difficulty levels, and upcoming exam dates.
- **LangGraph ReAct Agent**: Coordinates tools dynamically using reasoning and action steps powered by Groq LLMs.
- **Persistent Conversational Memory**: Retains multi-turn conversation context per session using LangGraph's `MemorySaver` checkpointer and thread IDs for contextual follow-up questions.

---

## Setup

```bash
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env         # then edit .env with your GROQ_API_KEY
```

### Run Backend

```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### Run Frontend

Open `frontend/index.html` in a web browser, or serve it using Python's built-in HTTP server:

```bash
cd frontend
python -m http.server 5500
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Root status message |
| `GET` | `/health` | Service health status check |
| `POST` | `/chat/message` | Send a question to the agent with `session_id` for stateful conversation |
| `POST` | `/syllabus/upload` | Upload a syllabus file (PDF, DOCX, TXT) and append to vector store |
| `GET` | `/syllabus/status` | Check if a syllabus FAISS index is loaded |
| `POST` | `/gpa/calculate` | Compute semester GPA from course grades and credit hours |
| `POST` | `/study-schedule/generate` | Generate a balanced study schedule based on exams and availability |

---

## Example Questions & Demonstrations

### 1. RAG over Syllabus
> "What percentage is the final exam in the AI course?"
> "What happens if I submit an assignment 48 hours late?"

### 2. GPA Calculation
> "Calculate my GPA for: AI (A, 3 credits), Networks (B+, 3 credits), Algorithms (A-, 2 credits)."

### 3. Study Scheduling
> "Create a study schedule for AI (hard, exam on 2026-08-28) and Networks (medium, exam on 2026-08-30) with 4 available hours per day."

### 4. Conversational Memory & Multi-turn Follow-ups
> **Turn 1:** "What percentage is the final exam?"
> **Turn 2:** "And what about the midterm?"
> **Turn 3:** "Remind me what I asked first."

---

## Project Structure

```
AcademicAIAssistant/
├── .env.example
├── README.md
├── requirements.txt
├── sample_syllabus.txt
├── main.py
├── test_agent.py
├── agent/
│   ├── __init__.py
│   └── agent.py
├── backend/
│   ├── __init__.py
│   └── main.py
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── chat.js
│   │   ├── gpa.js
│   │   ├── study-plan.js
│   │   └── upload.js
│   └── pages/
│       ├── chat.html
│       ├── gpa.html
│       ├── study-plan.html
│       └── upload.html
├── rag/
│   ├── document_loader.py
│   ├── embeddings.py
│   ├── retriever.py
│   ├── text_splitter.py
│   └── vector_store.py
└── tools/
    ├── __init__.py
    ├── gpa_calculator.py
    ├── rag_tool.py
    └── study_scheduler.py
```
