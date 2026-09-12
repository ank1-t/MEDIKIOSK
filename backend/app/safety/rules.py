"""
Deterministic Red-Flag Rules Engine
Evaluates answers for life-threatening or emergency symptoms.
Does not generate diagnosis — strictly produces triage priority warnings.
"""

from typing import List, Dict, Any

class SafetyEngine:
    @staticmethod
    def evaluate_red_flags(answers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Evaluate answers against deterministic safety rules.
        Example: Acute chest pain + radiating to left arm + dyspnea -> Priority triage alert.
        """
        alerts = []
        answer_map = {a.get("question_id"): str(a.get("answer", "")).lower() for a in answers}

        # Rule 1: Cardiac Warning (Left arm pain + Shortness of breath)
        has_arm_pain = "left_arm" in answer_map.get("cp_radiation", "")
        has_dyspnea = "yes" in answer_map.get("cp_breathless", "")

        if has_arm_pain and has_dyspnea:
            alerts.append({
                "rule_id": "RF-CARDIAC-01",
                "severity": "priority_triage",
                "message": "Priority Triage Alert: Patient reports chest pain radiating to left arm with breathlessness/sweating.",
                "action_recommended": "Expedited clinical triage evaluation recommended."
            })

        return alerts
