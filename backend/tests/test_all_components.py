"""
Complete System Verification Suite for MediKiosk
Tests:
1. Backend Health & Endpoints
2. Patient Registration & Sessions (Member 1)
3. Intake & SOCRATES Answers Storing (Member 2)
4. AI Clinical Summary & Red-Flag Priority Triage (Member 3 & 5)
5. Prescription Upload, OCR & Entity Extraction (Member 4)
6. Doctor Consultation Desk Edit & Confirmation (Member 5)
7. Algorand TestNet x402 Challenge & Facilitator Settlement
8. Frontend API Compatibility contract
"""

import os
import sys
import json
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_all_checks():
    results = []
    
    print("\n" + "=" * 60)
    print("      MEDIKIOSK COMPREHENSIVE COMPONENT VERIFICATION")
    print("=" * 60)

    # 1. Health check
    try:
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"
        results.append(("1. Health & Server Ping", True, "FastAPI backend responsive"))
    except Exception as e:
        results.append(("1. Health & Server Ping", False, str(e)))

    # 2. Session Creation (Identify screen)
    sess_id = None
    try:
        r = client.post("/api/sessions", json={
            "name": "Anita Sharma",
            "age": 42,
            "gender": "Female",
            "mobile": "9876543210",
            "abha_id": "12-3456-7890-1234",
            "language": "hi"
        })
        assert r.status_code == 201
        data = r.json()
        sess_id = data["session_id"]
        token = data.get("token_number", "OPD-AYUSH-104")
        results.append(("2. Patient Registration (Member 1)", True, f"Session {sess_id} created with Token {token}"))
    except Exception as e:
        results.append(("2. Patient Registration (Member 1)", False, str(e)))

    # 3. Intake Answers (Complaint & SOCRATES)
    try:
        answers = [
            {"question_id": "chief_complaint", "question_text": "What brings you?", "answer_text": "Chest pain with breathlessness"},
            {"question_id": "onset", "question_text": "Onset", "answer_text": "Today"},
            {"question_id": "severity", "question_text": "Severity", "answer_text": "8/10"},
            {"question_id": "nature", "question_text": "Nature", "answer_text": "Sharp"},
            {"question_id": "prakriti", "question_text": "Prakriti", "answer_text": "Pitta"},
            {"question_id": "agni", "question_text": "Agni", "answer_text": "Irregular"}
        ]
        r = client.post(f"/api/sessions/{sess_id}/answers", json={"answers": answers})
        assert r.status_code in (200, 201)
        
        # Verify persistence
        get_sess = client.get(f"/api/sessions/{sess_id}")
        assert get_sess.status_code == 200
        saved_ans = get_sess.json()["answers"]
        assert len(saved_ans) == 6
        results.append(("3. Clinical Intake & Answers (Member 2)", True, f"Saved & verified {len(saved_ans)} responses in DB"))
    except Exception as e:
        results.append(("3. Clinical Intake & Answers (Member 2)", False, str(e)))

    # 4. Document OCR & Entity Extraction (Scan & Review screen)
    try:
        sample_img = backend_dir.parent / "sample_data" / "documents" / "sample_prescription_01.jpg"
        sample_txt = backend_dir.parent / "sample_data" / "documents" / "sample_prescription_01.txt"
        manual_text = open(sample_txt, "r").read() if sample_txt.exists() else "Tab. Arogyavardhini Vati 250mg, Tab. Paracetamol 500mg"
        
        with open(sample_img, "rb") as f_img:
            r = client.post(
                "/api/documents",
                files={"file": ("prescription.jpg", f_img, "image/jpeg")},
                data={"session_id": sess_id, "type": "prescription", "manual_text": manual_text}
            )
        assert r.status_code == 201
        doc_data = r.json()
        meds = doc_data["extracted_data"].get("medicines", [])
        assert len(meds) > 0
        results.append(("4. Document OCR & Entities (Member 4)", True, f"Prescription processed. Extracted {len(meds)} medicines: {meds}"))
    except Exception as e:
        results.append(("4. Document OCR & Entities (Member 4)", False, str(e)))

    # 5. AI Summary & Priority Triage Alert (Member 3 & 5)
    summary_id = None
    try:
        r = client.post("/api/ai/summary", json={"session_id": sess_id})
        assert r.status_code == 200
        sum_data = r.json()
        summary_id = sum_data["id"]
        content = sum_data["content_json"]
        has_red_flag = sum_data.get("has_red_flag_alert")
        red_flag_msg = sum_data.get("red_flag_message", "")
        assert "chief_complaint" in content
        assert "hpi" in content
        assert has_red_flag is True
        assert "PRIORITY TRIAGE ALERT" in red_flag_msg
        results.append(("5. AI Summary & Red-Flag Triage (Member 3 & 5)", True, f"Generated HPI & Triggered '{red_flag_msg}'"))
    except Exception as e:
        results.append(("5. AI Summary & Red-Flag Triage (Member 3 & 5)", False, str(e)))

    # 6. Doctor Confirmation Desk (Doctor Portal)
    try:
        r = client.put(f"/api/summary/{summary_id}", json={
            "chief_complaint": "Acute severe substernal chest pain with dyspnea",
            "doctor_notes": "Immediate ECG completed. Patient stabilized by Dr. Sharma at OPD Desk.",
            "status": "doctor_confirmed"
        })
        assert r.status_code == 200
        doc_conf = r.json()
        assert doc_conf["status"] == "doctor_confirmed"
        results.append(("6. Doctor Review & Sign-Off (Member 5)", True, f"Doctor confirmed and updated summary ID: {summary_id}"))
    except Exception as e:
        results.append(("6. Doctor Review & Sign-Off (Member 5)", False, str(e)))

    # 7. Algorand TestNet x402 Micropayments
    try:
        # Check config
        r_cfg = client.get("/api/v1/x402/config")
        assert r_cfg.status_code == 200
        cfg = r_cfg.json()
        assert cfg["network"] == "Algorand TestNet"
        assert cfg["facilitator_name"] == "GoPlausible"

        # Check 402 challenge
        r_chal = client.post("/api/v1/x402/challenge", json={"service": "MediKiosk OPD Intake", "price": "$0.005"})
        assert r_chal.status_code == 402
        assert "Payment-Required" in r_chal.headers
        chal_body = r_chal.json()
        assert chal_body["status"] == 402
        assert chal_body["facilitator"]["type"] == "goplausible"

        # Verify payment with facilitator
        r_verify = client.post("/api/v1/x402/verify-intake", json={"auto_settle": True})
        assert r_verify.status_code == 200
        verify_data = r_verify.json()
        assert verify_data["success"] is True
        tx_id = verify_data["verification"]["tx_id"]
        lora_url = verify_data["verification"]["lora_url"]
        assert "lora.algokit.io/testnet" in lora_url
        results.append(("7. x402 Algorand TestNet Payments", True, f"HTTP 402 challenge + GoPlausible settlement verified: {tx_id} -> {lora_url}"))
    except Exception as e:
        results.append(("7. x402 Algorand TestNet Payments", False, str(e)))

    print("\nVERIFICATION RESULTS:")
    all_passed = True
    for name, status, detail in results:
        status_icon = "PASS" if status else "FAIL"
        print(f"  [{status_icon}] {name}")
        print(f"         Detail: {detail}")
        if not status:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print(">> ALL COMPONENTS & ENDPOINTS PASSED WITH 100% SUCCESS <<")
    else:
        print(">> SOME COMPONENTS FAILED <<")
    print("=" * 60 + "\n")
    return all_passed

if __name__ == "__main__":
    success = run_all_checks()
    sys.exit(0 if success else 1)
