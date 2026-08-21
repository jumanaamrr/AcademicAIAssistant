from typing import List, Dict


GRADE_POINTS = {
    "A": 4.0,
    "A-": 3.7,
    "B+": 3.3,
    "B": 3.0,
    "B-": 2.7,
    "C+": 2.3,
    "C": 2.0,
    "C-": 1.7,
    "D+": 1.3,
    "D": 1.0,
    "F": 0.0,
}


def calculate_gpa(courses: List[Dict]) -> float:
    """
    Calculate weighted GPA on a 4.0 scale.

    Each course must contain:
        - grade: letter grade such as A, B+, C-
        - credits: number of credit hours
    """

    if not courses:
        raise ValueError("Course list cannot be empty.")

    total_quality_points = 0.0
    total_credits = 0.0

    for course in courses:
        if "grade" not in course or "credits" not in course:
            raise ValueError(
                "Each course must contain 'grade' and 'credits'."
            )

        grade = str(course["grade"]).strip().upper()
        credits = course["credits"]

        if grade not in GRADE_POINTS:
            raise ValueError(f"Invalid grade: {grade}")

        try:
            credits = float(credits)
        except (TypeError, ValueError):
            raise ValueError("Credits must be a number.")

        if credits <= 0:
            raise ValueError("Credits must be greater than zero.")

        total_quality_points += GRADE_POINTS[grade] * credits
        total_credits += credits

    return round(total_quality_points / total_credits, 2)