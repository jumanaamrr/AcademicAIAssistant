from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "University Assistant" in response.json()["message"]


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_chat_message():
    with patch("main.run_agent", return_value="The final exam is 35 percent."):
        response = client.post(
            "/chat/message",
            json={"question": "What is the final exam worth?", "session_id": "test-session"},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["session_id"] == "test-session"
    assert "35 percent" in body["answer"]


def test_syllabus_upload():
    with patch("tools.rag_tool.update_rag_with_file") as mock_update:
        response = client.post(
            "/syllabus/upload",
            data={"course_name": "CS301"},
            files={"file": ("sample_syllabus.txt", b"CS301 Artificial Intelligence", "text/plain")},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["course_name"] == "CS301"
    mock_update.assert_called_once()


def test_syllabus_status():
    response = client.get("/syllabus/status")
    assert response.status_code == 200
    assert "syllabus_loaded" in response.json()
    assert "message" in response.json()


def test_gpa_calculate():
    response = client.post(
        "/gpa/calculate",
        json={
            "courses": [
                {"name": "AI", "credits": 3, "grade": "A"},
                {"name": "Networks", "credits": 3, "grade": "B"},
            ]
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["gpa"] == 3.5
    assert body["total_credits"] == 3 + 3
    assert len(body["courses"]) == 2


def test_study_schedule_generate():
    response = client.post(
        "/study-schedule/generate",
        json={
            "subjects": [
                {"name": "AI", "exam_date": "2026-12-20", "difficulty": "Hard"},
                {"name": "Networks", "exam_date": "2026-12-22", "difficulty": "Medium"},
            ],
            "available_hours_per_day": 4,
            "start_date": "2026-12-10",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total_days"] >= 1
    assert len(body["schedule"]) >= 1
    assert body["schedule"][0]["date"] == "2026-12-10"


def test_report_generate_and_download(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.report_generator.REPORTS_DIR", str(tmp_path))
    monkeypatch.setattr("main.REPORTS_DIR", str(tmp_path))

    response = client.post(
        "/report/generate",
        json={
            "student_name": "Alex Johnson",
            "gpa": 3.66,
            "courses": [
                {"name": "AI", "grade": "A", "credits": 3, "quality_points": 12.0}
            ],
            "schedule": [
                {
                    "date": "2026-12-10",
                    "total_hours": 4,
                    "sessions": [
                        {
                            "subject": "AI",
                            "hours": 4,
                            "difficulty": "hard",
                            "exam_date": "2026-12-15",
                        }
                    ],
                }
            ],
            "notes": "Stay consistent with daily review.",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "Alex Johnson" in body["html"]
    assert body["filename"].endswith(".html")

    download = client.get(body["download_url"])
    assert download.status_code == 200
    assert "Academic Summary Report" in download.text


def test_report_generate_requires_student_name():
    response = client.post("/report/generate", json={"student_name": "   "})
    assert response.status_code == 400
