import tempfile
from pathlib import Path

import pytest
from app.utils.file_helpers import validate_pdf, generate_unique_filename
from app.core.exceptions import FileValidationError


class TestFileHelpers:
    def test_validate_pdf_valid(self):
        with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
            f.write(b"%PDF-1.4 test content")
            f.flush()
            validate_pdf(Path(f.name))

    def test_validate_pdf_invalid_extension(self):
        with tempfile.NamedTemporaryFile(suffix=".txt") as f:
            with pytest.raises(FileValidationError):
                validate_pdf(Path(f.name))

    def test_generate_unique_filename(self):
        name = generate_unique_filename("test document.pdf")
        assert "test document" in name
        assert "_" in name

    def test_generate_unique_filename_special_chars(self):
        name = generate_unique_filename("my/file:name.pdf")
        assert "file" in name or "name" in name
        assert "_" in name
