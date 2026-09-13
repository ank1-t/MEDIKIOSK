"""
AI Summarization Gateway & Clinical Safety Integration
Supports:
- Gemini API (google.genai / httpx direct API)
- Strict prompt enforcement (chief_complaint, hpi, past_history, allergies, red_flags_noted)
- Deterministic fallback summary when offline or if API key is invalid
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
import httpx

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert clinical intake documentation engine for a medical triage kiosk.
Analyze the provided patient questionnaire answers and uploaded document findings.
Generate a strictly structured medical intake summary draft for the attending physician.

STRICT INSTRUCTIONS:
1. Return ONLY a valid JSON object. No Markdown code fencing, no formatting outside of JSON.
2. The JSON object MUST contain exactly these top-level keys:
   - "chief_complaint": string (concise primary symptom)
   - "hpi": string (chronological history of present illness including onset, duration, radiation, character)
   - "past_history": list of strings (past conditions, surgeries, cardiac history reported)
   - "allergies": list of strings (any reported allergies, or empty list if none)
   - "red_flags_noted": list of strings (clinical red flags identified from symptoms, e.g. acute chest pain with breathlessness or radiation)
3. DO NOT invent facts or add diagnoses. State only reported facts.
4. Keep clinical language objective, clear, and professional.
"""

class AISummaryService:
    @staticmethod
    def build_deterministic_fallback(answers: List[Dict[str, Any]], documents: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Deterministic, robust fallback summary built directly from raw answers.
        Satisfies Requirement 28: if AI fails or times out, never show blank screen.
        """
        ans_map = {}
        for a in answers:
            qid = str(a.get("question_id", ""))
            val = str(a.get("answer_text") or a.get("answer") or "").strip()
            ans_map[qid] = val

        onset = ans_map.get("cp_onset", "Not specified")
        duration = ans_map.get("cp_duration", "Not specified")
        severity = ans_map.get("cp_severity", "Not specified")
        radiation = ans_map.get("cp_radiation", "No")
        breathless = ans_map.get("cp_breathlessness") or ans_map.get("cp_breathless", "No")
        past_cardiac = ans_map.get("cp_past_cardiac", "No")

        red_flags: List[str] = []
        is_chest_pain = any("cp_" in k for k in ans_map.keys()) or any("chest" in str(v).lower() for v in ans_map.values())
        has_breathless = "yes" in breathless.lower()

        if is_chest_pain and has_breathless:
            red_flags.append("Acute chest pain accompanied by breathlessness / dyspnea (Priority Triage Alert)")
        if "yes" in radiation.lower() or "left_arm" in radiation.lower():
            red_flags.append("Pain radiating to arm or jaw")

        past_history_items: List[str] = []
        if "yes" in past_cardiac.lower():
            past_history_items.append("Positive personal history of cardiovascular disease / cardiac event")
        else:
            past_history_items.append("No prior cardiac history reported on kiosk intake")

        # Document extracted notes
        if documents:
            for doc in documents:
                extracted = doc.get("extracted_data") or {}
                meds = extracted.get("medicines") or []
                if meds:
                    past_history_items.append(f"Document ({doc.get('filename')}): Current/prior meds: {', '.join(meds)}")

        hpi_text = (
            f"Patient presented with chest pain starting {onset}. "
            f"Symptom duration: {duration}. Reported pain severity rating: {severity}/10. "
            f"Radiation: {radiation}. Accompanying breathlessness/dyspnea: {breathless}. "
            f"Intake completed at kiosk."
        )

        return {
            "chief_complaint": "Chest pain / discomfort",
            "hpi": hpi_text,
            "past_history": past_history_items,
            "allergies": [],
            "red_flags_noted": red_flags,
            "source": "deterministic_fallback"
        }

    @classmethod
    async def generate_summary(
        cls,
        answers: List[Dict[str, Any]],
        documents: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate structured clinical summary using Gemini API if key is available.
        Otherwise or on failure/timeout, return deterministic fallback.
        """
        api_key = os.getenv("GEMINI_API_KEY", "").strip()

        # If key is missing or dummy placeholder, use fallback immediately
        if not api_key or api_key == "your_gemini_api_key_here":
            logger.info("Gemini API key not configured or placeholder; using deterministic fallback summary.")
            return cls.build_deterministic_fallback(answers, documents)

        # Build prompt payload
        patient_input_summary = {
            "intake_answers": answers,
            "attached_documents": [
                {
                    "filename": d.get("filename"),
                    "type": d.get("type"),
                    "text_snippet": (d.get("text") or "")[:500]
                }
                for d in (documents or [])
            ]
        }

        user_content = f"PATIENT INTAKE DATA (JSON):\n{json.dumps(patient_input_summary, indent=2)}\n\nGenerate structured clinical summary adhering to instructions."

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {"text": SYSTEM_PROMPT + "\n\n" + user_content}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.1,
                    "responseMimeType": "application/json"
                }
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            raw_json = parts[0]["text"].strip()
                            parsed = json.loads(raw_json)
                            # Ensure all required keys exist
                            return {
                                "chief_complaint": parsed.get("chief_complaint", "Chest pain"),
                                "hpi": parsed.get("hpi", ""),
                                "past_history": parsed.get("past_history", []),
                                "allergies": parsed.get("allergies", []),
                                "red_flags_noted": parsed.get("red_flags_noted", []),
                                "source": "gemini_ai"
                            }
                logger.warning(f"Gemini API returned non-200 status {res.status_code}: {res.text}")
        except Exception as e:
            logger.warning(f"Gemini API call failed or timed out ({e}). Activating deterministic fallback.")

        return cls.build_deterministic_fallback(answers, documents)
