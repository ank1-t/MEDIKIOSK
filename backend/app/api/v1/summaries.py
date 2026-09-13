"""
Summary & AI Integration Endpoints
Endpoints:
- POST /api/ai/summary (Generates structured clinical summary draft, checks red-flag rule)
- GET /api/summary/{session_id} (Fetch latest summary for session)
- PUT /api/summary/{id} (Doctor edit and confirmation)
- GET /api/questions/chest-pain (Member 3 shared chest pain questionnaire)
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models.models import Session, Answer, Document, Summary, Alert
from app.schemas.schemas import AISummaryRequest, SummaryResponse, SummaryUpdate
from app.services.ai.summary_service import AISummaryService
from app.safety.rules import SafetyEngine

router = APIRouter(tags=["Summaries & AI"])

QUESTIONS_FILE = Path(__file__).resolve().parent.parent.parent / "clinical" / "questions_chest_pain.json"

@router.get("/questions/chest-pain")
async def get_chest_pain_questions():
    """Returns standardized chest pain intake questions for Member 2 frontend."""
    if QUESTIONS_FILE.exists():
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


@router.post("/ai/summary", response_model=SummaryResponse, status_code=status.HTTP_200_OK)
async def generate_summary_endpoint(payload: AISummaryRequest, db: DBSession = Depends(get_db)):
    """
    Takes session_id, fetches saved answers, calls Gemini/fallback,
    evaluates red flags, saves summary to DB, and returns structured JSON.
    """
    session_id = payload.session_id
    session_obj = db.query(Session).filter(Session.id == session_id).first()
    if not session_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found."
        )

    # 1. Fetch saved answers
    answers_query = db.query(Answer).filter(Answer.session_id == session_id).all()
    answers_list = [
        {"question_id": a.question_id, "answer": a.answer_text, "source": a.source}
        for a in answers_query
    ]

    # 2. Fetch any uploaded documents
    docs_query = db.query(Document).filter(Document.session_id == session_id).all()
    docs_list = [
        {"filename": d.filename, "type": d.type, "text": d.text}
        for d in docs_query
    ]

    # 3. Call AI Service (with fallback guarantee)
    summary_data = await AISummaryService.generate_summary(answers=answers_list, documents=docs_list)

    # 4. Red-flag evaluation: Check if chest pain + breathlessness = yes
    # Hardcoded red flag rule (Requirement 40 & 48)
    answer_dict = {a["question_id"]: str(a["answer"]).lower() for a in answers_list}
    has_breathless = (
        "yes" in answer_dict.get("cp_breathlessness", "")
        or "yes" in answer_dict.get("cp_breathless", "")
        or "yes" in answer_dict.get("breathlessness", "")
        or any("breath" in str(v).lower() or "dyspnea" in str(v).lower() for v in answer_dict.values())
    )
    is_chest_pain = any("cp_" in q for q in answer_dict.keys()) or any("chest" in str(v).lower() for v in answer_dict.values())

    has_red_flag = is_chest_pain and has_breathless
    red_flag_msg = "PRIORITY TRIAGE ALERT — not a diagnosis" if has_red_flag else None

    # Sync into red_flags_noted list if triggered
    if has_red_flag and "PRIORITY TRIAGE ALERT: Chest pain with breathlessness reported" not in summary_data.get("red_flags_noted", []):
        summary_data.setdefault("red_flags_noted", []).append("PRIORITY TRIAGE ALERT: Chest pain with breathlessness reported")

    # 5. Persist in database
    latest_summary = db.query(Summary).filter(Summary.session_id == session_id).order_by(Summary.version.desc()).first()
    version = (latest_summary.version + 1) if latest_summary else 1

    new_summary = Summary(
        session_id=session_id,
        version=version,
        content_json=summary_data,
        status="ai_draft",
        created_at=datetime.now(timezone.utc)
    )
    db.add(new_summary)

    # Record alert if triggered
    if has_red_flag:
        alert = Alert(
            session_id=session_id,
            rule_id="RF-CHEST-BREATHLESS-01",
            severity="priority_triage",
            status="active",
            timestamp=datetime.now(timezone.utc)
        )
        db.add(alert)

    db.commit()
    db.refresh(new_summary)

    return SummaryResponse(
        id=new_summary.id,
        session_id=new_summary.session_id,
        version=new_summary.version,
        content_json=new_summary.content_json,
        status=new_summary.status,
        created_at=new_summary.created_at,
        has_red_flag_alert=has_red_flag,
        red_flag_message=red_flag_msg
    )


@router.get("/summary/{session_id}", response_model=SummaryResponse)
async def get_summary_endpoint(session_id: str, db: DBSession = Depends(get_db)):
    """
    Fetch the latest clinical summary for a given session.
    If none exists yet, automatically builds one from answers.
    """
    latest_summary = db.query(Summary).filter(Summary.session_id == session_id).order_by(Summary.version.desc()).first()
    
    # Check red flag from answers
    answers_query = db.query(Answer).filter(Answer.session_id == session_id).all()
    answer_dict = {a.question_id: str(a.answer_text).lower() for a in answers_query}
    has_breathless = "yes" in answer_dict.get("cp_breathlessness", "") or "yes" in answer_dict.get("cp_breathless", "")
    is_chest_pain = any("cp_" in q for q in answer_dict.keys()) or any("chest" in str(v).lower() for v in answer_dict.values())
    has_red_flag = is_chest_pain and has_breathless
    red_flag_msg = "PRIORITY TRIAGE ALERT — not a diagnosis" if has_red_flag else None

    if latest_summary:
        return SummaryResponse(
            id=latest_summary.id,
            session_id=latest_summary.session_id,
            version=latest_summary.version,
            content_json=latest_summary.content_json,
            status=latest_summary.status,
            created_at=latest_summary.created_at,
            has_red_flag_alert=has_red_flag,
            red_flag_message=red_flag_msg
        )

    # Auto-generate draft if session exists
    session_obj = db.query(Session).filter(Session.id == session_id).first()
    if not session_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session '{session_id}' not found.")

    answers_list = [{"question_id": a.question_id, "answer": a.answer_text, "source": a.source} for a in answers_query]
    fallback_summary = AISummaryService.build_deterministic_fallback(answers=answers_list)
    new_summary = Summary(
        session_id=session_id,
        version=1,
        content_json=fallback_summary,
        status="ai_draft",
        created_at=datetime.now(timezone.utc)
    )
    db.add(new_summary)
    db.commit()
    db.refresh(new_summary)

    return SummaryResponse(
        id=new_summary.id,
        session_id=new_summary.session_id,
        version=new_summary.version,
        content_json=new_summary.content_json,
        status=new_summary.status,
        created_at=new_summary.created_at,
        has_red_flag_alert=has_red_flag,
        red_flag_message=red_flag_msg
    )


@router.put("/summary/{id}", response_model=SummaryResponse)
async def update_summary_endpoint(id: int, payload: SummaryUpdate, db: DBSession = Depends(get_db)):
    """
    Doctor edits summary fields and confirms intake record.
    Satisfies Requirement 39.
    """
    summary_obj = db.query(Summary).filter(Summary.id == id).first()
    if not summary_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Summary with id {id} not found.")

    current_data = dict(summary_obj.content_json)
    if payload.chief_complaint is not None:
        current_data["chief_complaint"] = payload.chief_complaint
    if payload.hpi is not None:
        current_data["hpi"] = payload.hpi
    if payload.past_history is not None:
        current_data["past_history"] = payload.past_history
    if payload.allergies is not None:
        current_data["allergies"] = payload.allergies
    if payload.red_flags_noted is not None:
        current_data["red_flags_noted"] = payload.red_flags_noted

    summary_obj.content_json = current_data
    summary_obj.status = payload.status or "doctor_confirmed"
    db.commit()
    db.refresh(summary_obj)

    # Check red flags
    answers = db.query(Answer).filter(Answer.session_id == summary_obj.session_id).all()
    ans_map = {a.question_id: str(a.answer_text).lower() for a in answers}
    has_red_flag = ("yes" in ans_map.get("cp_breathlessness", "") or "yes" in ans_map.get("cp_breathless", ""))
    red_flag_msg = "PRIORITY TRIAGE ALERT — not a diagnosis" if has_red_flag else None

    return SummaryResponse(
        id=summary_obj.id,
        session_id=summary_obj.session_id,
        version=summary_obj.version,
        content_json=summary_obj.content_json,
        status=summary_obj.status,
        created_at=summary_obj.created_at,
        has_red_flag_alert=has_red_flag,
        red_flag_message=red_flag_msg
    )
