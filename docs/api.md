# MediKiosk API Specification

Base URL: `/api/v1`

## Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Service health check |
| `POST` | `/sessions` | Create a new patient session |
| `GET` | `/sessions/{id}` | Load existing session state and progress |
| `POST` | `/sessions/{id}/answers` | Save an answer to a question |
| `GET` | `/questions/next` | Retrieve next deterministic question |
| `POST` | `/ai/extract` | Convert freeform narrative/speech transcript to structured fields |
| `POST` | `/ai/summary` | Generate a structured clinical summary from answers and OCR data |
| `POST` | `/documents` | Upload a patient medical document (PDF/JPG/PNG) |
| `POST` | `/documents/{id}/process` | Trigger OCR & medical entity extraction on an uploaded document |
| `GET` | `/timeline/{session_id}` | Retrieve chronological timeline of patient history & medical records |
| `GET` | `/summary/{session_id}` | Fetch generated clinical summary for doctor review |
| `PUT` | `/summary/{id}` | Update/edit clinical summary fields (doctor action) |
| `POST` | `/summary/{id}/confirm` | Confirm and sign off the clinical summary |
| `POST` | `/triage/check` | Execute deterministic red-flag triage rules |
| `POST` | `/integrations/his/send` | Mock push of intake record to Hospital Information System |
| `POST` | `/integrations/abdm/send` | Mock push of health summary to ABDM/FHIR gateway |
