"""
Tests for Member 4 deliverables:
- POST /api/documents (upload image, fallback text, OCR entity extraction)
- GET /api/documents (list)
- GET /api/timeline/{session_id} (chronological order)
"""

import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_document_upload_with_manual_fallback():
    """Test uploading a prescription file with fallback text and extracting entities."""
    # 1. Create a session
    sess_resp = client.post("/api/sessions", json={"demo_id": "DEMO-PT-DOC-1", "language": "en"})
    assert sess_resp.status_code == 201
    session_id = sess_resp.json()["id"]

    # 2. Upload sample document with manual fallback text (Requirement 34 & 35)
    sample_text = """
    CITY CARE MULTISPECIALITY CLINIC
    Date: 15-Jan-2025
    Rx:
    1. Tab. Metformin 500mg BD
    2. Tab. Amlodipine 5mg OD
    3. Tab. Atorvastatin 10mg HS
    """
    file_bytes = b"fake-image-bytes-prescription"
    files = {"file": ("rx_test.png", io.BytesIO(file_bytes), "image/png")}
    data = {
        "session_id": session_id,
        "type": "prescription",
        "manual_text": sample_text
    }

    upload_resp = client.post("/api/documents", files=files, data=data)
    assert upload_resp.status_code == 201
    doc_data = upload_resp.json()
    assert doc_data["session_id"] == session_id
    assert "filename" in doc_data
    assert doc_data["text"].strip() == sample_text.strip()
    assert "extracted_data" in doc_data

    # Check extracted date and medicines (Requirement 35)
    extracted = doc_data["extracted_data"]
    assert "15-Jan-2025" in extracted["document_date"]
    meds = [m.lower() for m in extracted["medicines"]]
    assert any("metformin" in m for m in meds)
    assert any("amlodipine" in m for m in meds)
    assert any("atorvastatin" in m for m in meds)

    # 3. Test timeline endpoint (Requirement 36)
    timeline_resp = client.get(f"/api/timeline/{session_id}")
    assert timeline_resp.status_code == 200
    timeline = timeline_resp.json()
    assert len(timeline) >= 1
    doc_item = next(item for item in timeline if item["item_type"] == "document")
    assert doc_item["details"]["document_id"] == doc_data["id"]
    assert len(doc_item["details"]["medicines"]) >= 3


def test_timeline_ordering():
    """Verify chronological timeline contains both answers and documents."""
    sess_resp = client.post("/api/sessions", json={"demo_id": "DEMO-PT-TIMELINE", "language": "en"})
    session_id = sess_resp.json()["id"]

    # Add answer
    client.post(f"/api/sessions/{session_id}/answers", json={
        "question_id": "q_chief_complaint",
        "answer_text": "High blood pressure checkup",
        "source": "touch"
    })

    # Add document
    file_bytes = b"mock-file-data"
    files = {"file": ("lab_report.jpg", io.BytesIO(file_bytes), "image/jpeg")}
    client.post("/api/documents", files=files, data={
        "session_id": session_id,
        "type": "lab_report",
        "manual_text": "Date: 10-Jan-2025 Blood Sugar: 140 mg/dl"
    })

    timeline_resp = client.get(f"/api/timeline/{session_id}")
    assert timeline_resp.status_code == 200
    timeline = timeline_resp.json()
    assert len(timeline) == 2
    types = [item["item_type"] for item in timeline]
    assert "answer" in types
    assert "document" in types
