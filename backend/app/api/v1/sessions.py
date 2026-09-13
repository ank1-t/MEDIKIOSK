"""
Session and Intake Answers Endpoints
Endpoints:
- POST /api/sessions
- POST /api/sessions/{id}/answers
- GET /api/sessions/{id}
"""

import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models.models import Patient, Session, Answer
from app.schemas.schemas import SessionCreate, SessionResponse, AnswerCreate, AnswerItem

router = APIRouter(tags=["Sessions"])

@router.post("/sessions", status_code=status.HTTP_201_CREATED)
async def create_session(payload: Optional[SessionCreate] = None, db: DBSession = Depends(get_db)):
    """
    Create a new patient kiosk session.
    Returns the session ID and metadata.
    """
    demo_id = payload.demo_id if (payload and payload.demo_id) else f"DEMO-PT-{uuid.uuid4().hex[:4].upper()}"
    language = payload.language if (payload and payload.language) else "en"

    # Find or create demo patient
    patient = db.query(Patient).filter(Patient.demo_id == demo_id).first()
    if not patient:
        patient = Patient(demo_id=demo_id, language=language)
        db.add(patient)
        db.commit()
        db.refresh(patient)

    # Create session
    session_id = f"sess_{uuid.uuid4().hex[:12]}"
    new_session = Session(
        id=session_id,
        patient_id=patient.id,
        status="in_progress",
        started_at=datetime.now(timezone.utc)
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return {
        "id": new_session.id,
        "session_id": new_session.id,
        "patient_id": patient.id,
        "demo_id": patient.demo_id,
        "language": patient.language,
        "status": new_session.status,
        "started_at": new_session.started_at
    }


@router.post("/sessions/{id}/answers", status_code=status.HTTP_201_CREATED)
async def save_answer(id: str, payload: Dict[str, Any], db: DBSession = Depends(get_db)):
    """
    Save one or multiple question + answers to the database for a given session.
    Supports both single answer object and {'answers': [...]} batch.
    """
    session_obj = db.query(Session).filter(Session.id == id).first()
    if not session_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id '{id}' not found."
        )

    # If batch answers provided: {"answers": [...]}
    if "answers" in payload and isinstance(payload["answers"], list):
        created_answers = []
        for a in payload["answers"]:
            qid = a.get("question_id")
            val = a.get("answer_text") or a.get("answer") or ""
            src = a.get("source") or "touch"
            if qid and val:
                ans_record = Answer(
                    session_id=session_obj.id,
                    question_id=qid,
                    answer_text=str(val),
                    source=src,
                    timestamp=datetime.now(timezone.utc)
                )
                db.add(ans_record)
                created_answers.append(ans_record)
        db.commit()
        return {
            "status": "success",
            "saved_count": len(created_answers),
            "message": f"Saved {len(created_answers)} answers successfully."
        }

    # Otherwise single answer
    qid = payload.get("question_id")
    text_value = payload.get("answer_text") or payload.get("answer")
    if not text_value or not qid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Field 'question_id' and 'answer_text' or 'answer' must be provided."
        )

    new_answer = Answer(
        session_id=session_obj.id,
        question_id=qid,
        answer_text=str(text_value),
        source=payload.get("source") or "touch",
        timestamp=datetime.now(timezone.utc)
    )
    db.add(new_answer)
    db.commit()
    db.refresh(new_answer)

    return {
        "id": new_answer.id,
        "session_id": new_answer.session_id,
        "question_id": new_answer.question_id,
        "answer_text": new_answer.answer_text,
        "source": new_answer.source,
        "timestamp": new_answer.timestamp,
        "message": "Answer saved successfully."
    }


@router.get("/sessions/{id}", response_model=SessionResponse)
async def get_session(id: str, db: DBSession = Depends(get_db)):
    """
    Fetch session details and all saved answers for that session.
    """
    session_obj = db.query(Session).filter(Session.id == id).first()
    if not session_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id '{id}' not found."
        )

    patient = session_obj.patient

    return SessionResponse(
        id=session_obj.id,
        session_id=session_obj.id,
        patient_id=session_obj.patient_id,
        demo_id=patient.demo_id if patient else "UNKNOWN",
        language=patient.language if patient else "en",
        status=session_obj.status,
        started_at=session_obj.started_at,
        completed_at=session_obj.completed_at,
        answers=[
            AnswerItem(
                id=a.id,
                question_id=a.question_id,
                answer_text=a.answer_text,
                source=a.source,
                timestamp=a.timestamp
            )
            for a in session_obj.answers
        ]
    )
