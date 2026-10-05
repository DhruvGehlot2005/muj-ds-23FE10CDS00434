"""
@file backend/tests/test_resume_quality.py
@description Unit tests for deterministic Structural Completeness scoring.
@module backend.tests
"""

from backend.app.services.resume_quality import calculate_structural_completeness


def test_complete_sections():
    """Test completeness score when all core and standard sections are present."""
    all_sections = [
        "CONTACT",
        "EDUCATION",
        "SKILLS",
        "PROJECTS",
        "EXPERIENCE",
        "SUMMARY",
        "CERTIFICATIONS",
        "ACHIEVEMENTS",
    ]
    result = calculate_structural_completeness(all_sections)
    assert result["completeness_score"] == 100
    assert len(result["missing_sections"]) == 0
    assert "SKILLS" in result["present_sections"]
    assert "EDUCATION" in result["present_sections"]


def test_missing_core_sections():
    """Test completeness score penalizes missing core sections (like SKILLS or EDUCATION)."""
    partial_sections = ["CONTACT", "SUMMARY"]
    result = calculate_structural_completeness(partial_sections)
    assert result["completeness_score"] < 50
    assert "SKILLS" in result["missing_sections"]
    assert "EDUCATION" in result["missing_sections"]
    assert "PROJECTS" in result["missing_sections"]


def test_empty_sections():
    """Test completeness score is 0 when no sections are detected."""
    result = calculate_structural_completeness([])
    assert result["completeness_score"] == 0
    assert len(result["present_sections"]) == 0
    assert len(result["missing_sections"]) == 4  # Core sections


def test_optional_missing_sections():
    """Test that certifications and achievements are categorized as optional missing."""
    core_only = ["CONTACT", "EDUCATION", "SKILLS", "PROJECTS"]
    result = calculate_structural_completeness(core_only)
    assert "CERTIFICATIONS" in result["optional_missing_sections"]
    assert "ACHIEVEMENTS" in result["optional_missing_sections"]
    # Score should still be solid for a student/fresher
    assert result["completeness_score"] >= 80
