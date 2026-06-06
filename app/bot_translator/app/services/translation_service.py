from __future__ import annotations

import asyncio
import logging

from langchain_core.runnables import Runnable

from app.core.exceptions import TranslationError
from app.langchain.chain import build_translation_chain
from app.langchain.splitter import build_text_splitter

logger = logging.getLogger(__name__)


class TranslationService:
    def __init__(
        self,
        chunk_size: int = 2000,
        chunk_overlap: int = 200,
        max_concurrent: int = 5,
    ) -> None:
        self._chain: Runnable | None = None
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._max_concurrent = max_concurrent
        self._splitter = build_text_splitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def _ensure_chain(self) -> Runnable:
        if self._chain is None:
            logger.info("Building translation chain...")
            self._chain = build_translation_chain()
        return self._chain

    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
    ) -> str:
        chain = self._ensure_chain()

        if not text.strip():
            logger.warning("Empty text received for translation")
            return ""

        chunks = self._splitter.split_text(text)
        logger.info(
            "Translating %d chars split into %d chunks (src=%s, tgt=%s)",
            len(text), len(chunks), source_lang, target_lang,
        )

        if not chunks:
            return ""

        translated_chunks: list[str] = []

        semaphore = asyncio.Semaphore(self._max_concurrent)

        async def translate_chunk(chunk: str) -> str:
            async with semaphore:
                try:
                    result = await chain.ainvoke({
                        "source_lang": source_lang,
                        "target_lang": target_lang,
                        "chunk": chunk,
                    })
                    return result
                except Exception as e:
                    logger.error("Chunk translation failed: %s", e)
                    raise TranslationError(f"Chunk translation failed: {e}") from e

        tasks = [translate_chunk(c) for c in chunks]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, res in enumerate(results):
            if isinstance(res, Exception):
                logger.error("Chunk %d/%d failed, using original text", i + 1, len(chunks))
                translated_chunks.append(chunks[i])
            else:
                translated_chunks.append(res)

        full_translation = "\n\n".join(translated_chunks)
        logger.info(
            "Translation complete: %d chars → %d chars",
            len(text), len(full_translation),
        )

        return full_translation
