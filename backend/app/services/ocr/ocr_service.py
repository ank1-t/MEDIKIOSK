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

# Common modern and AYUSH medications for clinical intake keyword extraction
KNOWN_MEDICINES = [
    # Modern Allopathic
    "Metformin", "Amlodipine", "Atorvastatin", "Paracetamol", "Azithromycin",
    "Pantoprazole", "Omeprazole", "Telmisartan", "Losartan", "Glimepiride",
    "Insulin", "Aspirin", "Clopidogrel", "Cetirizine", "Montelukast",
    "Amoxicillin", "Ciprofloxacin", "Levothyroxine", "Rosuvastatin", "Ibuprofen",
    "Dolo", "Combiflam", "Augmentin", "Pan-D", "Rablet", "Glycomet", "Ecosprin",
    # Ayurvedic & Herbal Formulations (Ministry of AYUSH)
    "Arogyavardhini Vati", "Triphala Guggulu", "Ashwagandha Churna",
    "Chyawanprash", "Brahmi Vati", "Kanchnar Guggulu", "Shankhapushpi",
    "Mahasudarshan Churna", "Sitopaladi Churna", "Chandraprabha Vati",
    "Khadirarishta", "Amritarishta", "Trikatu Churna", "Gokshuradi Guggulu",
    "Yograj Guggulu", "Dashmularishta", "Abhayarishta", "Vasavaleha",
    "Avipattikar Churna", "Sutshekhar Ras", "Laxmivilas Ras"
]

# Regex patterns for dates
DATE_PATTERNS = [
    r"\b\d{1,2}[-/](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[-/]\d{2,4}\b",
    r"\b\d{1,2}[-/.](?:0[1-9]|1[0-2]|[1-9])[-/.](?:\d{4}|\d{2})\b",
    r"\b(?:0[1-9]|1[0-2]|[1-9])[-/.](?:0[1-9]|[12]\d|3[01])[-/.](?:\d{4}|\d{2})\b",
    r"\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b",
]

# Regex patterns for clinical vitals and lab markers
VITAL_PATTERNS = {
    "haemoglobin": r"(?:Hb|Haemoglobin|Hemoglobin)\s*[:=-]?\s*(\d+(?:\.\d+)?)\s*(?:g/dL|g/dl|gm/dl)?",
    "fasting_glucose": r"(?:FBS|Fasting\s+(?:Blood\s+)?Glucose|Fasting\s+Sugar)\s*[:=-]?\s*(\d+(?:\.\d+)?)\s*(?:mg/dL|mg/dl)?",
    "random_glucose": r"(?:RBS|Random\s+(?:Blood\s+)?Glucose|Sugar)\s*[:=-]?\s*(\d+(?:\.\d+)?)\s*(?:mg/dL|mg/dl)?",
    "blood_pressure": r"(?:BP|Blood\s+Pressure)\s*[:=-]?\s*(\d{2,3}\s*/\s*\d{2,3})\s*(?:mmHg)?",
    "pulse": r"(?:Pulse|Heart\s+Rate|HR)\s*[:=-]?\s*(\d{2,3})\s*(?:bpm)?",
    "spo2": r"(?:SpO2|Oxygen|O2)\s*[:=-]?\s*(\d{2,3})\s*%",
    "serum_creatinine": r"(?:Creatinine|S\.Cr)\s*[:=-]?\s*(\d+(?:\.\d+)?)\s*(?:mg/dL)?",
    "tsh": r"(?:TSH)\s*[:=-]?\s*(\d+(?:\.\d+)?)\s*(?:uIU/mL|mIU/L)?"
}

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
        Extract dates, medicines (allopathic + AYUSH), lab vitals, and doctor/clinic names.
        """
        extracted_dates: List[str] = []
        for pattern in DATE_PATTERNS:
            matches = re.findall(pattern, text, flags=re.IGNORECASE)
            for m in matches:
                if m not in extracted_dates:
                    extracted_dates.append(m)

        detected_medicines: List[Dict[str, str]] = []
        for med in KNOWN_MEDICINES:
            pattern = rf"\b(?:Tab\.?|Cap\.?|Syp\.?|Vati|Churna|Ras)?\s*({re.escape(med)}(?:\s+\d+(?:mg|ml|g))?)\b"
            matches = re.finditer(pattern, text, flags=re.IGNORECASE)
            for m in matches:
                val = m.group(0).strip()
                if not any(d["name"].lower() == med.lower() for d in detected_medicines):
                    detected_medicines.append({
                        "name": med,
                        "raw_match": val,
                        "type": "medication"
                    })

        # Generic pattern for any Rx line item, e.g. "Tab. BrandName 500mg" or "1. MedicineName 10mg"
        generic_rx = re.findall(r"(?:^|\n)\s*(?:\d+[\.\)]|Rx:?|Tab\.?|Cap\.?|Syp\.?)\s*([A-Za-z\s]{3,25}\s+\d+\s*(?:mg|ml|g|mcg))", text, flags=re.IGNORECASE)
        for gen in generic_rx:
            cleaned = gen.strip()
            if not any(d["raw_match"].lower() == cleaned.lower() for d in detected_medicines):
                detected_medicines.append({
                    "name": cleaned.split()[0],
                    "raw_match": cleaned,
                    "type": "medication"
                })

        # Extract lab vitals
        detected_vitals: Dict[str, str] = {}
        for vital_name, vital_regex in VITAL_PATTERNS.items():
            match = re.search(vital_regex, text, flags=re.IGNORECASE)
            if match:
                detected_vitals[vital_name] = match.group(1).strip()

        # Detect clinic / doctor if present
        clinic_match = re.search(r"([A-Za-z\s]+(?:CLINIC|HOSPITAL|HEALTHCARE|MEDICAL CENTER|INSTITUTE OF AYURVEDA|AIIA))", text, flags=re.IGNORECASE)
        clinic_name = clinic_match.group(1).strip() if clinic_match else None

        doctor_match = re.search(r"(?:Dr\.?|Doctor)\s+([A-Za-z\.\s]{3,30})", text, flags=re.IGNORECASE)
        doctor_name = doctor_match.group(0).strip() if doctor_match else None

        return {
            "dates": extracted_dates,
            "primary_date": extracted_dates[0] if extracted_dates else datetime.now().strftime("%Y-%m-%d"),
            "medicines": detected_medicines,
            "vitals": detected_vitals,
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
            "vitals": {},
            "clinic_name": None,
            "doctor_name": None
        }

        return {
            "raw_text": raw_text,
            "source": source,
            "entities": entities,
            "document_date": entities["primary_date"],
            "medicines": [m["raw_match"] for m in entities["medicines"]],
            "vitals": entities.get("vitals", {}),
            "hospital_name": entities.get("clinic_name") or "Medical Center"
        }
