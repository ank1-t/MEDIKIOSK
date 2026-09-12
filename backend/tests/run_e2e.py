import httpx

client = httpx.Client(base_url="http://localhost:8000")

# 1. Health check
res = client.get("/health")
print("1. Health check status:", res.status_code)

# 2. Upload document
with open("sample_data/documents/sample_prescription_01.jpg", "rb") as f:
    files = {"file": ("sample_prescription_01.jpg", f, "image/jpeg")}
    data = {
        "session_id": "sess_e2e_demo_01",
        "type": "prescription",
        "manual_text": open("sample_data/documents/sample_prescription_01.txt").read()
    }
    upload_res = client.post("/api/documents", files=files, data=data)
    print("2. Upload status:", upload_res.status_code)
    upload_data = upload_res.json()
    print("   Uploaded doc ID:", upload_data["id"])
    print("   Extracted medicines:", upload_data["extracted_data"]["medicines"])
    print("   Extracted date:", upload_data["extracted_data"]["document_date"])

# 3. Add intake answer to same session
ans_res = client.post("/api/sessions/sess_e2e_demo_01/answers", json={
    "question_id": "q_chief_complaint",
    "answer_text": "Follow-up consultation for Type 2 Diabetes and Hypertension",
    "source": "touch"
})
print("3. Added Answer status:", ans_res.status_code)

# 4. Fetch timeline
timeline_res = client.get("/api/timeline/sess_e2e_demo_01")
print("4. Timeline status:", timeline_res.status_code)
timeline = timeline_res.json()
print(f"   Timeline items count: {len(timeline)}")
for item in timeline:
    print(f"   - [{item['item_type'].upper()}] {item['title']} ({item['date_or_time']})")
