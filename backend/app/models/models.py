"""
SQLAlchemy database models for MediKiosk
Core tables: patients, sessions, answers, documents
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    demo_id = Column(String(50), unique=True, index=True, nullable=False)
    language = Column(String(10), default="en")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    sessions = relationship("Session", back_populates="patient")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String(50), primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    status = Column(String(20), default="in_progress")  # in_progress, completed, abandoned
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    patient = relationship("Patient", back_populates="sessions")
    answers = relationship("Answer", back_populates="session", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="session", cascade="all, delete-orphan")
    summaries = relationship("Summary", back_populates="session", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="session", cascade="all, delete-orphan")


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), ForeignKey("sessions.id"), nullable=False)
    question_id = Column(String(50), nullable=False)
    answer_text = Column(Text, nullable=False)
    source = Column(String(20), default="touch")  # touch, voice
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("Session", back_populates="answers")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), ForeignKey("sessions.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)
    type = Column(String(50), default="medical_record")  # prescription, lab_report, discharge_summary
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    text = Column(Text, nullable=True)

    session = relationship("Session", back_populates="documents")


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), ForeignKey("sessions.id"), nullable=False)
    version = Column(Integer, default=1)
    content_json = Column(JSON, nullable=False)
    status = Column(String(30), default="ai_draft")  # ai_draft, doctor_edited, doctor_confirmed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("Session", back_populates="summaries")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), ForeignKey("sessions.id"), nullable=False)
    rule_id = Column(String(50), nullable=False)
    severity = Column(String(20), default="warning")  # info, warning, priority_triage
    status = Column(String(20), default="active")
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("Session", back_populates="alerts")
