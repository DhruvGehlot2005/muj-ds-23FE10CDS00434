"""
@file validator.py
@description Heuristic validation to verify that extracted text represents a plausible resume
@module backend.app.services.validator
"""

import re
from typing import List, Tuple

# Common resume section headers and structural keywords (case-insensitive regex patterns)
RESUME_INDICATORS: List[Tuple[str, str]] = [
    ("contact", r"\b(email|phone|mobile|tel|linkedin|github|portfolio|address|contact)\b"),
    ("education", r"\b(education|university|college|degree|bachelor|master|phd|b\.?tech|b\.?s\.?|m\.?s\.?|gpa|coursework)\b"),
    ("experience", r"\b(experience|employment|work history|internship|intern|job|career|responsibilities)\b"),
    ("skills", r"\b(skills|technical skills|proficiencies|technologies|programming|frameworks|tools)\b"),
    ("projects", r"\b(projects|personal projects|academic projects|capstone|portfolio|open source)\b"),
    ("achievements", r"\b(achievements|certifications|awards|honors|publications|extracurricular)\b"),
]

MIN_CHARACTER_COUNT = 150
MIN_WORD_COUNT = 30
MIN_MATCHED_CATEGORIES = 2


class ResumeValidationError(Exception):
    """Exception raised when document text fails resume heuristic validation."""

    def __init__(self, message: str, code: str = "NOT_A_RESUME"):
        super().__init__(message)
        self.message = message
        self.code = code


def validate_resume_content(text: str) -> bool:
    """
    Validates whether the provided text has structural and semantic characteristics
    of a genuine resume.

    @param text: Extracted and sanitized document text
    @return True if valid resume
    @raises ResumeValidationError: If text fails minimum size, word count, or indicator tests
    """
    if not text or not text.strip():
        raise ResumeValidationError(
            "Resume content is empty. Please provide a document with extractable text.",
            code="EMPTY_RESUME",
        )

    clean = text.strip()
    if len(clean) < MIN_CHARACTER_COUNT:
        raise ResumeValidationError(
            f"Extracted content is too short ({len(clean)} characters). A valid resume must contain more detailed information.",
            code="RESUME_TOO_SHORT",
        )

    words = re.findall(r"\b\w+\b", clean)
    if len(words) < MIN_WORD_COUNT:
        raise ResumeValidationError(
            f"Extracted content contains only {len(words)} words, which is insufficient for an ATS evaluation.",
            code="INSUFFICIENT_CONTENT",
        )

    # Check for presence of typical resume categories
    matched_categories = []
    text_lower = clean.lower()

    for category, pattern in RESUME_INDICATORS:
        if re.search(pattern, text_lower):
            matched_categories.append(category)

    if len(matched_categories) < MIN_MATCHED_CATEGORIES:
        raise ResumeValidationError(
            "The uploaded document does not appear to be a resume. It lacks standard resume sections such as Education, Experience, Skills, or Projects.",
            code="NOT_A_RESUME",
        )

    return True
