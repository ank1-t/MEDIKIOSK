"""
Mock Hospital Information System (HIS) Integration
Simulates EHR / OPD encounter submission.
"""

import uuid
from datetime import datetime
from typing import Dict, Any

class MockHISService:
    @staticmethod
    def push_encounter_summary(summary_data: Dict[str, Any], patient_mrn: str = "DEMO-MRN-9021") -> Dict[str, Any]:
        """Push pre-consult intake structured note to Hospital EHR."""
        encounter_id = f"ENC-{uuid.uuid4().hex[:6].upper()}"
        return {
            "status": "success",
            "hospital_encounter_id": encounter_id,
            "patient_mrn": patient_mrn,
            "received_at": datetime.utcnow().isoformat(),
            "notes_appended": True
        }
