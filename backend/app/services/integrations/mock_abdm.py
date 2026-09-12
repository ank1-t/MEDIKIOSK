"""
Mock ABDM / FHIR Interoperability Gateway
Simulates milestone integration with Ayushman Bharat Digital Mission (ABDM).
"""

import uuid
from datetime import datetime
from typing import Dict, Any

class MockABDMService:
    @staticmethod
    def push_health_record(summary_data: Dict[str, Any], abha_id: str = "demo-user@abdm") -> Dict[str, Any]:
        """Generate mock ABDM transaction acknowledge and FHIR bundle representation."""
        txn_id = f"ABDM-TXN-{uuid.uuid4().hex[:8].upper()}"
        return {
            "status": "acknowledged",
            "transaction_id": txn_id,
            "abha_id": abha_id,
            "bundle_type": "FHIR-R4-Composition",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Health summary bundle queued for patient consent manager gateway."
        }
