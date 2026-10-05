"""
@file test_extractor.py
@description Unit tests for document extraction, validation, and sanitization
@module backend.tests.test_extractor
"""

import os
import pytest
from backend.app.services.extractor import (
    ExtractionError,
    extract_document_text,
    sanitize_text,
    validate_file_metadata,
)

TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "tests")


def test_sanitize_text():
    """Verifies that control chars and HTML tags are stripped properly."""
    raw = "Hello\x00 World! <script>alert('xss')</script><b>Bold</b>\r\n\r\n\n\nTest"
    cleaned = sanitize_text(raw)
    assert "\x00" not in cleaned
    assert "<script>" not in cleaned
    assert "<b>" not in cleaned
    assert "Bold" in cleaned
    assert "Hello World!" in cleaned


def test_validate_file_metadata_valid_pdf():
    """Verifies valid PDF extension passes metadata validation."""
    ext = validate_file_metadata("resume.pdf", 1024)
    assert ext == "pdf"


def test_validate_file_metadata_valid_docx():
    """Verifies valid DOCX extension passes metadata validation."""
    ext = validate_file_metadata("resume.docx", 2048)
    assert ext == "docx"


def test_validate_file_metadata_invalid_extension():
    """Verifies unsupported file extension raises ExtractionError."""
    with pytest.raises(ExtractionError) as exc_info:
        validate_file_metadata("resume.txt", 1024)
    assert exc_info.value.code == "UNSUPPORTED_FORMAT"


def test_validate_file_metadata_empty_file():
    """Verifies zero byte file raises ExtractionError."""
    with pytest.raises(ExtractionError) as exc_info:
        validate_file_metadata("resume.pdf", 0)
    assert exc_info.value.code == "EMPTY_FILE"


def test_validate_file_metadata_oversized_file():
    """Verifies oversized file (>10MB) raises ExtractionError."""
    with pytest.raises(ExtractionError) as exc_info:
        validate_file_metadata("resume.pdf", 15 * 1024 * 1024)
    assert exc_info.value.code == "FILE_TOO_LARGE"


def test_extract_valid_pdf():
    """Tests text extraction from valid sample PDF fixture."""
    pdf_path = os.path.join(TEST_DATA_DIR, "sample_resume.pdf")
    with open(pdf_path, "rb") as f:
        content = f.read()

    text = extract_document_text("sample_resume.pdf", content)
    assert "Alex Morgan" in text
    assert "State University" in text
    assert "FastAPI" in text


def test_extract_valid_docx():
    """Tests text extraction from valid sample DOCX fixture."""
    docx_path = os.path.join(TEST_DATA_DIR, "sample_resume.docx")
    with open(docx_path, "rb") as f:
        content = f.read()

    text = extract_document_text("sample_resume.docx", content)
    assert "Taylor Reed" in text
    assert "Data Science" in text
    assert "Scikit-learn" in text


def test_extract_corrupted_pdf():
    """Tests that corrupted PDF bytes raise ExtractionError."""
    corrupted_bytes = b"%PDF-1.4 corrupted gibberish content that cannot be parsed"
    with pytest.raises(ExtractionError) as exc_info:
        extract_document_text("corrupted.pdf", corrupted_bytes)
    assert exc_info.value.code in ["PDF_PARSE_ERROR", "NO_TEXT_FOUND"]
