# Hackathon Live Demo Script (60-90s)

1. **The Problem Statement (10s)**:
   - "Doctors in busy OPDs spend 70% of their short consultation time collecting basic history and sorting through unorganized paper records."
2. **Kiosk Initiation & Language Selection (10s)**:
   - Patient arrives at MediKiosk, chooses Hindi / English, accepts voice/privacy consent.
3. **Multimodal Clinical Interview (25s)**:
   - Patient speaks: *"I have had chest pain and mild breathlessness for 2 days."*
   - Audio transcribed $\rightarrow$ deterministic follow-up questions triggered on screen.
   - Patient answers follow-ups using large accessible touch buttons.
4. **Document Ingestion & Timeline (15s)**:
   - Patient uploads an old ECG report or past prescription.
   - OCR extracts medication list and previous history into a clean visual chronological timeline.
5. **Red Flag & Doctor Confirmation (20s)**:
   - System flags a priority triage banner based on deterministic criteria.
   - Clinician opens Doctor Dashboard, reviews pre-organized structured summary, modifies one field, and clicks **Confirm & Export**.
   - Mock ABDM/HIS push acknowledged with transaction ID.
6. **Closing (5s)**:
   - *"AI prepares the structured information; the physician remains completely in control."*
