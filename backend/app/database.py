"""
Database connection and session configuration for SQLite / PostgreSQL
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./medikiosk.db")

# connect_args={"check_same_thread": False} is required for SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency for obtaining database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
