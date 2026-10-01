import pytest

from tools.gpa_calculator import calculate_gpa


def test_normal_weighted_gpa():
    gpa = calculate_gpa([
        {"name": "AI", "grade": "A", "credits": 3},
        {"name": "Networks", "grade": "B+", "credits": 3},
        {"name": "Algorithms", "grade": "A-", "credits": 2},
    ])
    assert gpa == 3.66


def test_single_course_gpa():
    assert calculate_gpa([{"grade": "A", "credits": 4}]) == 4.0


def test_failing_grade_is_zero_points():
    assert calculate_gpa([{"grade": "F", "credits": 3}]) == 0.0


def test_failing_grade_lowers_weighted_gpa():
    gpa = calculate_gpa([
        {"grade": "A", "credits": 3},
        {"grade": "F", "credits": 3},
    ])
    assert gpa == 2.0


def test_empty_course_list_raises():
    with pytest.raises(ValueError, match="cannot be empty"):
        calculate_gpa([])


def test_invalid_grade_raises():
    with pytest.raises(ValueError, match="Invalid grade"):
        calculate_gpa([{"grade": "Z", "credits": 3}])


def test_missing_fields_raises():
    with pytest.raises(ValueError, match="grade"):
        calculate_gpa([{"name": "AI", "credits": 3}])


def test_zero_credits_raises():
    with pytest.raises(ValueError, match="greater than zero"):
        calculate_gpa([{"grade": "A", "credits": 0}])
