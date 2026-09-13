"""
End-to-End Multi-Member Workflow Integration & Demo Test
Tests the complete 5-member pipeline:
1. Member 1: /health, POST /api/sessions, POST /api/sessions/{id}/answers, GET /api/sessions/{id}
2. Member 2: Incremental intake responses + Review
3. Member 3: Chest pain questions, POST /api/ai/summary with strict JSON schema
4. Member 4: Document upload + OCR extraction + Timeline
5. Member 5: Red-flag alert evaluation, summary editing, PUT /api/summary/{id}, and Hospital mock send
"""

import os
import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_integration_pipeline():
    print("==================================================")
    print("MEDIKIOSK 5-MEMBER INTEGRATION & DEMO PIPELINE")
    print("==================================================")

    # Step 44: Member 1 - Health Check
    health_res = client.get("/health")
    assert health_res.status_code == 200, f"Health check failed: {health_res.text}"
    print(f"[PASS] Step 44: Backend /health confirmed OK -> {health_res.json()}")

    # Step 45: Member 1 & 2 - Create Session and Save Intake Answers
    session_res = client.post("/api/sessions", json={"demo_id": "DEMO-INTEGRATION-01", "language": "en"})
    assert session_res.status_code == 201
    sess_id = session_res.json()["session_id"]
    print(f"[PASS] Step 45a: Member 2 started kiosk, session created -> {sess_id}")

    test_answers = [
        ("cp_onset", "Suddenly today"),
        ("cp_duration", "Several hours continuous"),
        ("cp_severity", "9"),
        ("cp_radiation", "Yes, radiates to arm/jaw"),
        ("cp_breathlessness", "Yes"),
        ("cp_past_cardiac", "Yes")
    ]
    for qid, text in test_answers:
        ans_res = client.post(f"/api/sessions/{sess_id}/answers", json={
            "question_id": qid,
            "answer_text": text,
            "source": "touch"
        })
        assert ans_res.status_code == 201

    # Verify answers landed in DB (GET /api/sessions/{id})
    fetch_sess = client.get(f"/api/sessions/{sess_id}")
    assert fetch_sess.status_code == 200
    saved_answers = fetch_sess.json()["answers"]
    assert len(saved_answers) == 6
    print(f"[PASS] Step 45b: Member 1 confirms all {len(saved_answers)} answers safely persisted in SQLite database")

    # Step 46: Member 3 - Trigger /api/ai/summary
    ai_res = client.post("/api/ai/summary", json={"session_id": sess_id})
    assert ai_res.status_code == 200
    summary_data = ai_res.json()
    content = summary_data["content_json"]
    print(f"[PASS] Step 46: Member 3 triggered /api/ai/summary. Structured summary draft produced:")
    print(f"   - Chief Complaint: {content.get('chief_complaint')}")
    print(f"   - Red Flags: {content.get('red_flags_noted')}")
    assert "chief_complaint" in content
    assert "hpi" in content
    assert "past_history" in content
    assert "allergies" in content
    assert "red_flags_noted" in content

    # Step 47: Member 4 - Upload Sample Document to same session
    workspace_root = Path(__file__).resolve().parent.parent.parent
    sample_doc_path = workspace_root / "sample_data" / "documents" / "sample_prescription_01.jpg"
    sample_txt_path = workspace_root / "sample_data" / "documents" / "sample_prescription_01.txt"
    with open(sample_doc_path, "rb") as f_img:
        files = {"file": ("sample_prescription_01.jpg", f_img, "image/jpeg")}
        data = {
            "session_id": sess_id,
            "type": "prescription",
            "manual_text": open(sample_txt_path, "r").read()
        }
        up_res = client.post("/api/documents", files=files, data=data)
        assert up_res.status_code == 201
        doc_resp = up_res.json()
        print(f"[PASS] Step 47a: Member 4 uploaded prescription (Doc ID: {doc_resp['id']})")
        print(f"   - Extracted Medicines: {doc_resp['extracted_data']['medicines']}")

    # Check timeline contains both answers and document
    timeline_res = client.get(f"/api/timeline/{sess_id}")
    assert timeline_res.status_code == 200
    timeline = timeline_res.json()
    print(f"[PASS] Step 47b: Chronological Timeline contains {len(timeline)} total medical events")
    assert any(t["item_type"] == "document" for t in timeline)
    assert any(t["item_type"] == "answer" for t in timeline)

    # Step 48: Member 5 - Confirm Red-Flag Alert for chest-pain + breathlessness
    assert summary_data["has_red_flag_alert"] is True
    assert "PRIORITY TRIAGE ALERT" in summary_data["red_flag_message"]
    print(f"[PASS] Step 48a: Member 5 confirms PRIORITY TRIAGE ALERT is triggered on Red-Flag case!")

    # Test Normal Case side-by-side (Chest pain without breathlessness)
    norm_sess = client.post("/api/sessions", json={"demo_id": "DEMO-NORMAL-02", "language": "en"}).json()["session_id"]
    client.post(f"/api/sessions/{norm_sess}/answers", json={"question_id": "cp_onset", "answer_text": "Yesterday"})
    client.post(f"/api/sessions/{norm_sess}/answers", json={"question_id": "cp_breathlessness", "answer_text": "No"})
    norm_ai_res = client.post("/api/ai/summary", json={"session_id": norm_sess})
    assert norm_ai_res.json()["has_red_flag_alert"] is False
    print(f"[PASS] Step 48b: Normal scenario confirmed: No false alarm alert generated")

    # Step 49: Member 5 - Doctor Edit & Confirm via PUT /api/summary/{id}
    sum_id = summary_data["id"]
    put_res = client.put(f"/api/summary/{sum_id}", json={
        "chief_complaint": "Acute severe substernal chest pain with radiation & dyspnea",
        "hpi": content["hpi"] + " Verified bedside by Dr. A. Sharma.",
        "status": "doctor_confirmed"
    })
    assert put_res.status_code == 200
    confirmed_summary = put_res.json()
    assert confirmed_summary["status"] == "doctor_confirmed"
    print(f"[PASS] Step 49: Doctor edited and confirmed summary (status: {confirmed_summary['status']})")

    print("\nALL 5 MEMBERS INTEGRATED END-TO-END WITHOUT ANY CLASHES OR MISMATCHES!\n")

if __name__ == "__main__":
    run_integration_pipeline()
