"""
@file extractor.py
@description Secure text extraction from PDF and DOCX documents with size and MIME validation
@module backend.app.services.extractor
"""

import io
import os
import re
from typing import Tuple
import bleach
import pymupdf  # PyMuPDF
from docx import Document

from backend.app.config import settings
from backend.app.utils.logger import logger


class ExtractionError(Exception):
    """Custom exception raised when document extraction fails or input is invalid."""

    def __init__(self, message: str, code: str = "EXTRACTION_FAILED"):
        super().__init__(message)
        self.message = message
        self.code = code


def sanitize_text(text: str) -> str:
    """
    Sanitizes raw extracted text by removing control characters, stripping HTML,
    and normalizing whitespace.

    @param text: Raw extracted string
    @return Clean, normalized UTF-8 string
    """
    if not text:
        return ""

    # Remove null bytes and non-printable control characters (except newline, tab, carriage return)
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Strip HTML tags
    cleaned = bleach.clean(cleaned, tags=[], strip=True)

    # Normalize excessive blank lines and whitespace
    cleaned = re.sub(r"\r\n|\r", "\n", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)

    return cleaned.strip()


def validate_file_metadata(filename: str, file_size: int) -> str:
    """
    Validates file extension and size constraints.

    @param filename: Uploaded filename
    @param file_size: Uploaded file size in bytes
    @return Normalized file extension (pdf or docx)
    @raises ExtractionError: If validation fails
    """
    if not filename:
        raise ExtractionError("No filename provided.", code="INVALID_FILENAME")

    # Guard against path traversal
    base_name = os.path.basename(filename)
    ext = os.path.splitext(base_name)[1].lower().strip(".")

    if ext not in ["pdf", "docx"]:
        raise ExtractionError(
            f"Unsupported file format '{ext}'. Only PDF and DOCX are allowed.",
            code="UNSUPPORTED_FORMAT",
        )

    if file_size <= 0:
        raise ExtractionError("Uploaded file is empty (0 bytes).", code="EMPTY_FILE")

    if file_size > settings.max_upload_size_bytes:
        raise ExtractionError(
            f"File exceeds maximum allowed size of {settings.max_upload_size_mb}MB.",
            code="FILE_TOO_LARGE",
        )

    return ext


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extracts text from PDF bytes using PyMuPDF (fitz).

    @param file_bytes: In-memory PDF byte stream
    @return Cleaned text string
    @raises ExtractionError: If PDF is corrupted or unreadable
    """
    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
        if doc.page_count == 0:
            raise ExtractionError("PDF document has no pages.", code="EMPTY_DOCUMENT")

        extracted_pages = []
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            page_text = page.get_text("text")
            if page_text:
                extracted_pages.append(page_text)

        doc.close()
        full_text = "\n\n".join(extracted_pages)
        sanitized = sanitize_text(full_text)

        if not sanitized:
            raise ExtractionError(
                "PDF contains no extractable text. Scanned images or password-protected PDFs are not supported.",
                code="NO_TEXT_FOUND",
            )
        return sanitized
    except ExtractionError:
        raise
    except Exception as exc:
        logger.error(f"PDF extraction error: {type(exc).__name__}")
        raise ExtractionError(
            "Failed to parse PDF document. Ensure the file is a valid, uncorrupted PDF.",
            code="PDF_PARSE_ERROR",
        ) from exc


def extract_text_from_docx(file_bytes: bytes) -> str:
    """
    Extracts text from DOCX bytes using python-docx.

    @param file_bytes: In-memory DOCX byte stream
    @return Cleaned text string
    @raises ExtractionError: If DOCX is corrupted or unreadable
    """
    try:
        file_stream = io.BytesIO(file_bytes)
        doc = Document(file_stream)

        extracted_lines = []
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if text:
                extracted_lines.append(text)

        # Also extract table text
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    extracted_lines.append(row_text)

        full_text = "\n".join(extracted_lines)
        sanitized = sanitize_text(full_text)

        if not sanitized:
            raise ExtractionError(
                "DOCX document contains no extractable text.",
                code="NO_TEXT_FOUND",
            )
        return sanitized
    except ExtractionError:
        raise
    except Exception as exc:
        logger.error(f"DOCX extraction error: {type(exc).__name__}")
        raise ExtractionError(
            "Failed to parse DOCX document. Ensure the file is a valid DOCX file.",
            code="DOCX_PARSE_ERROR",
        ) from exc


def extract_document_text(filename: str, file_bytes: bytes) -> str:
    """
    Validates and extracts sanitized text from an in-memory document (PDF or DOCX).

    @param filename: Name of uploaded file
    @param file_bytes: Raw binary content
    @return Clean extracted text
    """
    ext = validate_file_metadata(filename, len(file_bytes))
    if ext == "pdf":
        return extract_text_from_pdf(file_bytes)
    elif ext == "docx":
        return extract_text_from_docx(file_bytes)
    else:
        raise ExtractionError(f"Unsupported extension: {ext}", code="UNSUPPORTED_FORMAT")
