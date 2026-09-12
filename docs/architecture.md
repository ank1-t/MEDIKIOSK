# MediKiosk System Architecture

## Architecture Overview

```mermaid
flowchart LR
    subgraph Client ["Client Tier (Kiosk & Clinician)"]
        PatientUI["Patient Kiosk UI (Next.js)"]
        DoctorUI["Doctor Review Dashboard"]
    end

    subgraph BackendServer ["FastAPI Application"]
        API["REST API Router (/api/v1)"]
        SessionEng["Session & Question Engine"]
        SafetyEng["Safety & Triage Rules Engine"]
        AIService["AI & Summary Service (Gemini/Ollama)"]
        OCRService["Document OCR Engine"]
        MockAdapter["Interoperability Adapter (Mock ABDM/HIS)"]
    end

    subgraph DataStore ["Data & Storage"]
        DB[(SQLite / PostgreSQL)]
        FileStore[Local Storage / Uploads]
    end

    PatientUI -->|HTTP / JSON| API
    DoctorUI -->|HTTP / JSON| API
    API --> SessionEng
    API --> SafetyEng
    API --> AIService
    API --> OCRService
    API --> MockAdapter
    SessionEng --> DB
    OCRService --> FileStore
```

## Core Design Principles
1. **Separation of Concerns**: Deterministic rules govern the question trees and triage flags; AI is strictly restricted to extraction and summarization.
2. **Data Traceability**: Every summary fact is traceable back to patient voice transcript, touch selection, or OCR-extracted document text.
3. **Graceful Degradation**: If AI or network fails, the system seamlessly drops back to offline deterministic question forms.
4. **Physician Control**: The AI produces a draft; only the physician can confirm the final structured clinical record.
