"""
Pydantic schemas for MediKiosk API validation
"""

from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class HealthResponse(BaseModel):
    status: str = "ok"


class SessionCreate(BaseModel):
    demo_id: Optional[str] = Field(None, description="Demo Patient Identifier e.g. DEMO-PT-001")
    language: Optional[str] = Field("en", description="Language code: en, hi")


class AnswerItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    question_id: str
    answer_text: str
    source: Optional[str] = "touch"
    timestamp: Optional[datetime] = None


class AnswerCreate(BaseModel):
    question_id: str
    answer_text: Optional[str] = None
    answer: Optional[str] = None  # support both 'answer' and 'answer_text' keys
    source: Optional[str] = "touch"

    def get_text(self) -> str:
        return self.answer_text if self.answer_text is not None else (self.answer or "")


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    patient_id: int
    demo_id: str
    language: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    answers: List[AnswerItem] = []


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: str
    filename: str
    file_path: Optional[str] = None
    type: str
    uploaded_at: datetime
    text: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None


class TimelineItem(BaseModel):
    id: str
    item_type: str  # "document" | "answer"
    title: str
    date_or_time: str
    timestamp: datetime
    details: Dict[str, Any]
