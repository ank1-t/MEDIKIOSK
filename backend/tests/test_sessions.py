"""
Backend API Unit and Integration Tests for Member 1 Deliverables:
- GET /health
- POST /api/sessions
- POST /api/sessions/{id}/answers
- GET /api/sessions/{id}
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Verify GET /health returns status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_session_lifecycle_with_answers():
    """
    Test complete flow:
    1. Create a session
    2. Save 3 fake answers
    3. Fetch session and assert all 3 answers are returned
    """
    # 1. Create a session
    create_resp = client.post("/api/sessions", json={"demo_id": "DEMO-PT-001", "language": "en"})
    assert create_resp.status_code == 201
    session_data = create_resp.json()
    assert "id" in session_data
    session_id = session_data["id"]
    assert session_data["status"] == "in_progress"

    # 2. Save 3 fake answers
    answers_to_submit = [
        {"question_id": "q_chief_complaint", "answer_text": "Chest pain radiating to left arm", "source": "voice"},
        {"question_id": "q_duration", "answer_text": "2 days", "source": "touch"},
        {"question_id": "q_severity", "answer_text": "8/10 severe squeezing pressure", "source": "touch"},
    ]

    for ans in answers_to_submit:
        ans_resp = client.post(f"/api/sessions/{session_id}/answers", json=ans)
        assert ans_resp.status_code == 201
        ans_data = ans_resp.json()
        assert ans_data["question_id"] == ans["question_id"]
        assert ans_data["answer_text"] == ans["answer_text"]

    # 3. Fetch the session and verify all 3 answers are present
    get_resp = client.get(f"/api/sessions/{session_id}")
    assert get_resp.status_code == 200
    retrieved_data = get_resp.json()
    assert retrieved_data["id"] == session_id
    assert len(retrieved_data["answers"]) == 3

    saved_questions = [a["question_id"] for a in retrieved_data["answers"]]
    assert "q_chief_complaint" in saved_questions
    assert "q_duration" in saved_questions
    assert "q_severity" in saved_questions


def test_get_nonexistent_session():
    """Verify 404 is returned when querying unknown session."""
    response = client.get("/api/sessions/sess_nonexistent_99999")
    assert response.status_code == 404
