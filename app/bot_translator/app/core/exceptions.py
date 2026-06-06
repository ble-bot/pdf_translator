class PDFTranslatorError(Exception):
    """Base exception for the PDF Translator application."""


class PDFParseError(PDFTranslatorError):
    """Raised when PDF parsing fails."""


class OCRError(PDFTranslatorError):
    """Raised when OCR processing fails."""


class LanguageDetectionError(PDFTranslatorError):
    """Raised when language detection fails."""


class TranslationError(PDFTranslatorError):
    """Raised when the translation pipeline fails."""


class RenderError(PDFTranslatorError):
    """Raised when document rendering/export fails."""


class FileValidationError(PDFTranslatorError):
    """Raised when file validation fails (size, type, etc.)."""


class TelegramError(PDFTranslatorError):
    """Raised when Telegram API interaction fails."""
