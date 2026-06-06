from __future__ import annotations

import os
import shutil
import uuid
from pathlib import Path

from app.config import settings
from app.core.exceptions import FileValidationError


ALLOWED_EXTENSIONS = {".pdf"}
MAX_FILE_SIZE_BYTES = settings.MAX_FILE_SIZE_MB * 1024 * 1024


def validate_pdf(file_path: Path) -> None:
    if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise FileValidationError(f"Invalid file type: {file_path.suffix}. Only PDF is allowed.")

    file_size = file_path.stat().st_size
    if file_size > MAX_FILE_SIZE_BYTES:
        raise FileValidationError(
            f"File too large: {file_size / 1024 / 1024:.1f} MB. "
            f"Maximum allowed: {settings.MAX_FILE_SIZE_MB} MB."
        )


def ensure_dirs() -> None:
    settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    settings.DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    settings.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def generate_unique_filename(original: str) -> str:
    stem = Path(original).stem
    safe_stem = "".join(c if c.isalnum() or c in " _-" else "_" for c in stem)
    return f"{safe_stem}_{uuid.uuid4().hex[:8]}"


def cleanup_file(path: Path) -> None:
    try:
        if path.exists():
            os.remove(path)
    except OSError:
        pass


def cleanup_directory(dir_path: Path) -> None:
    try:
        if dir_path.exists():
            shutil.rmtree(dir_path)
    except OSError:
        pass


def cleanup_document_resources(doc_path: Path, image_paths: list[Path] = None) -> None:
    """Cleans up the PDF file and all extracted images."""
    cleanup_file(doc_path)
    if image_paths:
        for img_path in image_paths:
            cleanup_file(img_path)
    
    # Also cleanup the directory if it's empty
    if doc_path.parent.exists() and not any(doc_path.parent.iterdir()):
        cleanup_directory(doc_path.parent)
