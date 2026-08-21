from typing import List, Dict
from datetime import date


def create_study_schedule(
    subjects: List[Dict],
    available_hours_per_day: float,
    start_date: str | None = None,
) -> List[Dict]:
    

    if not subjects:
        raise ValueError("Subjects list cannot be empty.")

    if available_hours_per_day <= 0:
        raise ValueError("Available study hours must be greater than zero.")

    if start_date is None:
        start = date.today()
    else:
        try:
            start = date.fromisoformat(start_date)
        except ValueError:
            raise ValueError(
                "start_date must be in YYYY-MM-DD format."
            )

    normalized_subjects = []

    for subject in subjects:
        if "name" not in subject or "exam_date" not in subject:
            raise ValueError(
                "Each subject must contain 'name' and 'exam_date'."
            )

        name = str(subject["name"]).strip()

        if not name:
            raise ValueError("Subject name cannot be empty.")

        try:
            exam_date = date.fromisoformat(subject["exam_date"])
        except ValueError:
            raise ValueError(
                f"Invalid exam date for {name}. "
                "Use YYYY-MM-DD format."
            )

        if exam_date < start:
            raise ValueError(
                f"Exam date for {name} cannot be before the start date."
            )

        difficulty = str(
            subject.get("difficulty", "medium")
        ).strip().lower()

        if difficulty not in {"easy", "medium", "hard"}:
            raise ValueError(
                f"Invalid difficulty for {name}. "
                "Use easy, medium, or hard."
            )

        difficulty_weight = {
            "easy": 1,
            "medium": 2,
            "hard": 3,
        }[difficulty]

        normalized_subjects.append({
            "name": name,
            "exam_date": exam_date,
            "difficulty": difficulty,
            "weight": difficulty_weight,
        })

    last_exam = max(
        subject["exam_date"]
        for subject in normalized_subjects
    )

    total_days = (last_exam - start).days + 1

    schedule = []

    for day_offset in range(total_days):
        current_day = start.fromordinal(
            start.toordinal() + day_offset
        )

        available_subjects = [
            subject
            for subject in normalized_subjects
            if current_day <= subject["exam_date"]
        ]

        if not available_subjects:
            continue

        # Calculate priority for each subject.
        # Subjects with earlier exams and higher difficulty
        # receive more study time.
        priorities = []

        for subject in available_subjects:
            days_until_exam = (
                subject["exam_date"] - current_day
            ).days

            urgency = 1 / (days_until_exam + 1)

            priority = (
                subject["weight"] * 0.6
                + urgency * 10 * 0.4
            )

            priorities.append(
                (subject, priority)
            )

        total_priority = sum(
            priority
            for _, priority in priorities
        )

        daily_plan = []

        for subject, priority in priorities:
            allocated_hours = (
                available_hours_per_day
                * priority
                / total_priority
            )

            allocated_hours = round(
                allocated_hours,
                1
            )

            if allocated_hours <= 0:
                continue

            daily_plan.append({
                "subject": subject["name"],
                "hours": allocated_hours,
                "difficulty": subject["difficulty"],
                "exam_date": subject["exam_date"].isoformat(),
            })

        # Remove tiny allocations caused by rounding.
        daily_plan = [
            item
            for item in daily_plan
            if item["hours"] > 0
        ]

        schedule.append({
            "date": current_day.isoformat(),
            "total_hours": round(
                sum(item["hours"] for item in daily_plan),
                1
            ),
            "sessions": daily_plan,
        })

    return schedule