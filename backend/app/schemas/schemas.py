"""
Pydantic schemas for MediKiosk API validation
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class SessionCreate(BaseModel):
    demo_id: str = Field(..., description="Demo Patient Identifier e.g. DEMO-PT-001")
    language: str = Field("en", description="Language code: en, hi")


class SessionResponse(BaseModel):
    session_id: str
    patient_id: int
    demo_id: str
    language: str
    status: str
    started_at: datetime


class AnswerCreate(BaseModel):
    question_id: str
    answer: str
    source: str = Field("touch", description="'touch' or 'voice'")


class QuestionOption(BaseModel):
    id: str
    label_en: str
    label_hi: str


class Question(BaseModel):
    id: str
    type: str  # yes_no, single_choice, multi_choice, number, date, text
    text_en: str
    text_hi: str
    audio_en: Optional[str] = None
    audio_hi: Optional[str] = None
    options: Optional[List[QuestionOption]] = None
    mandatory: bool = True


class SummaryContent(BaseModel):
    chief_complaint: str
    history_of_present_illness: str
    past_medical_history: List[str] = []
    medications: List[str] = []
    allergies: List[str] = []
    family_history: List[str] = []
    personal_history: List[str] = []
    review_of_systems: Dict[str, Any] = {}
    investigations: List[str] = []
    alerts: List[str] = []


class SummaryResponse(BaseModel):
    id: int
    session_id: str
    version: int
    status: str
    content: SummaryContent
    disclaimer: str = "AI-generated draft — physician verification required"
