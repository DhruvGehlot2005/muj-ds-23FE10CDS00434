"""
@file schemas.py
@description Strict Pydantic models for custom NLP outputs, Gemini LLM schemas, API requests, and responses.
@module backend.app.models.schemas
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------
# Custom NLP Models
# ---------------------------------------------------------

class ClassifiedBlock(BaseModel):
    """Segmented block classified by TF-IDF + Logistic Regression."""
    text: str = Field(description="Segment text")
    label: str = Field(description="Predicted section class label")
    confidence: float = Field(ge=0.0, le=1.0, description="Classifier probability confidence")


class ResumeStructureData(BaseModel):
    """Deterministic structural completeness analysis."""
    completeness_score: int = Field(ge=0, le=100, description="Structural completeness score 0-100")
    present_sections: List[str] = Field(default_factory=list, description="Mandatory/recommended sections present")
    missing_sections: List[str] = Field(default_factory=list, description="Expected core sections missing")
    optional_missing_sections: List[str] = Field(default_factory=list, description="Optional sections not detected")
    classified_blocks: List[ClassifiedBlock] = Field(default_factory=list, description="ML classified blocks")


class ContactAnalysisData(BaseModel):
    """Deterministic contact extraction results."""
    email: Optional[str] = Field(default=None, description="Extracted email address")
    phone: Optional[str] = Field(default=None, description="Extracted phone number")
    linkedin: Optional[str] = Field(default=None, description="Extracted LinkedIn profile URL")
    github: Optional[str] = Field(default=None, description="Extracted GitHub profile URL")


class SkillAnalysisData(BaseModel):
    """Deterministic explicit skill extraction and categorization."""
    explicit_skills: List[str] = Field(default_factory=list, description="Canonical skills detected")
    categorized_skills: Dict[str, List[str]] = Field(default_factory=dict, description="Skills grouped by category")
    total_skills_count: int = Field(ge=0, description="Count of unique canonical skills found")


class AchievementItem(BaseModel):
    """Detected quantitative achievement statement."""
    statement: str = Field(description="Extracted achievement statement")
    metric_type: str = Field(description="Category of metric: percentage, ranking, monetary, etc.")
    matched_text: str = Field(description="Specific quantitative token or phrase matched")


class AchievementAnalysisData(BaseModel):
    """Deterministic achievement language detection."""
    achievements_count: int = Field(ge=0, description="Total quantitative statements identified")
    achievements: List[AchievementItem] = Field(default_factory=list, description="Detected achievement items")
    detected_metric_types: List[str] = Field(default_factory=list, description="Types of metrics present")
    quantification_score: int = Field(ge=0, le=100, description="Calibrated quantification density score 0-100")


# ---------------------------------------------------------
# Gemini Semantic Outputs
# ---------------------------------------------------------

class OverallAnalysis(BaseModel):
    """Structured semantic evaluation of overall resume quality."""
    overall_quality_score: Optional[int] = Field(default=None, ge=0, le=100, description="Qualitative evaluation score 0-100")
    overall_score: Optional[int] = Field(default=None, ge=0, le=100, description="Overall score alias")
    completeness_score: Optional[int] = Field(default=85, ge=0, le=100, description="Completeness score 0-100")
    clarity_score: int = Field(default=80, ge=0, le=100, description="Clarity and readability score 0-100")
    professionalism_score: int = Field(default=85, ge=0, le=100, description="Professionalism and tone score 0-100")
    ats_compatibility_score: Optional[int] = Field(default=None, ge=0, le=100, description="ATS friendliness score 0-100")
    ats_score: Optional[int] = Field(default=None, ge=0, le=100, description="ATS score alias")
    section_evaluations: Dict[str, str] = Field(default_factory=dict, description="Section status evaluations")
    strengths: List[str] = Field(default_factory=list, description="Evidence-backed qualitative strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Evidence-backed areas for improvement")
    missing_sections: List[str] = Field(default_factory=list, description="Missing sections")
    recommendations: List[str] = Field(default_factory=list, description="Actionable recommendations")

    @model_validator(mode="before")
    @classmethod
    def sync_legacy_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "overall_score" in data and "overall_quality_score" not in data:
                data["overall_quality_score"] = data["overall_score"]
            elif "overall_quality_score" in data and "overall_score" not in data:
                data["overall_score"] = data["overall_quality_score"]

            if "ats_score" in data and "ats_compatibility_score" not in data:
                data["ats_compatibility_score"] = data["ats_score"]
            elif "ats_compatibility_score" in data and "ats_score" not in data:
                data["ats_score"] = data["ats_compatibility_score"]
        return data


class RoleAnalysis(BaseModel):
    """Structured semantic evaluation of alignment with a target job role."""
    target_role: str = Field(description="Target role evaluated against")
    role_compatibility_score: Optional[int] = Field(default=None, ge=0, le=100, description="Role alignment score 0-100")
    role_match_score: Optional[int] = Field(default=None, ge=0, le=100, description="Role match score alias")
    strengths: List[str] = Field(default_factory=list, description="Role-specific strengths")
    matching_areas: List[str] = Field(default_factory=list, description="Demonstrated matching areas")
    weaknesses: List[str] = Field(default_factory=list, description="Role-specific areas needing depth")
    weak_areas: List[str] = Field(default_factory=list, description="Weak areas")
    gaps: List[str] = Field(default_factory=list, description="Commonly expected skills/tools missing")
    missing_areas: List[str] = Field(default_factory=list, description="Missing areas")
    recommendations: List[str] = Field(default_factory=list, description="Role-specific recommendations")

    @model_validator(mode="before")
    @classmethod
    def sync_role_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "role_match_score" in data and "role_compatibility_score" not in data:
                data["role_compatibility_score"] = data["role_match_score"]
            elif "role_compatibility_score" in data and "role_match_score" not in data:
                data["role_match_score"] = data["role_compatibility_score"]

            if "matching_areas" in data and not data.get("strengths"):
                data["strengths"] = data["matching_areas"]
            elif "strengths" in data and not data.get("matching_areas"):
                data["matching_areas"] = data["strengths"]

            if "weak_areas" in data and not data.get("weaknesses"):
                data["weaknesses"] = data["weak_areas"]
            elif "weaknesses" in data and not data.get("weak_areas"):
                data["weak_areas"] = data["weaknesses"]

            if "missing_areas" in data and not data.get("gaps"):
                data["gaps"] = data["missing_areas"]
            elif "gaps" in data and not data.get("missing_areas"):
                data["missing_areas"] = data["gaps"]
        return data


class ExplicitMatchItem(BaseModel):
    """Requirement explicitly evidenced in resume."""
    requirement: str
    evidence: str


class PartialMatchItem(BaseModel):
    """Requirement partially or indirectly evidenced in resume."""
    requirement: str
    evidence: str
    gap: Optional[str] = None


class MissingRequirementItem(BaseModel):
    """Requirement not found in resume."""
    requirement: str
    importance: str = Field(default="REQUIRED", description="REQUIRED or PREFERRED")


class JobMatchAnalysis(BaseModel):
    """Hybrid lexical + semantic comparison between resume and job description."""
    lexical_similarity_score: float = Field(default=0.0, ge=0.0, le=100.0, description="TF-IDF Cosine Similarity percentage")
    tfidf_similarity: float = Field(default=0.0, ge=0.0, le=1.0, description="Raw TF-IDF Cosine Similarity 0.0-1.0")
    semantic_match_score: Optional[int] = Field(default=None, ge=0, le=100, description="Gemini semantic match score 0-100")
    match_score: Optional[int] = Field(default=None, ge=0, le=100, description="Match score alias")
    matching_skills: List[str] = Field(default_factory=list, description="Deterministic skill overlap")
    missing_skills: List[str] = Field(default_factory=list, description="Deterministic JD missing skills")
    explicit_matches: List[Any] = Field(default_factory=list, description="Semantic explicit matches")
    partial_matches: List[Any] = Field(default_factory=list, description="Semantic partial matches")
    missing_requirements: List[Any] = Field(default_factory=list, description="Semantic missing requirements")
    recommendations: List[str] = Field(default_factory=list, description="JD-tailored recommendations")

    @model_validator(mode="before")
    @classmethod
    def sync_job_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "match_score" in data and "semantic_match_score" not in data:
                data["semantic_match_score"] = data["match_score"]
            elif "semantic_match_score" in data and "match_score" not in data:
                data["match_score"] = data["semantic_match_score"]

            if "lexical_similarity_score" not in data:
                data["lexical_similarity_score"] = float(data.get("match_score", 0))
            if "tfidf_similarity" not in data:
                data["tfidf_similarity"] = round(float(data.get("lexical_similarity_score", 0)) / 100.0, 4)
        return data


# ---------------------------------------------------------
# API Response Schema
# ---------------------------------------------------------

class AnalyzeResponseData(BaseModel):
    """Comprehensive payload container for the hybrid NLP + LLM analysis."""
    resume_structure: ResumeStructureData
    contact_analysis: ContactAnalysisData
    skill_analysis: SkillAnalysisData
    achievement_analysis: AchievementAnalysisData
    overall_analysis: OverallAnalysis
    role_analysis: Optional[RoleAnalysis] = None
    job_match_analysis: Optional[JobMatchAnalysis] = None


class ApiResponse(BaseModel):
    """Unified API response wrapper adhering to OWASP & system standards."""
    success: bool
    data: Optional[AnalyzeResponseData] = None
    error: Optional[str] = None
    message: Optional[str] = None
    details: Optional[Dict[str, str]] = None
