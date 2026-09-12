# MediKiosk - AI-Powered Clinical History & Medical Intake Platform

MediKiosk is a patient-facing software platform that moves structured history-taking and medical-document organization to the period before doctor consultation. Patients can speak or tap answers in their preferred language, upload previous medical documents, and receive a draft structured history for doctor review and confirmation.

---

## 🏗️ Architecture & Tech Stack

- **Frontend**: Next.js / React kiosk UI with accessibility-first design (English & Hindi support)
- **Backend**: Python FastAPI REST API with modular services
- **Database**: SQLite (prototype/MVP), PostgreSQL (future)
- **AI Gateway**: Multimodal AI (Gemini / Ollama), OCR (Tesseract / PaddleOCR / Vision API), Speech (Web Speech API / AI4Bharat / Bhashini)
- **Integrations**: Mock ABDM (Ayushman Bharat Digital Mission) & Mock HIS endpoints

---

## 📁 Repository Structure

```text
.
├── frontend/                     # Next.js Kiosk Web Application
│   ├── app/                      # App router pages & layouts (Welcome, Registration, History, etc.)
│   ├── components/               # UI components (Questions, Audio guidance, Review, Kiosk buttons)
│   ├── lib/                      # Utilities, API client helpers
│   └── types/                    # TypeScript type definitions
│
├── backend/                      # FastAPI Backend Server
│   ├── app/
│   │   ├── api/                  # API route handlers (v1 endpoints)
│   │   ├── models/               # Database ORM models (SQLAlchemy/SQLModel)
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   ├── services/             # Core service implementations
│   │   │   ├── ai/               # LLM extraction & summarization gateway
│   │   │   ├── speech/           # Speech-to-text & Audio handlers
│   │   │   ├── ocr/              # Document OCR & extraction pipelines
│   │   │   ├── documents/        # File management & storage
│   │   │   └── integrations/     # Mock ABDM / HIS adapters
│   │   ├── clinical/             # Deterministic question ontologies & branching engine
│   │   ├── safety/               # Red-flag rules, triage alerts, audit trail
│   │   └── main.py               # Application entrypoint & CORS setup
│   └── tests/                    # Backend unit & integration test suites
│
├── sample_data/                  # Demo & Synthetic Datasets
│   ├── patients/                 # Synthetic patient profiles & scenarios (e.g., chest pain, fever)
│   └── documents/                # Sample prescriptions & lab reports for OCR testing
│
├── docs/                         # Project Documentation & Specifications
│   ├── requirements.md           # Product requirements & scope
│   ├── architecture.md           # Technical design & data flow
│   ├── api.md                    # REST API specifications
│   ├── safety.md                 # Clinical safety boundaries & red-flag rules
│   └── demo-script.md            # Hackathon live demo walkthrough script
│
├── .env.example                  # Environment variable template
├── .gitignore                    # Standard git ignore rules
├── docker-compose.yml            # Container setup for local development
└── README.md                     # Project overview (this file)
```

---

## 👥 Team Workstreams & Responsibilities

| Workstream | Key Directories | Focus Area |
| :--- | :--- | :--- |
| **Frontend & UI/UX** | `frontend/` | Kiosk UI, touch/voice inputs, Hindi/English localization, progress flow |
| **Backend & Core API** | `backend/app/api/`, `backend/app/models/` | FastAPI endpoints, SQLite schema, session state management |
| **Clinical & Safety Engine** | `backend/app/clinical/`, `backend/app/safety/` | Question branching logic, red-flag triage detection |
| **AI & Document Intelligence** | `backend/app/services/` | Summary generation, entity extraction, OCR pipelines, audio |
| **Interoperability & Mocking**| `backend/app/services/integrations/` | Mock ABDM/FHIR and HIS push endpoints |

---

## 🚀 Getting Started

### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🛡️ Clinical Safety Disclaimer
MediKiosk is an intake and history summarization prototype. It is **not** a diagnostic device, does **not** prescribe medication, and all generated summaries require explicit physician review and verification.
