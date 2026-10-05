"""
@file backend/app/services/contact_extractor.py
@description Deterministic extraction of contact information (email, phone, LinkedIn, GitHub) from resume text.
@module backend/app/services
"""

import re
from typing import Dict, Optional


# Precompiled regex patterns for contact extraction
EMAIL_PATTERN = re.compile(
    r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    re.IGNORECASE
)

# Supports standard international, US, UK, and Indian phone number formats
PHONE_PATTERN = re.compile(
    r"(?:(?:\+|00)\d{1,3}[\s.-]?)?(?:\(?\d{2,5}\)?[\s.-]?)?\d{3,5}[\s.-]?\d{4}(?:\s*(?:ext|x|ext.)\s*\d{1,5})?",
    re.IGNORECASE
)

LINKEDIN_PATTERN = re.compile(
    r"(?:https?://)?(?:www\.)?linkedin\.com/(?:in|profile)/[a-zA-Z0-9_.-]+/?",
    re.IGNORECASE
)

GITHUB_PATTERN = re.compile(
    r"(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_.-]+/?",
    re.IGNORECASE
)


class ContactExtractor:
    """
    Deterministic contact extractor for resume text.
    Extracts email, phone, LinkedIn URL, and GitHub URL using strict regex patterns.
    Ensures zero PII is logged or fabricated.
    """

    def __init__(self) -> None:
        """Initialize contact extraction patterns."""
        self.email_regex = EMAIL_PATTERN
        self.phone_regex = PHONE_PATTERN
        self.linkedin_regex = LINKEDIN_PATTERN
        self.github_regex = GITHUB_PATTERN

    def extract_contacts(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extract contact details from resume text.

        Args:
            text: Raw or preprocessed resume text.

        Returns:
            Dict containing email, phone, linkedin, and github (or None if not found).
        """
        if not text or not text.strip():
            return {
                "email": None,
                "phone": None,
                "linkedin": None,
                "github": None,
            }

        # 1. Email extraction
        email = None
        email_match = self.email_regex.search(text)
        if email_match:
            candidate_email = email_match.group(0).strip(".,;:()")
            # Avoid obvious false positives like file extensions
            if not candidate_email.endswith((".png", ".jpg", ".pdf", ".docx", ".zip")):
                email = candidate_email

        # 2. LinkedIn extraction
        linkedin = None
        linkedin_match = self.linkedin_regex.search(text)
        if linkedin_match:
            candidate_li = linkedin_match.group(0).strip(".,;:()")
            if not candidate_li.startswith("http"):
                candidate_li = f"https://{candidate_li}"
            linkedin = candidate_li

        # 3. GitHub extraction
        github = None
        github_match = self.github_regex.search(text)
        if github_match:
            candidate_gh = github_match.group(0).strip(".,;:()")
            # Ignore general github.com links without username
            parts = candidate_gh.rstrip("/").split("/")
            if len(parts) >= 2 and parts[-1].lower() not in ("github.com", "features", "explore"):
                if not candidate_gh.startswith("http"):
                    candidate_gh = f"https://{candidate_gh}"
                github = candidate_gh

        # 4. Phone extraction
        phone = None
        # Search in the top 30% of resume or first 1500 chars where contact info usually lives
        header_text = text[:1500] if len(text) > 1500 else text
        phone_matches = self.phone_regex.findall(header_text)
        for candidate in phone_matches:
            cleaned_candidate = candidate.strip(".,;:()")
            # Remove non-digit characters to check digit count
            digits = re.sub(r"\D", "", cleaned_candidate)
            # Valid phone numbers typically have 10 to 15 digits
            if 10 <= len(digits) <= 15:
                # Avoid dates like 2020-2024 or years
                if not re.match(r"^(19|20)\d{2}[\s.-]*(19|20)\d{2}$", cleaned_candidate.strip()):
                    phone = cleaned_candidate
                    break

        return {
            "email": email,
            "phone": phone,
            "linkedin": linkedin,
            "github": github,
        }
