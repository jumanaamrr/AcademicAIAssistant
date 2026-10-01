# Evaluation Report

Date: 2026-10-01  
Project: Academic AI Assistant  
Command: `python -m pytest tests/ -v`

## Summary

| Suite | Tests | Result |
|---|---|---|
| `tests/test_gpa_calculator.py` | 8 | Passed |
| `tests/test_study_scheduler.py` | 6 | Passed |
| `tests/test_api.py` | 9 | Passed |
| **Total** | **23** | **23 passed** |

Runtime: 15.74s on Python 3.12.10 / pytest 9.1.1 (Windows).

One non-blocking warning: `langchain-community` deprecation from `rag/document_loader.py`.

## GPA calculator

| Case | Expected | Observed |
|---|---|---|
| AI A/3, Networks B+/3, Algorithms A-/2 | 3.66 | Pass |
| Single A course | 4.00 | Pass |
| F grade | 0.00 | Pass |
| A + F, equal credits | 2.00 | Pass |
| Empty list / invalid grade / missing fields / zero credits | `ValueError` | Pass |

Accuracy for the documented demonstration mix is exact after rounding to two decimal places (`29.3 / 8 = 3.6625 → 3.66`).

## Study scheduler

| Case | Expected | Observed |
|---|---|---|
| Two subjects with future exam dates | Non-empty schedule starting on the requested date | Pass |
| Hard vs easy, same exam date | Hard subject receives more hours | Pass |
| Invalid exam date / start date | `ValueError` | Pass |
| Empty subjects / zero hours | `ValueError` | Pass |

Priority ordering uses difficulty weight and exam urgency, which is the intended scheduling policy.

## API integration

Chat and syllabus ingest are mocked so the suite does not require Groq or embedding downloads:

| Endpoint | Check |
|---|---|
| `GET /` | Status message |
| `GET /health` | `healthy` |
| `POST /chat/message` | Mocked agent answer + session id |
| `POST /syllabus/upload` | Success payload; RAG write mocked |
| `GET /syllabus/status` | Index flag present |
| `POST /gpa/calculate` | GPA 3.5 for A and B, 3 credits each |
| `POST /study-schedule/generate` | Schedule starts on `2026-12-10` |
| `POST /report/generate` | HTML contains student name; file downloadable |
| `POST /report/generate` empty name | HTTP 400 |

## Gaps still outside this suite

- Live Groq RAG quality still depends on `test_agent.py` and a valid `GROQ_API_KEY`.
- Frontend Export Report, Chat, Upload, GPA, and Study Plan pages need a running API (`uvicorn main:app --port 8001`) for end-to-end manual checks.
- Email sending is not implemented; the automated action is HTML report generation and download, which matches the academic-assistant scope.
