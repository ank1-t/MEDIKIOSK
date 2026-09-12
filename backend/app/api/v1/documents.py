"""
Document Upload, OCR, and Timeline Endpoints
Handles:
- POST /api/documents (file upload, OCR extraction, fallback text support)
- GET /api/documents (list documents)
- GET /api/documents/{id}
- GET /api/timeline/{session_id} (chronological history view)
"""

import uuid
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models.models import Document, Session, Answer, Patient
from app.schemas.schemas import DocumentResponse, TimelineItem
from app.services.documents.doc_service import DocumentService
from app.services.ocr.ocr_service import OCRService

router = APIRouter(tags=["Documents & Timeline"])

@router.post("/documents", status_code=status.HTTP_201_CREATED, response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
    type: Optional[str] = Form("prescription"),
    manual_text: Optional[str] = Form(None),
    db: DBSession = Depends(get_db)
):
    """
    Upload a patient medical document (Prescription/Report).
    1. Saves the file to local uploads folder.
    2. Inserts a row in the documents table.
    3. Runs OCR (or uses manual fallback text if provided / needed).
    4. Extracts key entities (medicines, dates).
    5. Updates document text and returns structured response.
    """
    # Ensure session exists or create a demo session if none provided
    if session_id:
        session_obj = db.query(Session).filter(Session.id == session_id).first()
        if not session_obj:
            # Auto-provision or reject; here we create session gracefully for standalone testing
            demo_patient = db.query(Patient).first()
            if not demo_patient:
                demo_patient = Patient(demo_id="DEMO-PT-001", language="en")
                db.add(demo_patient)
                db.commit()
                db.refresh(demo_patient)

            session_obj = Session(
                id=session_id,
                patient_id=demo_patient.id,
                status="in_progress",
                started_at=datetime.now(timezone.utc)
            )
            db.add(session_obj)
            db.commit()
            db.refresh(session_obj)
    else:
        # Create a new session automatically
        demo_patient = db.query(Patient).first()
        if not demo_patient:
            demo_patient = Patient(demo_id=f"DEMO-PT-{uuid.uuid4().hex[:4].upper()}", language="en")
            db.add(demo_patient)
            db.commit()
            db.refresh(demo_patient)

        session_id = f"sess_{uuid.uuid4().hex[:12]}"
        session_obj = Session(
            id=session_id,
            patient_id=demo_patient.id,
            status="in_progress",
            started_at=datetime.now(timezone.utc)
        )
        db.add(session_obj)
        db.commit()
        db.refresh(session_obj)

    # Read uploaded file content
    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    # Save to local storage
    saved_filename, saved_file_path = DocumentService.save_file(file.filename or "prescription.jpg", content)

    # Insert row in documents table
    new_doc = Document(
        session_id=session_obj.id,
        filename=saved_filename,
        file_path=saved_file_path,
        type=type or "prescription",
        uploaded_at=datetime.now(timezone.utc),
        text=None
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    # Run OCR & entity extraction
    extraction_result = await OCRService.extract_text_and_entities(
        file_bytes=content,
        filename=new_doc.filename,
        manual_fallback_text=manual_text
    )

    # Update document record with extracted text
    new_doc.text = extraction_result.get("raw_text") or manual_text or ""
    db.commit()
    db.refresh(new_doc)

    return DocumentResponse(
        id=new_doc.id,
        session_id=new_doc.session_id,
        filename=new_doc.filename,
        file_path=new_doc.file_path,
        type=new_doc.type,
        uploaded_at=new_doc.uploaded_at,
        text=new_doc.text,
        extracted_data=extraction_result
    )


@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(session_id: Optional[str] = None, db: DBSession = Depends(get_db)):
    """Retrieve uploaded documents, optionally filtered by session_id."""
    query = db.query(Document)
    if session_id:
        query = query.filter(Document.session_id == session_id)
    docs = query.order_by(Document.uploaded_at.desc()).all()

    results = []
    for d in docs:
        extracted = OCRService.extract_entities_from_text(d.text or "")
        results.append(DocumentResponse(
            id=d.id,
            session_id=d.session_id,
            filename=d.filename,
            file_path=d.file_path,
            type=d.type,
            uploaded_at=d.uploaded_at,
            text=d.text,
            extracted_data={
                "raw_text": d.text or "",
                "entities": extracted,
                "medicines": [m["raw_match"] for m in extracted.get("medicines", [])],
                "document_date": extracted.get("primary_date")
            }
        ))
    return results


@router.get("/documents/{id}", response_model=DocumentResponse)
async def get_document(id: int, db: DBSession = Depends(get_db)):
    """Fetch single document by database ID."""
    doc = db.query(Document).filter(Document.id == id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {id} not found."
        )

    extracted = OCRService.extract_entities_from_text(doc.text or "")
    return DocumentResponse(
        id=doc.id,
        session_id=doc.session_id,
        filename=doc.filename,
        file_path=doc.file_path,
        type=doc.type,
        uploaded_at=doc.uploaded_at,
        text=doc.text,
        extracted_data={
            "raw_text": doc.text or "",
            "entities": extracted,
            "medicines": [m["raw_match"] for m in extracted.get("medicines", [])],
            "document_date": extracted.get("primary_date")
        }
    )


@router.get("/timeline/{session_id}", response_model=List[TimelineItem])
@router.get("/documents/timeline/{session_id}", response_model=List[TimelineItem])
async def get_timeline(session_id: str, db: DBSession = Depends(get_db)):
    """
    Display uploaded documents and intake events in a chronological timeline sorted by date.
    Satisfies Requirement 36.
    """
    items: List[TimelineItem] = []

    # 1. Fetch documents for this session
    docs = db.query(Document).filter(Document.session_id == session_id).all()
    for d in docs:
        extracted = OCRService.extract_entities_from_text(d.text or "")
        date_str = extracted.get("primary_date") or d.uploaded_at.strftime("%Y-%m-%d")
        meds = [m["raw_match"] for m in extracted.get("medicines", [])]

        items.append(TimelineItem(
            id=f"doc_{d.id}",
            item_type="document",
            title=f"Uploaded {d.type.replace('_', ' ').capitalize()}: {d.filename}",
            date_or_time=date_str,
            timestamp=d.uploaded_at,
            details={
                "document_id": d.id,
                "filename": d.filename,
                "file_path": d.file_path,
                "type": d.type,
                "text": d.text,
                "medicines": meds,
                "clinic_name": extracted.get("clinic_name"),
                "doctor_name": extracted.get("doctor_name")
            }
        ))

    # 2. Fetch answered intake questions for this session
    answers = db.query(Answer).filter(Answer.session_id == session_id).all()
    for a in answers:
        items.append(TimelineItem(
            id=f"ans_{a.id}",
            item_type="answer",
            title=f"Intake Response ({a.question_id})",
            date_or_time=a.timestamp.strftime("%Y-%m-%d %H:%M"),
            timestamp=a.timestamp,
            details={
                "question_id": a.question_id,
                "answer_text": a.answer_text,
                "source": a.source
            }
        ))

    # Sort chronological: oldest to newest (or newest first; sorting by timestamp)
    items.sort(key=lambda x: x.timestamp)
    return items
