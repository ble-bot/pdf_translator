from __future__ import annotations

from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


class PageImage(BaseModel):
    """Represents an image extracted from a PDF page."""
    page_number: int
    image_path: Path
    image_bytes: Optional[bytes] = None


class TableData(BaseModel):
    """Represents a table extracted from a PDF."""
    page_number: int
    markdown: str
    csv: str


class ExtractedDocument(BaseModel):
    """Full extracted content from a PDF document."""
    file_path: Path
    original_filename: str
    total_pages: int
    texts: list[str] = Field(default_factory=list)
    tables: list[TableData] = Field(default_factory=list)
    images: list[PageImage] = Field(default_factory=list)
    full_markdown: str = ""
    detected_language: Optional[str] = None
    ocr_texts: dict[int, str] = Field(default_factory=dict)

    def get_combined_text(self) -> str:
        """Combines full markdown with OCR results."""
        combined = self.full_markdown
        for ocr_text in self.ocr_texts.values():
            if ocr_text.strip():
                combined += "\n\n" + ocr_text
        return combined


class TranslatedDocument(BaseModel):
    """The translated version of a document."""
    original_filename: str
    source_language: str
    target_language: str
    translated_markdown: str
    output_path: Optional[Path] = None
