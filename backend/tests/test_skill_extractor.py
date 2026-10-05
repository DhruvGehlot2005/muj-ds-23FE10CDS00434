"""
@file backend/tests/test_skill_extractor.py
@description Unit tests for deterministic skill extraction, alias normalization, and categorization.
@module backend.tests
"""

from backend.app.services.skill_extractor import SkillExtractor


def test_extract_canonical_skills():
    """Test extracting standard skills from text."""
    text = "Experienced in Python, PostgreSQL, Docker, and React for full-stack engineering."
    extractor = SkillExtractor()
    result = extractor.extract_skills(text)

    skills = result["explicit_skills"]
    assert "Python" in skills
    assert "PostgreSQL" in skills
    assert "Docker" in skills
    assert "React" in skills
    assert result["total_skills_count"] >= 4


def test_alias_normalization():
    """Test resolving skill aliases to their canonical vocabulary names."""
    text = "Developed frontend with JS and backend with Golang, deployed on k8s and GCP."
    extractor = SkillExtractor()
    result = extractor.extract_skills(text)

    skills = result["explicit_skills"]
    assert "JavaScript" in skills  # normalized from JS
    assert "Go" in skills          # normalized from Golang
    assert "Kubernetes" in skills  # normalized from k8s
    assert "Google Cloud" in skills # normalized from GCP


def test_duplicate_skills_deduplicated():
    """Test multiple mentions of the same skill or its alias produce one canonical item."""
    text = "Python developer. Used python for 3 years. Building python apps."
    extractor = SkillExtractor()
    result = extractor.extract_skills(text)

    python_mentions = [s for s in result["explicit_skills"] if s == "Python"]
    assert len(python_mentions) == 1


def test_categorization():
    """Test that detected skills are mapped into their appropriate categories."""
    text = "Built web apps with Django, stored data in MongoDB, and wrote scripts in Python."
    extractor = SkillExtractor()
    result = extractor.extract_skills(text)

    categorized = result["categorized_skills"]
    assert "Programming Languages" in categorized
    assert "Python" in categorized["Programming Languages"]
    assert "Databases" in categorized
    assert "MongoDB" in categorized["Databases"]
