import pytest
from app.services.language_service import LanguageService


class TestLanguageService:
    @pytest.fixture
    def service(self):
        return LanguageService(low_accuracy=True)

    def test_detect_english(self, service):
        result = service.detect("Hello world, this is a test document.")
        assert result == "English"

    def test_detect_spanish(self, service):
        result = service.detect("Hola mundo, este es un documento de prueba.")
        assert result == "Spanish"

    def test_detect_french(self, service):
        result = service.detect("Bonjour le monde, ceci est un document de test.")
        assert result == "French"

    def test_detect_german(self, service):
        result = service.detect("Hallo Welt, dies ist ein Testdokument.")
        assert result == "German"

    def test_empty_text(self, service):
        with pytest.raises(Exception):
            service.detect("")
