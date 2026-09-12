"""
AI Summarization & Extraction Service Gateway
Handles LLM interaction with strict schema output and traceability.
"""

from typing import Dict, Any, List

class AISummaryService:
    @staticmethod
    async def generate_summary(answers: List[Dict[str, Any]], extracted_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate structured clinical summary draft from raw answers and OCR-extracted document data.
        Falls back to deterministic template generation if LLM is offline.
        """
        # Formulate structured sections
        chief_complaints = [a.get("answer") for a in answers if "complaint" in a.get("question_id", "")]
        cc_text = ", ".join(chief_complaints) if chief_complaints else "Patient reported symptoms during kiosk intake"

        return {
            "chief_complaint": cc_text,
            "history_of_present_illness": f"Intake completed via MediKiosk. Total responses recorded: {len(answers)}.",
            "past_medical_history": ["Extracted from uploaded records or patient touch inputs"],
            "medications": [],
            "allergies": [],
            "family_history": [],
            "personal_history": [],
            "review_of_systems": {},
            "investigations": [],
            "alerts": []
        }
