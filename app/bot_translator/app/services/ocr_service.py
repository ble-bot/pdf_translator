from __future__ import annotations

import asyncio
import logging
from functools import partial
from pathlib import Path

from rapidocr_onnxruntime import RapidOCR

from app.core.exceptions import OCRError

logger = logging.getLogger(__name__)


class OCRService:
    def __init__(self) -> None:
        self._engine: RapidOCR | None = None

    def _ensure_engine(self) -> RapidOCR:
        if self._engine is None:
            logger.info("Initializing RapidOCR engine...")
            self._engine = RapidOCR()
        return self._engine

    async def extract_text(self, image_path: Path) -> str:
        engine = self._ensure_engine()
        loop = asyncio.get_running_loop()

        try:
            result, elapsed = await loop.run_in_executor(
                None, partial(engine, str(image_path))
            )
        except Exception as e:
            logger.error("OCR failed for %s: %s", image_path, e)
            raise OCRError(f"OCR processing failed: {e}") from e

        if not result:
            logger.info("No text detected in %s", image_path)
            return ""

        texts = []
        for item in result:
            if len(item) >= 2 and item[1]:
                texts.append(str(item[1]))

        extracted = " ".join(texts)
        logger.debug(
            "OCR extracted %d chars from %s in %.2fs",
            len(extracted), image_path, elapsed,
        )
        return extracted

    async def extract_text_batch(
        self, image_paths: list[Path]
    ) -> dict[int, str]:
        """Run OCR on multiple images. Returns dict mapping index to text."""
        tasks = [self.extract_text(p) for p in image_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        output: dict[int, str] = {}
        for i, (path, result) in enumerate(zip(image_paths, results)):
            if isinstance(result, Exception):
                logger.warning("OCR failed for %s: %s", path, result)
                output[i] = ""
            else:
                output[i] = result

        return output
