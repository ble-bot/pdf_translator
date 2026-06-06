from __future__ import annotations

import logging
from lingua import LanguageDetectorBuilder, Language

from app.core.exceptions import LanguageDetectionError

logger = logging.getLogger(__name__)

LANGUAGE_NAME_MAP: dict[Language, str] = {
    Language.ENGLISH: "English",
    Language.SPANISH: "Spanish",
    Language.FRENCH: "French",
    Language.GERMAN: "German",
    Language.ITALIAN: "Italian",
    Language.PORTUGUESE: "Portuguese",
    Language.DUTCH: "Dutch",
    Language.RUSSIAN: "Russian",
    Language.JAPANESE: "Japanese",
    Language.CHINESE: "Chinese",
    Language.KOREAN: "Korean",
    Language.ARABIC: "Arabic",
    Language.HINDI: "Hindi",
    Language.TURKISH: "Turkish",
    Language.POLISH: "Polish",
    Language.INDONESIAN: "Indonesian",
    Language.VIETNAMESE: "Vietnamese",
    Language.THAI: "Thai",
    Language.CZECH: "Czech",
    Language.SWEDISH: "Swedish",
}

SUPPORTED_LANGUAGES = sorted(LANGUAGE_NAME_MAP.values())


class LanguageService:
    def __init__(self, low_accuracy: bool = False) -> None:
        builder = LanguageDetectorBuilder.from_languages(*list(LANGUAGE_NAME_MAP.keys()))
        if low_accuracy:
            builder.with_low_accuracy_mode()
        self._detector = builder.build()

    def detect(self, text: str) -> str:
        if not text or not text.strip():
            raise LanguageDetectionError("Empty text for language detection.")

        detected = self._detector.detect_language_of(text)

        if detected is None:
            logger.warning("Language detection returned None, defaulting to English")
            return "English"

        name = LANGUAGE_NAME_MAP.get(detected)
        if name is None:
            logger.warning(
                "Detected language %s not in map, using name", detected.name
            )
            return detected.name.title()

        logger.info("Detected language: %s", name)
        return name
