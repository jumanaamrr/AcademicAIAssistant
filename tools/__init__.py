from tools.gpa_calculator import calculate_gpa
from tools.study_scheduler import create_study_schedule
from tools.report_generator import generate_report

__all__ = [
    "calculate_gpa",
    "create_study_schedule",
    "generate_report",
    "ask_academic_rag",
    "update_rag_with_file",
]


def __getattr__(name):
    if name in {"ask_academic_rag", "update_rag_with_file"}:
        from tools.rag_tool import ask_academic_rag, update_rag_with_file

        return ask_academic_rag if name == "ask_academic_rag" else update_rag_with_file
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
