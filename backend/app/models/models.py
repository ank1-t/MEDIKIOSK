"""
SQLAlchemy database models for MediKiosk
Tables: patients, sessions, answers, documents, entities, summaries, alerts, audit_events
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    demo_id = Column(String(50), unique=True, index=True, nullable=False)
    language = Column(String(10), default="en")
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship("Session", back_populates="patient")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String(50), primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    status = Column(String(20), default="in_progress")  # in_progress, completed, abandoned
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    patient = relationship("Patient", back_populates="sessions")
    answers = relationship("Answer", back_populates="session")
    documents = relationship("Document", back_populates="session")
    summaries = relationship("Summary", back_populates="session")
    alerts = relationship("Alert", back_populates="session")


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), ForeignKey("sessions.id"), nullable=False)
    question_id = Column(String(50), nullable=False)
    answer = Column(Text, nullable=False)
    source = Column(String(20), default="touch")  # touch, voice
    timestamp = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="answers")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), ForeignKey("sessions.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    type = Column(String(50))  # prescription, lab_report, discharge_summary
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    text = Column(Text, nullable=True)

    session = relationship("Session", back_populates="documents")
    entities = relationship("ExtractedEntity", back_populates="document")


class ExtractedEntity(Base):
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    type = Column(String(50), nullable=False)  # medication, lab_test, diagnosis, date
    value = Column(String(255), nullable=False)
    confidence = Column(String(20), default="medium")
    source = Column(String(100), nullable=True)

    document = relationship("Document", back_populates="entities")


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), ForeignKey("sessions.id"), nullable=False)
    version = Column(Integer, default=1)
    content_json = Column(JSON, nullable=False)
    status = Column(String(30), default="ai_draft")  # ai_draft, doctor_edited, doctor_confirmed
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="summaries")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), ForeignKey("sessions.id"), nullable=False)
    rule_id = Column(String(50), nullable=False)
    severity = Column(String(20), default="warning")  # info, warning, priority_triage
    status = Column(String(20), default="active")
    timestamp = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="alerts")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), index=True, nullable=False)
    actor = Column(String(50), default="patient")  # patient, doctor, system
    action = Column(String(100), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
