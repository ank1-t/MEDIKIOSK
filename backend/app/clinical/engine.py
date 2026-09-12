"""
Clinical History Engine - Deterministic Question Flow & Branching
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any

ONTOLOGY_PATH = Path(__file__).parent / "ontology.json"

class ClinicalEngine:
    def __init__(self):
        with open(ONTOLOGY_PATH, "r", encoding="utf-8") as f:
            self.ontology = json.load(f)

    def get_next_question(self, complaint: str, current_question_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get the next deterministic question for a given chief complaint pathway."""
        trees = self.ontology.get("complaint_trees", {})
        tree = trees.get(complaint)
        if not tree:
            return None

        if not current_question_id:
            first_q_id = tree.get("initial_question")
            return tree.get("questions", {}).get(first_q_id)

        current_q = tree.get("questions", {}).get(current_question_id)
        if not current_q:
            return None

        next_q_id = current_q.get("next")
        if not next_q_id:
            return None

        return tree.get("questions", {}).get(next_q_id)
