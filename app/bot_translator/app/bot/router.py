from __future__ import annotations

import logging
from pathlib import Path

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.bot.keyboards import build_language_keyboard, build_cancel_keyboard
from app.bot.states import TranslationStates
from app.config import settings
from app.core.exceptions import (
    FileValidationError,
    PDFParseError,
    OCRError,
    TranslationError,
    RenderError,
)
from app.models.document import ExtractedDocument, TranslatedDocument
from app.services.language_service import LanguageService
from app.services.ocr_service import OCRService
from app.services.pdf_service import PDFService
from app.services.render_service import RenderService
from app.services.telegram_service import TelegramService
from app.services.translation_service import TranslationService
from app.utils.file_helpers import (
    validate_pdf,
    generate_unique_filename,
    cleanup_file,
    cleanup_document_resources,
)

logger = logging.getLogger(__name__)

router = Router()

pdf_service = PDFService()
ocr_service = OCRService()
language_service = LanguageService()
translation_service = TranslationService()
render_service = RenderService()


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "🤖 *PDF Translator Bot*\n\n"
        "Envíame un archivo PDF y lo traduciré al idioma que elijas.\n\n"
        "Pasos:\n"
        "1. Envía el PDF\n"
        "2. Selecciona el idioma destino\n"
        "3. Recibe el PDF traducido\n\n"
        "*Límite:* {} MB por archivo".format(settings.MAX_FILE_SIZE_MB),
        parse_mode="Markdown",
    )


@router.message(F.document)
async def handle_document(message: Message, state: FSMContext, telegram_service: TelegramService) -> None:
    if message.document is None:
        return

    if not message.document.file_name or not message.document.file_name.lower().endswith(".pdf"):
        await message.answer("⚠️ Solo acepto archivos PDF. Envíame un documento .pdf válido.")
        return

    if message.document.file_size and message.document.file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        await message.answer(
            f"⚠️ Archivo demasiado grande ({message.document.file_size / 1024 / 1024:.1f} MB). "
            f"Límite: {settings.MAX_FILE_SIZE_MB} MB."
        )
        return

    status_msg = await message.answer("📥 Descargando PDF...")

    try:
        unique_name = generate_unique_filename(message.document.file_name)
        download_path = settings.DOWNLOADS_DIR / unique_name
        download_path.mkdir(parents=True, exist_ok=True)
        pdf_path = await telegram_service.download_pdf(message, download_path)
    except Exception as e:
        logger.error("Download failed: %s", e)
        await status_msg.edit_text("❌ Error al descargar el archivo. Intenta de nuevo.")
        return

    await status_msg.edit_text("📄 Analizando documento...")

    try:
        validate_pdf(pdf_path)
        doc = await pdf_service.extract(pdf_path, message.document.file_name)
    except FileValidationError as e:
        await status_msg.edit_text(f"⚠️ {e}")
        cleanup_file(pdf_path)
        return
    except PDFParseError as e:
        logger.error("PDF parse failed: %s", e)
        await status_msg.edit_text("❌ No pude analizar el PDF. ¿Es un documento válido?")
        cleanup_file(pdf_path)
        return

    await status_msg.edit_text("🔍 Extrayendo texto de imágenes...")

    try:
        if doc.images:
            ocr_results = await ocr_service.extract_text_batch([img.image_path for img in doc.images])
            doc.ocr_texts = ocr_results
    except OCRError as e:
        logger.warning("OCR error (non-fatal): %s", e)
        doc.ocr_texts = {}

    await status_msg.edit_text("🌐 Detectando idioma...")

    try:
        combined_text = doc.get_combined_text()
        detected_lang = language_service.detect(combined_text)
        doc.detected_language = detected_lang
    except Exception as e:
        logger.warning("Language detection failed: %s", e)
        doc.detected_language = "English"

    await state.set_data({"doc": doc.model_dump(), "pdf_path": str(pdf_path)})
    await state.set_state(TranslationStates.waiting_for_language)

    await status_msg.edit_text(
        f"🌍 *Idioma detectado:* {doc.detected_language}\n\n"
        "¿A qué idioma deseas traducir el documento?",
        parse_mode="Markdown",
        reply_markup=build_language_keyboard(exclude_lang=doc.detected_language),
    )


@router.callback_query(StateFilter(TranslationStates.waiting_for_language), F.data.startswith("lang_"))
async def handle_language_selection(callback: CallbackQuery, state: FSMContext, telegram_service: TelegramService) -> None:
    target_lang = callback.data.replace("lang_", "")

    data = await state.get_data()
    doc_dict = data.get("doc")
    if doc_dict is None:
        await callback.message.answer("⚠️ Sesión expirada. Envía el PDF de nuevo.")
        await state.clear()
        await callback.answer()
        return

    doc = ExtractedDocument(**doc_dict)
    pdf_path = Path(data["pdf_path"])
    output_path: Path | None = None

    await callback.message.edit_text(f"🔄 Traduciendo a *{target_lang}*...\n\nEsto puede tomar unos minutos.", parse_mode="Markdown")
    await state.set_state(TranslationStates.processing)
    await callback.answer()

    try:
        combined_text = doc.get_combined_text()

        translated = await translation_service.translate(
            text=combined_text,
            source_lang=doc.detected_language or "English",
            target_lang=target_lang,
        )

        translated_doc = TranslatedDocument(
            original_filename=doc.original_filename,
            source_language=doc.detected_language or "English",
            target_language=target_lang,
            translated_markdown=translated,
        )

        await callback.message.edit_text("📃 Generando PDF final...")

        output_stem = generate_unique_filename(doc.original_filename)
        output_filename = f"{output_stem}_{target_lang.lower()}.pdf"

        output_path = await render_service.render_pdf(translated_doc, output_filename)

        await telegram_service.send_document(
            chat_id=callback.message.chat.id,
            file_path=output_path,
            caption=f"✅ *Traducción completada*\n\n"
                    f"📄 {doc.original_filename}\n"
                    f"🌐 {doc.detected_language} → {target_lang}",
        )

        await callback.message.edit_text("✅ ¡Traducción completada! PDF enviado arriba.")

    except TranslationError as e:
        logger.error("Translation failed: %s", e)
        await callback.message.edit_text("❌ Error durante la traducción. Intenta de nuevo.")
    except RenderError as e:
        logger.error("Render failed: %s", e)
        await callback.message.edit_text("❌ Error al generar el PDF final.")
    except Exception as e:
        logger.exception("Unexpected error during translation flow")
        await callback.message.edit_text("❌ Ocurrió un error inesperado.")
    finally:
        # Full cleanup: input PDF, extracted images, and output PDF
        cleanup_document_resources(pdf_path, [img.image_path for img in doc.images])
        if output_path:
            cleanup_file(output_path)
        await state.clear()


@router.callback_query(F.data == "cancel")
async def handle_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text("❌ Operación cancelada.")
    await callback.answer()


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    current = await state.get_state()
    if current is not None:
        await state.clear()
        await message.answer("❌ Operación cancelada.")
    else:
        await message.answer("No hay ninguna operación activa.")
