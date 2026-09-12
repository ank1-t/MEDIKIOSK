"""
Document File Management Service
Handles local disk / object storage persistence for uploaded medical reports.
"""

import os
import uuid
from pathlib import Path
from typing import Tuple

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)

class DocumentService:
    @staticmethod
    def save_file(filename: str, content: bytes) -> Tuple[str, str]:
        """
        Save uploaded document file to local storage directory.
        Returns unique stored filename and full path.
        """
        extension = Path(filename).suffix or ".jpg"
        clean_stem = "".join(c for c in Path(filename).stem if c.isalnum() or c in ("-", "_")).strip()
        unique_filename = f"{clean_stem}_{uuid.uuid4().hex[:8]}{extension}"
        file_path = UPLOAD_DIR / unique_filename

        with open(file_path, "wb") as f:
            f.write(content)
        return unique_filename, str(file_path).replace("\\", "/")
