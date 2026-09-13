"""
Tests for AI Summary and Red-Flag Safety Rules
Verifies:
- POST /api/ai/summary
- GET /api/summary/{session_id}
- PUT /api/summary/{id}
- Deterministic fallback summary with strict schema
- Red flag alert on chest pain + breathlessness
- Question schema retrieval
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_questions_endpoint():
    res = client.get("/api/questions/chest-pain")
    assert res.status_code == 200
    questions = res.json()
    assert len(questions) >= 6
    ids = [q["id"] for q in questions]
    assert "cp_onset" in ids
    assert "cp_duration" in ids
    assert "cp_severity" in ids
    assert "cp_radiation" in ids
    assert "cp_breathlessness" in ids
    assert "cp_past_cardiac" in ids


def test_ai_summary_and_red_flag_alert():
    # 1. Create session
    sess_res = client.post("/api/sessions", json={"demo_id": "PT-TEST-ALERT", "language": "en"})
    assert sess_res.status_code == 201
    session_id = sess_res.json()["session_id"]

    # 2. Add chest pain + breathlessness answers (Triggers Red-Flag)
    client.post(f"/api/sessions/{session_id}/answers", json={"question_id": "cp_onset", "answer_text": "Suddenly today"})
    client.post(f"/api/sessions/{session_id}/answers", json={"question_id": "cp_duration", "answer_text": "Several hours continuous"})
    client.post(f"/api/sessions/{session_id}/answers", json={"question_id": "cp_severity", "answer_text": "8"})
    client.post(f"/api/sessions/{session_id}/answers", json={"question_id": "cp_radiation", "answer_text": "Yes, radiates to arm/jaw"})
    client.post(f"/api/sessions/{session_id}/answers", json={"question_id": "cp_breathlessness", "answer_text": "Yes"})

    # 3. Call AI summary
    sum_res = client.post("/api/ai/summary", json={"session_id": session_id})
    assert sum_res.status_code == 200
    data = sum_res.json()
    content = data["content_json"]

    # Verify strict schema fields
    assert "chief_complaint" in content
    assert "hpi" in content
    assert "past_history" in content
    assert "allergies" in content
    assert "red_flags_noted" in content

    # Verify Red Flag trigger
    assert data["has_red_flag_alert"] is True
    assert "PRIORITY TRIAGE ALERT" in data["red_flag_message"]

    # 4. Fetch summary via GET /api/summary/{session_id}
    get_res = client.get(f"/api/summary/{session_id}")
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert get_data["has_red_flag_alert"] is True

    # 5. Doctor edits and confirms via PUT /api/summary/{id}
    summary_id = data["id"]
    put_res = client.put(f"/api/summary/{summary_id}", json={
        "chief_complaint": "Acute severe substernal chest pain with dyspnea",
        "status": "doctor_confirmed"
    })
    assert put_res.status_code == 200
    put_data = put_res.json()
    assert put_data["status"] == "doctor_confirmed"
    assert put_data["content_json"]["chief_complaint"] == "Acute severe substernal chest pain with dyspnea"


def test_normal_case_no_red_flag():
    # Session without breathlessness (Normal / Non-critical case)
    sess_res = client.post("/api/sessions", json={"demo_id": "PT-TEST-NORMAL", "language": "en"})
    session_id = sess_res.json()["session_id"]

    client.post(f"/api/sessions/{session_id}/answers", json={"question_id": "cp_onset", "answer_text": "1 to 2 days ago"})
    client.post(f"/api/sessions/{session_id}/answers", json={"question_id": "cp_breathlessness", "answer_text": "No"})

    sum_res = client.post("/api/ai/summary", json={"session_id": session_id})
    assert sum_res.status_code == 200
    data = sum_res.json()
    assert data["has_red_flag_alert"] is False
    assert data["red_flag_message"] is None
