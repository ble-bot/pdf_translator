from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from docling.document_converter import DocumentConverter

from app.config import settings
from app.core.exceptions import PDFParseError
from app.models.document import ExtractedDocument, PageImage, TableData

logger = logging.getLogger(__name__)


class PDFService:
    def __init__(self) -> None:
        self._converter: DocumentConverter | None = None

    def _ensure_converter(self) -> DocumentConverter:
        if self._converter is None:
            logger.info("Initializing Docling DocumentConverter...")
            self._converter = DocumentConverter()
        return self._converter

    async def extract(self, file_path: Path, original_filename: str) -> ExtractedDocument:
        converter = self._ensure_converter()
        loop = asyncio.get_running_loop()

        logger.info("Parsing PDF: %s", file_path)

        try:
            logger.debug("Starting Docling conversion...")
            result = await loop.run_in_executor(
                None, converter.convert, str(file_path)
            )
            logger.debug("Docling conversion finished.")
        except Exception as e:
            logger.error("Docling conversion failed: %s", e)
            raise PDFParseError(f"Failed to parse PDF: {e}") from e

        doc = result.document
        total_pages = len(doc.pages) if doc.pages else 0
        logger.info("PDF parsed successfully: %d pages", total_pages)

        logger.debug("Extracting texts...")
        texts: list[str] = []
        for item in doc.texts:
            texts.append(item.text)

        logger.debug("Extracting tables...")
        tables: list[TableData] = []
        for table in doc.tables:
            df = table.export_to_dataframe()
            page = table.prov[0].page_no if table.prov else 0
            tables.append(
                TableData(
                    page_number=page,
                    markdown=df.to_markdown(index=False),
                    csv=df.to_csv(index=False),
                )
            )

        logger.debug("Extracting images...")
        images: list[PageImage] = []
        for i, picture in enumerate(doc.pictures):
            page = picture.prov[0].page_no if picture.prov else 0
            image_path = settings.OUTPUTS_DIR / f"img_{page}_{i}.png"
            try:
                if picture.image and picture.image.pil_image:
                    pil_img = picture.image.pil_image
                    pil_img.save(str(image_path), format="PNG")
            except Exception as e:
                logger.warning("Failed to save image page_%d_img_%d: %s", page, i, e)

            images.append(
                PageImage(
                    page_number=page,
                    image_path=image_path,
                )
            )

        logger.debug("Exporting to markdown...")
        full_markdown = doc.export_to_markdown()
        logger.debug("Markdown export finished.")

        return ExtractedDocument(
            file_path=file_path,
            original_filename=original_filename,
            total_pages=total_pages,
            texts=texts,
            tables=tables,
            images=images,
            full_markdown=full_markdown,
        )
