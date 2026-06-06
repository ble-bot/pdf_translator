from __future__ import annotations

import logging
from pathlib import Path

from aiogram import Bot
from aiogram.types import FSInputFile, Message

logger = logging.getLogger(__name__)


class TelegramService:
    def __init__(self, bot: Bot) -> None:
        self._bot = bot

    async def download_pdf(self, message: Message, download_path: Path) -> Path:
        document = message.document
        if document is None:
            raise ValueError("No document in message")

        file = await self._bot.get_file(document.file_id)
        file_path = download_path / document.file_name or "document.pdf"
        await self._bot.download_file(file.file_path, file_path)

        logger.info("PDF downloaded: %s (%d bytes)", file_path, document.file_size or 0)
        return file_path

    async def send_message(
        self,
        chat_id: int,
        text: str,
        reply_markup=None,
    ) -> Message:
        return await self._bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
        )

    async def send_document(
        self,
        chat_id: int,
        file_path: Path,
        caption: str | None = None,
    ) -> Message:
        input_file = FSInputFile(str(file_path))
        return await self._bot.send_document(
            chat_id=chat_id,
            document=input_file,
            caption=caption,
        )

    async def edit_message(
        self,
        chat_id: int,
        message_id: int,
        text: str,
        reply_markup=None,
    ) -> Message:
        return await self._bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=reply_markup,
        )
