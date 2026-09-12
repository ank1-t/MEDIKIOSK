# MediKiosk Requirements & Scope

## 1. Primary Goal
Build a working pre-consultation clinical intake prototype for a hackathon demo:
- **Patient Flow**: Kiosk registration $\rightarrow$ Language selection $\rightarrow$ Consent $\rightarrow$ Voice/Touch clinical history $\rightarrow$ Document Upload/OCR $\rightarrow$ AI-assisted structured summary $\rightarrow$ Doctor review and confirmation $\rightarrow$ Mock HIS/ABDM export.

## 2. In-Scope Features (MVP)
- **Patient Registration**: Demo patient ID assignment (synthetic data only).
- **Language Selector**: English and Hindi support with audio assistance.
- **Consent Screen**: Clear data handling consent with audio playback option.
- **Deterministic History Taking**: Question tree with branching based on Chief Complaint.
- **Multimodal Input**: Speech-to-text with fallback to large touch-friendly UI controls.
- **Document Ingestion & OCR**: Upload PDF/JPG/PNG records, extract key clinical entities (medications, diagnoses, dates, lab values) and render a chronological timeline.
- **AI-Assisted Summarization**: Schema-constrained summarization (Chief Complaint, HPI, Past History, Allergies/Medications, Family/Personal History, ROS).
- **Clinical Safety & Triage**: Deterministic red-flag rule evaluation for priority alerts.
- **Doctor Dashboard**: Review interface allowing clinicians to edit, accept, or reject AI-generated drafts.
- **Mock Interoperability**: Mock ABDM/FHIR and HIS push endpoints.

## 3. Explicit Non-Goals (What We Do NOT Build)
- Autonomous medical diagnoses or prescription changes.
- Ingestion or processing of real patient Aadhaar or ABHA IDs.
- Live hospital production deployment.
- Direct clinical decision without a doctor-in-the-loop.

## 4. Key Acceptance Criteria
1. Full end-to-end demo runnable under 60-90 seconds.
2. Complete touch fallback if speech/microphone fails.
3. Every AI-generated field includes source references and is editable by the doctor.
4. Red flags trigger priority triage alerts without generating medical diagnoses.
