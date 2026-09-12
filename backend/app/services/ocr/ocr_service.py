"""
Medical Document OCR & Entity Extraction Service
Parses prescriptions, lab reports, discharge summaries to structured fields.
Supports pytesseract OCR when available, with automatic regex/keyword entity extraction
and fallback mechanisms.
"""

import io
import re
import shutil
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Common medications for clinical intake keyword extraction
KNOWN_MEDICINES = [
    "Metformin", "Amlodipine", "Atorvastatin", "Paracetamol", "Azithromycin",
    "Pantoprazole", "Omeprazole", "Telmisartan", "Losartan", "Glimepiride",
    "Insulin", "Aspirin", "Clopidogrel", "Cetirizine", "Montelukast",
    "Amoxicillin", "Ciprofloxacin", "Levothyroxine", "Rosuvastatin", "Ibuprofen"
]

# Regex patterns for dates
DATE_PATTERNS = [
    r"\b\d{1,2}[-/](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[-/]\d{2,4}\b",
    r"\b\d{1,2}[-/.](?:0[1-9]|1[0-2]|[1-9])[-/.](?:\d{4}|\d{2})\b",
    r"\b(?:0[1-9]|1[0-2]|[1-9])[-/.](?:0[1-9]|[12]\d|3[01])[-/.](?:\d{4}|\d{2})\b",
]

class OCRService:
    @staticmethod
    def is_tesseract_available() -> bool:
        """Check if tesseract binary is accessible in environment PATH."""
        return shutil.which("tesseract") is not None

    @staticmethod
    def extract_text_from_image(file_bytes: bytes) -> str:
        """
        Attempt OCR extraction using pytesseract with PIL if tesseract is installed.
        Returns empty string if unavailable or on error.
        """
        try:
            from PIL import Image
            import pytesseract

            image = Image.open(io.BytesIO(file_bytes))
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            logger.warning(f"pytesseract extraction bypassed or failed: {e}")
            return ""

    @classmethod
    def extract_entities_from_text(cls, text: str) -> Dict[str, Any]:
        """
        Extract date, medicines, and clinics using simple keyword search and regex.
        Satisfies requirement 35: simple keyword search, avoid overengineering.
        """
        extracted_dates: List[str] = []
        for pattern in DATE_PATTERNS:
            matches = re.findall(pattern, text, flags=re.IGNORECASE)
            for m in matches:
                if m not in extracted_dates:
                    extracted_dates.append(m)

        detected_medicines: List[Dict[str, str]] = []
        for med in KNOWN_MEDICINES:
            # Match medicine name with optional dosage (e.g., "Metformin 500mg" or "Tab. Metformin")
            pattern = rf"\b(?:Tab\.?|Cap\.?|Syp\.?)?\s*({med}(?:\s+\d+(?:mg|ml|g))?)\b"
            matches = re.finditer(pattern, text, flags=re.IGNORECASE)
            for m in matches:
                val = m.group(0).strip()
                if not any(d["name"].lower() == med.lower() for d in detected_medicines):
                    detected_medicines.append({
                        "name": med,
                        "raw_match": val,
                        "type": "medication"
                    })

        # Detect clinic / doctor if present
        clinic_match = re.search(r"([A-Za-z\s]+(?:CLINIC|HOSPITAL|HEALTHCARE|MEDICAL CENTER))", text, flags=re.IGNORECASE)
        clinic_name = clinic_match.group(1).strip() if clinic_match else None

        doctor_match = re.search(r"(?:Dr\.?|Doctor)\s+([A-Za-z\.\s]+)", text, flags=re.IGNORECASE)
        doctor_name = doctor_match.group(0).strip() if doctor_match else None

        return {
            "dates": extracted_dates,
            "primary_date": extracted_dates[0] if extracted_dates else datetime.now().strftime("%Y-%m-%d"),
            "medicines": detected_medicines,
            "clinic_name": clinic_name,
            "doctor_name": doctor_name
        }

    @classmethod
    async def extract_text_and_entities(
        cls,
        file_bytes: bytes,
        filename: str,
        manual_fallback_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform OCR on document bytes or use fallback text if provided or if OCR yields no text.
        """
        raw_text = ""
        source = "ocr"

        # If user explicitly supplied typed/pasted fallback text (Requirement 34)
        if manual_fallback_text and manual_fallback_text.strip():
            raw_text = manual_fallback_text.strip()
            source = "manual_fallback"
        else:
            # Attempt OCR
            if cls.is_tesseract_available():
                raw_text = cls.extract_text_from_image(file_bytes)

            # If OCR failed or is uninstalled, provide clear fallback notification
            if not raw_text:
                source = "none"
                raw_text = ""

        entities = cls.extract_entities_from_text(raw_text) if raw_text else {
            "dates": [],
            "primary_date": datetime.now().strftime("%Y-%m-%d"),
            "medicines": [],
            "clinic_name": None,
            "doctor_name": None
        }

        return {
            "raw_text": raw_text,
            "source": source,
            "entities": entities,
            "document_date": entities["primary_date"],
            "medicines": [m["raw_match"] for m in entities["medicines"]],
            "hospital_name": entities.get("clinic_name") or "Medical Center"
        }
