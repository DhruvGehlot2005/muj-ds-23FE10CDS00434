"""
@file backend/tests/test_text_similarity.py
@description Unit tests for statistical TF-IDF cosine similarity and JD skill comparison.
@module backend.tests
"""

from backend.app.services.text_similarity import TextSimilarityEngine


def test_identical_texts_high_similarity():
    """Test identical texts yield near 1.0 similarity."""
    text = "We are seeking a Python developer with FastAPI, PostgreSQL, and Docker experience."
    engine = TextSimilarityEngine()
    sim = engine.compute_lexical_similarity(text, text)
    assert sim >= 0.99


def test_completely_different_texts_low_similarity():
    """Test disjoint texts yield low or 0.0 similarity."""
    t1 = "Organic chemistry molecular synthesis and crystallization."
    t2 = "Kubernetes cluster container orchestration with Helm charts."
    engine = TextSimilarityEngine()
    sim = engine.compute_lexical_similarity(t1, t2)
    assert sim < 0.2


def test_jd_skills_and_overlap():
    """Test deterministic matching and missing skills calculation."""
    resume_text = "Proficient in Python, React, and PostgreSQL."
    jd_text = "Looking for a candidate with Python, React, AWS, and Docker skills."

    engine = TextSimilarityEngine()
    analysis = engine.analyze_job_description(resume_text, jd_text)

    assert "Python" in analysis["matching_skills"]
    assert "React" in analysis["matching_skills"]
    assert "AWS" in analysis["missing_skills"]
    assert "Docker" in analysis["missing_skills"]
    assert analysis["lexical_similarity_score"] > 0
