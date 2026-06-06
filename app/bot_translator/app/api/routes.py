from __future__ import annotations

import time
from pathlib import Path

from fastapi import APIRouter

router = APIRouter()

_start_time: float = time.time()

_translation_count: int = 0
_error_count: int = 0


def increment_translation_count() -> None:
    global _translation_count
    _translation_count += 1


def increment_error_count() -> None:
    global _error_count
    _error_count += 1


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "uptime_seconds": int(time.time() - _start_time),
    }


@router.get("/status")
async def status():
    md_files = list(Path("storage/outputs").glob("*.md")) if Path("storage/outputs").exists() else []
    pdf_files = list(Path("storage/outputs").glob("*.pdf")) if Path("storage/outputs").exists() else []

    return {
        "status": "running",
        "uptime_seconds": int(time.time() - _start_time),
        "translations_completed": _translation_count,
        "errors": _error_count,
        "outputs": {
            "markdown": len(md_files),
            "pdf": len(pdf_files),
        },
    }
