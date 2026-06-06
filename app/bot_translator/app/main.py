from __future__ import annotations

import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import router as api_router
from app.bot.router import router as bot_router
from app.config import settings
from app.core.exceptions import PDFTranslatorError
from app.core.logging import setup_logging
from app.services.telegram_service import TelegramService
from app.utils.file_helpers import ensure_dirs

logger = logging.getLogger(__name__)

bot: Bot | None = None
dp: Dispatcher | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global bot, dp
    setup_logging()
    ensure_dirs()

    logger.info("Starting PDF Translator AI Bot...")

    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    telegram_service = TelegramService(bot)
    dp.workflow_data.update(telegram_service=telegram_service)
    dp.include_router(bot_router)

    polling_task = asyncio.create_task(dp.start_polling(bot))

    yield

    polling_task.cancel()
    try:
        await polling_task
    except asyncio.CancelledError:
        pass

    if bot:
        await bot.session.close()

    logger.info("Shutdown complete.")


app = FastAPI(
    title="PDF Translator AI Bot",
    description="Telegram bot for PDF translation using Gemini 2.5 Pro",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(api_router, prefix="/api/v1")


@app.exception_handler(PDFTranslatorError)
async def pdf_translator_error_handler(request: Request, exc: PDFTranslatorError):
    logger.error("Unhandled application error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)},
    )


@app.get("/")
async def root():
    return {
        "app": "PDF Translator AI Bot",
        "version": "1.0.0",
        "status": "running",
    }


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
