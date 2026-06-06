from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.services.language_service import SUPPORTED_LANGUAGES


def build_language_keyboard(exclude_lang: str | None = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    # Prioritize Spanish if it's not the source language
    languages = list(SUPPORTED_LANGUAGES)
    if "Spanish" in languages:
        languages.remove("Spanish")
        if exclude_lang != "Spanish":
            languages.insert(0, "Spanish")

    for lang in languages:
        if lang == exclude_lang:
            continue
        
        display_name = "Español 🇪🇸" if lang == "Spanish" else lang
        builder.button(text=display_name, callback_data=f"lang_{lang}")

    builder.adjust(2, repeat=True)
    builder.row(InlineKeyboardButton(text="❌ Cancelar", callback_data="cancel"))

    return builder.as_markup()


def build_cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Cancelar", callback_data="cancel")
    return builder.as_markup()
