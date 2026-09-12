# MediKiosk Clinical Safety & Governance

## 1. Safety Pillars
- **Strict Boundary**: The system is an intake and documentation assistant, never a diagnostic agent.
- **Rule-Based Triage**: High-risk symptom combinations (e.g., chest pain with radiation to left arm and shortness of breath) trigger priority alerts using deterministic rule sets, not probabilistic LLM guesswork.
- **Doctor-in-the-Loop**: All AI suggestions are clearly badged with `AI-generated draft — physician verification required`.
- **Traceability & Audit Log**: Every field in the summary can be traced back to the raw patient utterance, touch response, or source document chunk.

## 2. Red-Flag Alert Categories
1. **Cardiac / Acute Chest Pain**: Pressure sensation, radiating to arm/jaw, associated diaphoresis/dyspnea $\rightarrow$ Priority Triage Alert.
2. **Respiratory Distress**: Severe stridor, cyanosis, inability to complete full sentences $\rightarrow$ Immediate Nurse Notification.
3. **Anaphylaxis / Drug Reaction**: Sudden onset hives, facial swelling, breathing difficulty following medication $\rightarrow$ Immediate Red Flag.
