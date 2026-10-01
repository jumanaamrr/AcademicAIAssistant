import pytest

from tools.study_scheduler import create_study_schedule


def test_schedule_generation_returns_days_and_sessions():
    schedule = create_study_schedule(
        subjects=[
            {"name": "AI", "exam_date": "2026-12-15", "difficulty": "hard"},
            {"name": "Networks", "exam_date": "2026-12-20", "difficulty": "medium"},
        ],
        available_hours_per_day=4,
        start_date="2026-12-10",
    )

    assert len(schedule) >= 1
    first_day = schedule[0]
    assert first_day["date"] == "2026-12-10"
    assert "sessions" in first_day
    assert first_day["total_hours"] > 0
    subjects = {session["subject"] for session in first_day["sessions"]}
    assert "AI" in subjects


def test_harder_subject_gets_more_hours():
    schedule = create_study_schedule(
        subjects=[
            {"name": "AI", "exam_date": "2026-12-15", "difficulty": "hard"},
            {"name": "PE", "exam_date": "2026-12-15", "difficulty": "easy"},
        ],
        available_hours_per_day=4,
        start_date="2026-12-10",
    )

    sessions = {item["subject"]: item["hours"] for item in schedule[0]["sessions"]}
    assert sessions["AI"] > sessions["PE"]


def test_invalid_exam_date_raises():
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        create_study_schedule(
            subjects=[{"name": "AI", "exam_date": "15/12/2026", "difficulty": "hard"}],
            available_hours_per_day=4,
            start_date="2026-12-01",
        )


def test_invalid_start_date_raises():
    with pytest.raises(ValueError, match="start_date"):
        create_study_schedule(
            subjects=[{"name": "AI", "exam_date": "2026-12-15", "difficulty": "medium"}],
            available_hours_per_day=4,
            start_date="not-a-date",
        )


def test_empty_subjects_raises():
    with pytest.raises(ValueError, match="cannot be empty"):
        create_study_schedule(subjects=[], available_hours_per_day=4, start_date="2026-12-01")


def test_zero_hours_raises():
    with pytest.raises(ValueError, match="greater than zero"):
        create_study_schedule(
            subjects=[{"name": "AI", "exam_date": "2026-12-15", "difficulty": "easy"}],
            available_hours_per_day=0,
            start_date="2026-12-01",
        )
