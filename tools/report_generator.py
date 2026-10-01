"""
Report Generator Tool
=====================
Generates a formatted HTML academic summary report that combines a student's
GPA results and study schedule into a single downloadable document.

This is the "Automated Actions" component of the multi-agent pipeline:
  Data Retrieval → Data Processing → Summarization → Report Generation (automated output)
"""

import html as html_lib
import os
from datetime import datetime
from typing import List, Dict, Optional


REPORTS_DIR = "reports"


def generate_report(
    student_name: str,
    gpa: Optional[float] = None,
    courses: Optional[List[Dict]] = None,
    schedule: Optional[List[Dict]] = None,
    notes: Optional[str] = None,
) -> Dict:
    """
    Generate an HTML academic summary report.

    Args:
        student_name: The student's name for the report header.
        gpa: Computed GPA value (0.0 – 4.0).
        courses: List of course dicts with keys: name, grade, credits, quality_points.
        schedule: List of day dicts with keys: date, total_hours, sessions.
        notes: Optional free-text notes or AI-generated summary.

    Returns:
        Dict with keys:
          - html: Full HTML string of the report
          - file_path: Absolute path to the saved .html file
          - filename: Basename of the saved file
          - generated_at: ISO timestamp
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)

    timestamp = datetime.now()
    generated_at = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    filename = f"academic_report_{timestamp.strftime('%Y%m%d_%H%M%S')}.html"
    file_path = os.path.join(REPORTS_DIR, filename)

    html = _build_html(
        student_name=student_name,
        gpa=gpa,
        courses=courses or [],
        schedule=schedule or [],
        notes=notes or "",
        generated_at=generated_at,
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)

    return {
        "html": html,
        "file_path": os.path.abspath(file_path),
        "filename": filename,
        "generated_at": generated_at,
    }


def _gpa_badge_color(gpa: float) -> str:
    if gpa >= 3.7:
        return "#22c55e"   # green
    elif gpa >= 3.0:
        return "#3b82f6"   # blue
    elif gpa >= 2.0:
        return "#f59e0b"   # amber
    else:
        return "#ef4444"   # red


def _gpa_label(gpa: float) -> str:
    if gpa >= 3.7:
        return "Excellent Standing"
    elif gpa >= 3.0:
        return "Good Standing"
    elif gpa >= 2.0:
        return "Satisfactory"
    else:
        return "Academic Warning"


def _esc(value) -> str:
    if value is None or value == "":
        return "—"
    return html_lib.escape(str(value))


def _difficulty_color(difficulty: str) -> str:
    d = difficulty.lower()
    if d == "hard":
        return "#ef4444"
    elif d == "medium":
        return "#f59e0b"
    return "#22c55e"


def _build_html(
    student_name: str,
    gpa: Optional[float],
    courses: List[Dict],
    schedule: List[Dict],
    notes: str,
    generated_at: str,
) -> str:
    # --- GPA Section ---
    if gpa is not None:
        badge_color = _gpa_badge_color(gpa)
        standing = _gpa_label(gpa)
        gpa_section = f"""
        <section class="section">
            <h2>GPA Summary</h2>
            <div class="gpa-badge" style="background:{badge_color};">
                <span class="gpa-value">{gpa:.2f}</span>
                <span class="gpa-label">/ 4.00 — {standing}</span>
            </div>
        """
        if courses:
            rows = ""
            for c in courses:
                rows += f"""
                <tr>
                    <td>{_esc(c.get("name"))}</td>
                    <td>{_esc(c.get("credits"))}</td>
                    <td><strong>{_esc(c.get("grade"))}</strong></td>
                    <td>{_esc(c.get("quality_points"))}</td>
                </tr>"""
            gpa_section += f"""
            <table>
                <thead>
                    <tr>
                        <th>Course</th><th>Credits</th><th>Grade</th><th>Quality Points</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>"""
        gpa_section += "</section>"
    else:
        gpa_section = ""

    # --- Study Schedule Section ---
    if schedule:
        days_html = ""
        for day in schedule:
            date_str = day.get("date", "")
            total_hours = day.get("total_hours", 0)
            sessions = day.get("sessions", [])
            session_rows = ""
            for s in sessions:
                diff = s.get("difficulty", "medium")
                color = _difficulty_color(diff)
                session_rows += f"""
                <tr>
                    <td>{_esc(s.get("subject"))}</td>
                    <td>{_esc(s.get("hours"))}h</td>
                    <td><span class="badge" style="background:{color};">{_esc(diff.capitalize())}</span></td>
                    <td>{_esc(s.get("exam_date"))}</td>
                </tr>"""
            days_html += f"""
            <div class="day-card">
                <div class="day-header">
                    <strong>{_esc(date_str)}</strong>
                    <span>{_esc(total_hours)}h total</span>
                </div>
                <table>
                    <thead>
                        <tr><th>Subject</th><th>Hours</th><th>Difficulty</th><th>Exam Date</th></tr>
                    </thead>
                    <tbody>{session_rows}</tbody>
                </table>
            </div>"""
        schedule_section = f"""
        <section class="section">
            <h2>Study Schedule</h2>
            {days_html}
        </section>"""
    else:
        schedule_section = ""

    # --- Notes Section ---
    if notes:
        notes_section = f"""
        <section class="section">
            <h2>AI-Generated Notes</h2>
            <div class="notes-box">{_esc(notes)}</div>
        </section>"""
    else:
        notes_section = ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Academic Report — {_esc(student_name)}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            background: #f1f5f9;
            color: #1e293b;
            padding: 2rem;
        }}
        .report-wrapper {{
            max-width: 860px;
            margin: 0 auto;
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 4px 24px rgba(0,0,0,.10);
            overflow: hidden;
        }}
        .report-header {{
            background: linear-gradient(135deg, #1764a3 0%, #0ea5e9 100%);
            color: #fff;
            padding: 2.5rem 2rem 2rem;
        }}
        .report-header h1 {{ font-size: 1.8rem; font-weight: 700; }}
        .report-header .meta {{ margin-top: .5rem; font-size: .9rem; opacity: .85; }}
        .section {{
            padding: 2rem;
            border-bottom: 1px solid #e2e8f0;
        }}
        .section:last-child {{ border-bottom: none; }}
        .section h2 {{
            font-size: 1.2rem;
            font-weight: 600;
            color: #1764a3;
            margin-bottom: 1.25rem;
        }}
        .gpa-badge {{
            display: inline-flex;
            align-items: baseline;
            gap: .75rem;
            color: #fff;
            border-radius: 10px;
            padding: .8rem 1.5rem;
            margin-bottom: 1.5rem;
        }}
        .gpa-value {{ font-size: 2.5rem; font-weight: 800; }}
        .gpa-label {{ font-size: 1rem; opacity: .9; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: .9rem;
            margin-top: .5rem;
        }}
        th {{
            background: #f8fafc;
            color: #64748b;
            font-weight: 600;
            text-align: left;
            padding: .6rem 1rem;
            border-bottom: 2px solid #e2e8f0;
        }}
        td {{
            padding: .6rem 1rem;
            border-bottom: 1px solid #f1f5f9;
        }}
        tr:last-child td {{ border-bottom: none; }}
        .day-card {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            margin-bottom: 1rem;
            overflow: hidden;
        }}
        .day-header {{
            display: flex;
            justify-content: space-between;
            padding: .75rem 1rem;
            background: #e2e8f0;
            font-size: .9rem;
            font-weight: 600;
        }}
        .badge {{
            color: #fff;
            font-size: .75rem;
            padding: .2rem .6rem;
            border-radius: 999px;
            font-weight: 600;
        }}
        .notes-box {{
            background: #f0f9ff;
            border-left: 4px solid #0ea5e9;
            padding: 1rem 1.25rem;
            border-radius: 0 8px 8px 0;
            font-size: .95rem;
            line-height: 1.6;
            white-space: pre-wrap;
        }}
        .report-footer {{
            text-align: center;
            padding: 1.25rem;
            font-size: .8rem;
            color: #94a3b8;
            background: #f8fafc;
        }}
        @media print {{
            body {{ padding: 0; background: #fff; }}
            .report-wrapper {{ box-shadow: none; }}
        }}
    </style>
</head>
<body>
    <div class="report-wrapper">
        <div class="report-header">
            <h1>Academic Summary Report</h1>
            <div class="meta">
                Student: <strong>{_esc(student_name)}</strong> &nbsp;|&nbsp;
                Generated: {_esc(generated_at)}
            </div>
        </div>

        {gpa_section}
        {schedule_section}
        {notes_section}

        <div class="report-footer">
            Generated by Academic AI Assistant &mdash; {generated_at}
        </div>
    </div>
</body>
</html>
"""
