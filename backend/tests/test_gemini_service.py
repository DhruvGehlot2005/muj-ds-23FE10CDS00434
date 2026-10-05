"""
@file backend/tests/test_gemini_service.py
@description Unit tests for LLM orchestration service, mock fallback, and schema validation.
@module backend.tests
"""

import pytest
from backend.app.models.schemas import OverallAnalysis, RoleAnalysis
from backend.app.services.llm_service import LLMService, LLMServiceError


def test_mock_mode_overall_analysis():
    """Test LLM service operates in mock mode when key is absent."""
    service = LLMService()
    service.is_mock = True

    evidence = {
        "resume_sections": {"SKILLS": ["Python, Docker"]},
        "explicit_skills": ["Python", "Docker"],
        "structural_completeness": {"score": 85},
    }

    result = service.analyze_overall(evidence)
    assert isinstance(result, OverallAnalysis)
    assert result.overall_quality_score > 0
    assert len(result.strengths) > 0


def test_mock_mode_target_role():
    """Test LLM service target role analysis in mock mode."""
    service = LLMService()
    service.is_mock = True

    evidence = {"explicit_skills": ["Python", "FastAPI"]}
    result = service.analyze_target_role(evidence, "Backend Engineer")
    assert isinstance(result, RoleAnalysis)
    assert result.target_role == "Backend Engineer"
    assert result.role_compatibility_score > 0


def test_extract_json_substring():
    """Test regex extraction of JSON wrapped in markdown or conversational text."""
    service = LLMService()
    raw = "Here is the analysis:\n```json\n{\"overall_quality_score\": 85, \"clarity_score\": 80, \"professionalism_score\": 90, \"ats_compatibility_score\": 85, \"strengths\": [], \"weaknesses\": [], \"recommendations\": []}\n```\nHope this helps!"
    extracted = service._extract_json_substring(raw)
    assert extracted.startswith("{")
    assert extracted.endswith("}")


def test_parse_json_malformed_raises_error():
    """Test malformed JSON string raises LLMServiceError."""
    service = LLMService()
    with pytest.raises(LLMServiceError) as exc_info:
        service._parse_json_model("This is completely invalid non-json", OverallAnalysis)
    assert exc_info.value.code == "MALFORMED_JSON"
