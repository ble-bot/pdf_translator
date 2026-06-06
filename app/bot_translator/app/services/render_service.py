from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from app.config import settings
from app.core.exceptions import RenderError
from app.models.document import TranslatedDocument

logger = logging.getLogger(__name__)


class RenderService:
    async def render_pdf(
        self,
        translated_doc: TranslatedDocument,
        output_filename: str,
    ) -> Path:
        output_path = settings.OUTPUTS_DIR / output_filename

        try:
            await self._convert_via_pandoc(
                markdown=translated_doc.translated_markdown,
                output_path=output_path,
            )
        except Exception as e:
            logger.error("Pandoc PDF rendering failed: %s", e)
            raise RenderError(f"Failed to render PDF: {e}") from e

        translated_doc.output_path = output_path
        logger.info("PDF rendered: %s", output_path)
        return output_path

    async def render_markdown_file(
        self,
        translated_doc: TranslatedDocument,
        output_filename: str,
    ) -> Path:
        output_path = settings.OUTPUTS_DIR / output_filename.replace(".pdf", ".md")

        output_path.write_text(translated_doc.translated_markdown, encoding="utf-8")
        logger.info("Markdown saved: %s", output_path)
        return output_path

    async def _convert_via_pandoc(
        self,
        markdown: str,
        output_path: Path,
    ) -> None:
        temp_md = output_path.with_suffix(".tmp.md")
        temp_md.write_text(markdown, encoding="utf-8")

        try:
            proc = await asyncio.create_subprocess_exec(
                "pandoc",
                str(temp_md),
                "--pdf-engine=weasyprint",
                "-o", str(output_path),
                "--from=markdown",
                "--to=pdf",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown pandoc error"
                logger.error("Pandoc failed (code %d): %s", proc.returncode, error_msg)
                raise RenderError(f"Pandoc conversion failed: {error_msg}")

            logger.info("Pandoc PDF generated: %s", output_path)

        finally:
            if temp_md.exists():
                temp_md.unlink()
