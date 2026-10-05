"""
@file test_llm_service.py
@description Unit tests for LLM orchestration, prompt parsing, and JSON validation
@module backend.tests.test_llm_service
"""

import json
import pytest
from backend.app.models.schemas import (
    JobMatchAnalysis,
    OverallAnalysis,
    RoleAnalysis,
)
from backend.app.services.llm_service import LLMService, LLMServiceError


@pytest.fixture
def llm_service():
    """Initializes LLMService in mock mode."""
    return LLMService()


def test_prompts_loaded(llm_service):
    """Verifies that all four core prompt templates are loaded from prompts.txt."""
    assert "OVERALL_RESUME_ANALYSIS" in llm_service.prompts
    assert "TARGET_ROLE_ANALYSIS" in llm_service.prompts
    assert "JOB_DESCRIPTION_ANALYSIS" in llm_service.prompts
    assert "RESUME_JD_MATCHING" in llm_service.prompts


def test_analyze_overall_returns_valid_model(llm_service):
    """Verifies overall analysis returns a valid OverallAnalysis Pydantic instance."""
    result = llm_service.analyze_overall("Sample resume text for evaluation")
    assert isinstance(result, OverallAnalysis)
    assert 0 <= result.overall_score <= 100
    assert 0 <= result.completeness_score <= 100
    assert 0 <= result.clarity_score <= 100
    assert 0 <= result.ats_score <= 100
    assert len(result.strengths) > 0
    assert len(result.recommendations) > 0


def test_analyze_target_role_returns_valid_model(llm_service):
    """Verifies target role analysis returns a valid RoleAnalysis Pydantic instance."""
    result = llm_service.analyze_target_role("Sample resume text", "Software Developer")
    assert isinstance(result, RoleAnalysis)
    assert result.target_role == "Software Developer"
    assert 0 <= result.role_match_score <= 100
    assert len(result.matching_areas) > 0


def test_analyze_job_match_returns_valid_model(llm_service):
    """Verifies JD match returns a valid JobMatchAnalysis Pydantic instance."""
    result = llm_service.analyze_job_match("Resume text", "Job Description text")
    assert isinstance(result, JobMatchAnalysis)
    assert 0 <= result.match_score <= 100
    assert len(result.matching_skills) > 0
    assert len(result.missing_skills) > 0


def test_extract_json_substring_with_markdown(llm_service):
    """Verifies markdown backticks are cleanly stripped to extract raw JSON."""
    raw = "```json\n{\"overall_score\": 90, \"completeness_score\": 85, \"clarity_score\": 80, \"professionalism_score\": 88, \"ats_score\": 82, \"section_evaluations\": {}, \"strengths\": [], \"weaknesses\": [], \"missing_sections\": [], \"recommendations\": []}\n```"
    model = llm_service._parse_json_model(raw, OverallAnalysis)
    assert model.overall_score == 90


def test_parse_malformed_json_raises_error(llm_service):
    """Verifies malformed JSON string raises LLMServiceError with MALFORMED_JSON."""
    bad_json = "This is not valid JSON at all: {foo: bar}"
    with pytest.raises(LLMServiceError) as exc_info:
        llm_service._parse_json_model(bad_json, OverallAnalysis)
    assert exc_info.value.code == "MALFORMED_JSON"


def test_parse_invalid_schema_raises_error(llm_service):
    """Verifies JSON that fails Pydantic validation raises SCHEMA_VALIDATION_ERROR."""
    invalid_schema = json.dumps({"overall_score": 150})  # 150 violates le=100
    with pytest.raises(LLMServiceError) as exc_info:
        llm_service._parse_json_model(invalid_schema, OverallAnalysis)
    assert exc_info.value.code == "SCHEMA_VALIDATION_ERROR"


def test_yaml_prompts_loaded_properly(llm_service):
    """Verifies YAML-based prompts load non-empty strings for all prompt roles."""
    assert len(llm_service.prompts.get("system", "")) > 50
    assert len(llm_service.prompts.get("overall", "")) > 50
    assert len(llm_service.prompts.get("role", "")) > 50
    assert len(llm_service.prompts.get("jd", "")) > 50


def test_yaml_configuration_loaded():
    """Verifies that Settings loads properties from config.yaml properly."""
    from backend.app.config import settings

    assert settings.backend_host in ["127.0.0.1", "localhost"]
    assert settings.backend_port == 8000
    assert settings.max_upload_size_mb >= 1
    assert settings.section_classifier_confidence_threshold == 0.60


def test_prompt_placeholders_fully_replaced(llm_service):
    """Verifies that prompt construction replaces both {evidence_json} and {resume_text}."""
    structured_evidence = {
        "resume_text": "Experienced software engineer specializing in Python and React.",
        "resume_sections": {"SKILLS": ["Python", "React", "TypeScript"]},
        "explicit_skills": ["Python", "React"],
    }

    template = llm_service.prompts.get("overall", "")
    evidence_json = json.dumps(structured_evidence, indent=2)
    raw_text = structured_evidence.get("resume_text", "")

    prompt = (
        template.replace("{evidence_json}", evidence_json)
        .replace("{resume_text}", raw_text or evidence_json)
    )

    assert "{evidence_json}" not in prompt
    assert "{resume_text}" not in prompt
    assert "Experienced software engineer" in prompt


