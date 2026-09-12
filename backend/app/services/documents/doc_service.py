"""
Document File Management Service
Handles local disk / object storage persistence for uploaded medical reports.
"""

import os
from pathlib import Path

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)

class DocumentService:
    @staticmethod
    def save_file(filename: str, content: bytes) -> str:
        """Save uploaded document file to local storage directory."""
        file_path = UPLOAD_DIR / filename
        with open(file_path, "wb") as f:
            f.write(content)
        return str(file_path)
