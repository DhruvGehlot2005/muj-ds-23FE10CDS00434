"""
@file backend/tests/test_contact_extractor.py
@description Unit tests for deterministic contact extraction.
@module backend.tests
"""

from backend.app.services.contact_extractor import ContactExtractor


def test_extract_all_contacts():
    """Test extracting email, phone, linkedin, and github from header text."""
    text = (
        "Alice Smith\n"
        "Email: alice.smith@example.com | Phone: +1 (555) 234-5678\n"
        "https://www.linkedin.com/in/alicesmith | github.com/alicesmith\n"
        "Computer Science Graduate\n"
    )
    extractor = ContactExtractor()
    contacts = extractor.extract_contacts(text)

    assert contacts["email"] == "alice.smith@example.com"
    assert contacts["phone"] is not None
    assert "linkedin.com/in/alicesmith" in contacts["linkedin"]
    assert "github.com/alicesmith" in contacts["github"]


def test_extract_missing_contacts():
    """Test extractor returns None when contact fields are not present."""
    text = "Just plain resume text about projects and skills without any contact info."
    extractor = ContactExtractor()
    contacts = extractor.extract_contacts(text)

    assert contacts["email"] is None
    assert contacts["phone"] is None
    assert contacts["linkedin"] is None
    assert contacts["github"] is None


def test_extract_empty_string():
    """Test extractor handles empty input safely."""
    extractor = ContactExtractor()
    contacts = extractor.extract_contacts("")
    assert contacts["email"] is None
    assert contacts["phone"] is None
