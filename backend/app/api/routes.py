"""
@file routes.py
@description FastAPI API routes for hybrid NLP resume analysis and system health checks.
@module backend.app.api.routes
"""

from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.app.config import settings
from backend.app.models.schemas import (
    AchievementAnalysisData,
    AnalyzeResponseData,
    ApiResponse,
    ClassifiedBlock,
    ContactAnalysisData,
    ResumeStructureData,
    SkillAnalysisData,
)
from backend.app.services.achievement_detector import AchievementDetector
from backend.app.services.contact_extractor import ContactExtractor
from backend.app.services.extractor import (
    ExtractionError,
    extract_document_text,
    sanitize_text,
)
from backend.app.services.llm_service import LLMService, LLMServiceError
from backend.app.services.resume_quality import calculate_structural_completeness
from backend.app.services.section_classifier import SectionClassifierService
from backend.app.services.skill_extractor import SkillExtractor
from backend.app.services.text_similarity import TextSimilarityEngine
from backend.app.services.validator import ResumeValidationError, validate_resume_content
from backend.app.utils.logger import logger

router = APIRouter(prefix="/api")
limiter = Limiter(key_func=get_remote_address)

# Initialize NLP & ML Services
try:
    section_classifier = SectionClassifierService()
except Exception as e:
    logger.error("Could not load section classifier: %s", e)
    section_classifier = None

contact_extractor = ContactExtractor()
skill_extractor = SkillExtractor()
achievement_detector = AchievementDetector()
text_similarity_engine = TextSimilarityEngine(skill_extractor=skill_extractor)
llm_service = LLMService()


@router.get("/health", response_model=dict, tags=["Health"])
async def health_check():
    """Returns application health status, ML model status, and configuration info."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "architecture": "HYBRID NLP + LLM",
        "section_classifier_loaded": section_classifier is not None,
        "llm_mock_mode": llm_service.is_mock,
        "llm_model": settings.llm_model,
    }


@router.post("/analyze", response_model=ApiResponse, tags=["Analysis"])
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def analyze_resume(
    request: Request,
    resume: UploadFile = File(..., description="Resume document (PDF or DOCX)"),
    target_role: Optional[str] = Form(None, description="Optional target role"),
    jd_file: Optional[UploadFile] = File(None, description="Optional Job Description file"),
    jd_text: Optional[str] = Form(None, description="Optional Job Description text"),
):
    """
    Executes the Hybrid NLP + LLM pipeline:
    1. Custom Document Extraction & Sanitization (PyMuPDF / python-docx)
    2. Supervised Section Classification (TF-IDF + Logistic Regression)
    3. Deterministic Structural Completeness Scoring
    4. Deterministic Contact Extraction (Email, Phone, LinkedIn, GitHub)
    5. Deterministic Skill Extraction & Normalization (Curated Vocabulary)
    6. Quantified Achievement Detection (Metrics, Rankings, Percentages)
    7. Statistical Lexical Similarity (TF-IDF Cosine Similarity) when JD is supplied
    8. LLM Semantic Reasoning using Structured Evidence
    """
    logger.info("Incoming analysis request for: %s", resume.filename)

    # 1. Read and validate resume file
    try:
        resume_bytes = await resume.read()
        if not resume.filename:
            raise ExtractionError("Resume filename cannot be empty.", code="INVALID_FILENAME")

        resume_text = extract_document_text(resume.filename, resume_bytes)
        validate_resume_content(resume_text)
    except ExtractionError as ext_err:
        logger.warning("Resume extraction error: %s", ext_err.message)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": ext_err.code, "message": ext_err.message, "details": {}},
        )
    except ResumeValidationError as val_err:
        logger.warning("Resume validation failed: %s", val_err.message)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": val_err.code, "message": val_err.message, "details": {}},
        )

    # 2. Extract Job Description if provided
    extracted_jd_text = ""
    if jd_file and jd_file.filename:
        try:
            jd_bytes = await jd_file.read()
            if len(jd_bytes) > 0:
                extracted_jd_text = extract_document_text(jd_file.filename, jd_bytes)
        except ExtractionError as ext_err:
            logger.warning("JD file extraction error: %s", ext_err.message)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": ext_err.code, "message": f"Job Description file error: {ext_err.message}", "details": {}},
            )

    if not extracted_jd_text and jd_text and jd_text.strip():
        extracted_jd_text = sanitize_text(jd_text.strip())

    # 3. Clean optional target role
    cleaned_target_role = sanitize_text(target_role.strip()) if target_role and target_role.strip() else None

    # 4. CUSTOM NLP / ML PIPELINE
    # 4a. Supervised Section Classification
    if section_classifier is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "MODEL_UNAVAILABLE",
                "message": "Section classifier model is not loaded. Run train_section_classifier.py first.",
                "details": {},
            },
        )

    classification_result = section_classifier.classify_resume(resume_text)
    detected_sections = classification_result.get("detected_classes", [])
    classified_blocks = [
        ClassifiedBlock(
            text=block["text"],
            label=block["label"],
            confidence=block["confidence"],
        )
        for block in classification_result.get("sections", [])
    ]

    # 4b. Deterministic Contact Extraction
    contact_dict = contact_extractor.extract_contacts(resume_text)
    contact_analysis = ContactAnalysisData(**contact_dict)

    # Guarantee CONTACT is marked present if email, phone, github, or linkedin are extracted
    if any(contact_dict.values()) and "CONTACT" not in detected_sections:
        detected_sections.append("CONTACT")

    # 4c. Deterministic Structural Completeness
    completeness_dict = calculate_structural_completeness(detected_sections)
    resume_structure = ResumeStructureData(
        completeness_score=completeness_dict["completeness_score"],
        present_sections=completeness_dict["present_sections"],
        missing_sections=completeness_dict["missing_sections"],
        optional_missing_sections=completeness_dict["optional_missing_sections"],
        classified_blocks=classified_blocks,
    )

    # 4d. Deterministic Skill Extraction
    skill_dict = skill_extractor.extract_skills(resume_text)
    skill_analysis = SkillAnalysisData(
        explicit_skills=skill_dict["explicit_skills"],
        categorized_skills=skill_dict["categorized_skills"],
        total_skills_count=skill_dict["total_skills_count"],
    )

    # 4e. Quantified Achievement Detection
    achievement_dict = achievement_detector.detect_achievements(resume_text)
    achievement_analysis = AchievementAnalysisData(
        achievements_count=achievement_dict["achievements_count"],
        achievements=achievement_dict["achievements"],
        detected_metric_types=achievement_dict["detected_metric_types"],
        quantification_score=achievement_dict["quantification_score"],
    )

    # 4f. Lexical Similarity & Deterministic JD Overlap (if JD supplied)
    jd_sim_result = None
    if extracted_jd_text:
        jd_sim_result = text_similarity_engine.analyze_job_description(
            resume_text=resume_text,
            jd_text=extracted_jd_text,
            resume_skills=skill_analysis.explicit_skills,
        )

    # 5. ASSEMBLE STRUCTURED EVIDENCE FOR LLM
    structured_evidence = {
        "resume_text": resume_text,
        "resume_sections": classification_result.get("grouped_sections", {}),
        "explicit_skills": skill_analysis.explicit_skills,
        "categorized_skills": skill_analysis.categorized_skills,
        "structural_completeness": {
            "score": resume_structure.completeness_score,
            "present_sections": resume_structure.present_sections,
            "missing_sections": resume_structure.missing_sections,
        },
        "contact_analysis": {k: bool(v) for k, v in contact_dict.items()},
        "quantified_achievements": [a["statement"] for a in achievement_dict["achievements"]],
        "quantification_density_score": achievement_dict["quantification_score"],
    }

    if cleaned_target_role:
        structured_evidence["target_role"] = cleaned_target_role

    if extracted_jd_text and jd_sim_result:
        structured_evidence["job_description_summary"] = {
            "lexical_similarity_score": jd_sim_result["lexical_similarity_score"],
            "matching_skills": jd_sim_result["matching_skills"],
            "missing_skills": jd_sim_result["missing_skills"],
        }

    # 6. LLM SEMANTIC REASONING
    try:
        # 6a. Overall Resume Qualitative Analysis
        overall_result = llm_service.analyze_overall(structured_evidence)

        # 6b. Target Role Analysis (if requested)
        role_result = None
        if cleaned_target_role:
            role_result = llm_service.analyze_target_role(structured_evidence, cleaned_target_role)

        # 6c. Semantic Job Match Analysis (if JD provided)
        job_match_result = None
        if extracted_jd_text and jd_sim_result:
            job_match_result = llm_service.analyze_job_match(
                structured_evidence=structured_evidence,
                jd_text=extracted_jd_text,
                lexical_similarity_score=jd_sim_result["lexical_similarity_score"],
                matching_skills=jd_sim_result["matching_skills"],
                missing_skills=jd_sim_result["missing_skills"],
            )

        response_data = AnalyzeResponseData(
            resume_structure=resume_structure,
            contact_analysis=contact_analysis,
            skill_analysis=skill_analysis,
            achievement_analysis=achievement_analysis,
            overall_analysis=overall_result,
            role_analysis=role_result,
            job_match_analysis=job_match_result,
        )

        return ApiResponse(success=True, data=response_data)

    except LLMServiceError as llm_err:
        logger.error("LLM analysis failed: %s", llm_err.message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": llm_err.code, "message": llm_err.message, "details": llm_err.details},
        )
    except Exception as exc:
        logger.error("Unexpected error during analysis: %s: %s", type(exc).__name__, str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "SERVER_ERROR", "message": "An unexpected server error occurred during processing.", "details": {}},
        )
