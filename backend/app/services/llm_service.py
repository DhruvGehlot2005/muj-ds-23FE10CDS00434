"""
@file llm_service.py
@description LLM orchestration service utilizing prompt templates and structured NLP evidence validation.
@module backend.app.services.llm_service
"""

import json
import logging
import os
import re
import time
from typing import Any, Dict, List, Optional, Union
from google import genai
from google.genai import types
from pydantic import ValidationError

from backend.app.config import settings
from backend.app.models.schemas import (
    JobMatchAnalysis,
    OverallAnalysis,
    RoleAnalysis,
)

logger = logging.getLogger(__name__)

PROMPTS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "prompts")
)


class LLMServiceError(Exception):
    """Custom exception for LLM API invocation or validation failures."""

    def __init__(self, message: str, code: str = "LLM_SERVICE_ERROR", details: Optional[Dict[str, str]] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class LLMService:
    """
    Manages structured evidence prompt construction, API communication with Google Gemini,
    and Pydantic response validation.
    """

    def __init__(self, prompts_dir: Optional[str] = None) -> None:
        """
        Initializes the LLM service and loads external prompt templates.

        Args:
            prompts_dir: Optional custom directory containing prompt text files.
        """
        self.prompts_dir = prompts_dir or PROMPTS_DIR
        self.prompts: Dict[str, str] = {}
        self._load_prompts()
        self._init_client()

    def _load_prompts(self) -> None:
        """
        Reads prompt templates from YAML files (with fallback to .txt)
        and populates the prompt lookup table.
        """
        # 1. First attempt to load from unified YAML prompt definitions
        try:
            import yaml
            unified_yaml_candidates = [
                os.path.join(self.prompts_dir, "prompts.yaml"),
                os.path.join(self.prompts_dir, "prompts.yml"),
                os.path.join(os.path.dirname(self.prompts_dir), "prompts", "prompts.yaml"),
            ]
            for yaml_path in unified_yaml_candidates:
                if os.path.exists(yaml_path):
                    with open(yaml_path, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                    if isinstance(data, dict):
                        prompts_dict = data.get("prompts", data)
                        if isinstance(prompts_dict, dict):
                            key_mappings = {
                                "system": ["system_instructions", "system"],
                                "overall": ["overall_resume_analysis", "overall"],
                                "role": ["target_role_analysis", "role"],
                                "jd": ["job_description_analysis", "resume_jd_matching", "jd"],
                            }
                            for target_key, candidate_keys in key_mappings.items():
                                for cand in candidate_keys:
                                    if cand in prompts_dict:
                                        val = prompts_dict[cand]
                                        if isinstance(val, dict) and "template" in val:
                                            self.prompts[target_key] = val["template"].strip()
                                        elif isinstance(val, str):
                                            self.prompts[target_key] = val.strip()
                                        break
                            logger.info("Loaded prompt templates from unified YAML: %s", yaml_path)
                            break
        except Exception as e:
            logger.warning("Error reading unified prompts.yaml: %s. Falling back to individual files.", e)

        # 2. Check for individual YAML or TXT files for any missing keys
        prompt_file_pairs = {
            "system": ["system_instructions.yaml", "system_instructions.yml", "system_instructions.txt"],
            "overall": ["overall_resume_analysis.yaml", "overall_resume_analysis.yml", "overall_resume_analysis.txt"],
            "role": ["target_role_analysis.yaml", "target_role_analysis.yml", "target_role_analysis.txt"],
            "jd": ["job_description_analysis.yaml", "job_description_analysis.yml", "job_description_analysis.txt"],
        }

        for key, filenames in prompt_file_pairs.items():
            if key in self.prompts and self.prompts[key]:
                continue
            for filename in filenames:
                path = os.path.join(self.prompts_dir, filename)
                if os.path.exists(path):
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            content = f.read().strip()
                        if filename.endswith((".yaml", ".yml")):
                            try:
                                import yaml
                                parsed = yaml.safe_load(content)
                                if isinstance(parsed, dict) and "template" in parsed:
                                    self.prompts[key] = parsed["template"].strip()
                                elif isinstance(parsed, str):
                                    self.prompts[key] = parsed.strip()
                                else:
                                    self.prompts[key] = content
                            except Exception:
                                self.prompts[key] = content
                        else:
                            self.prompts[key] = content
                        break
                    except Exception as e:
                        logger.warning("Error reading %s: %s", path, e)
            if key not in self.prompts:
                self.prompts[key] = ""

        # Aliases for compatibility
        self.prompts["OVERALL_RESUME_ANALYSIS"] = self.prompts.get("overall", "")
        self.prompts["TARGET_ROLE_ANALYSIS"] = self.prompts.get("role", "")
        self.prompts["JOB_DESCRIPTION_ANALYSIS"] = self.prompts.get("jd", "")
        self.prompts["RESUME_JD_MATCHING"] = self.prompts.get("jd", "")

    def _init_client(self) -> None:
        """Initializes the Gemini API client if an API key is configured."""
        self.api_key = settings.llm_api_key
        self.model_name = settings.llm_model
        self.is_mock = (
            not self.api_key
            or self.api_key == "your_gemini_api_key_here"
            or self.api_key == "mock-key-for-local-testing"
        )
        if self.is_mock:
            logger.warning("LLM API key not configured or set to mock. Service running in mock demonstration mode.")
            self.client = None
        else:
            self.client = genai.Client(api_key=self.api_key)

    def _extract_json_substring(self, text: str) -> str:
        """
        Extracts raw JSON content even if wrapped in markdown code fences or narrative text.

        Args:
            text: Raw LLM output string.

        Returns:
            Trimmed JSON substring.
        """
        clean = text.strip()
        clean = re.sub(r"^```(?:json)?\s*", "", clean, flags=re.MULTILINE)
        clean = re.sub(r"```\s*$", "", clean, flags=re.MULTILINE)
        clean = clean.strip()

        start = clean.find("{")
        end = clean.rfind("}")
        if start != -1 and end != -1 and end > start:
            return clean[start : end + 1]
        return clean

    def _call_gemini_api(self, prompt: str) -> str:
        """
        Dispatches prompt to Gemini LLM with system instructions, JSON mode,
        model cascade, and retry logic.

        Args:
            prompt: Formatted user prompt.

        Returns:
            Raw JSON string from Gemini.
        """
        if not self.client:
            raise LLMServiceError("LLM client is uninitialized.", code="CLIENT_UNINITIALIZED")

        candidate_models = [self.model_name]
        for fallback in ["gemini-3.5-flash-lite", "gemini-flash-latest", "gemini-3.8-flash"]:
            if fallback not in candidate_models:
                candidate_models.append(fallback)

        last_err = None
        system_instruction = self.prompts.get("system", "")

        for current_model in candidate_models:
            for attempt in range(2):
                try:
                    config = types.GenerateContentConfig(
                        system_instruction=system_instruction if system_instruction else None,
                        response_mime_type="application/json",
                        temperature=0.2,
                    )
                    response = self.client.models.generate_content(
                        model=current_model,
                        contents=prompt,
                        config=config,
                    )
                    if response.text:
                        return response.text
                except Exception as exc:
                    last_err = exc
                    err_str = str(exc)
                    is_transient = any(
                        code in err_str
                        for code in ["503", "429", "UNAVAILABLE", "ResourceExhausted", "high demand", "404", "NOT_FOUND"]
                    )
                    if is_transient and attempt == 0:
                        time.sleep(1)
                        continue
                    logger.warning("Model %s unavailable (%s), trying next candidate...", current_model, err_str[:80])
                    break

        raise LLMServiceError(
            f"All Gemini models were unavailable or returned errors: {str(last_err)}",
            code="API_REQUEST_FAILED",
        )

    def analyze_overall(
        self,
        evidence_or_text: Optional[Union[Dict[str, Any], str]] = None,
        structured_evidence: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> OverallAnalysis:
        """
        Analyzes overall resume quality using structured NLP evidence or fallback text.

        Args:
            evidence_or_text: Dict of custom NLP features or raw resume text.
            structured_evidence: Keyword alias for structured NLP features.

        Returns:
            Validated OverallAnalysis Pydantic model.
        """
        payload = structured_evidence if structured_evidence is not None else evidence_or_text
        if payload is None:
            payload = {}

        if self.is_mock:
            return OverallAnalysis(
                overall_quality_score=84,
                overall_score=84,
                completeness_score=88,
                clarity_score=86,
                professionalism_score=88,
                ats_compatibility_score=85,
                ats_score=85,
                section_evaluations={
                    "contact_info": "PRESENT",
                    "education": "PRESENT",
                    "skills": "PRESENT",
                    "projects": "PRESENT",
                },
                strengths=[
                    "Clearly identified core technical skills aligned with modern software stacks.",
                    "Structured presentation with verified contact information and project sections.",
                    "Demonstrates foundational problem-solving through academic and practical projects.",
                ],
                weaknesses=[
                    "Project bullet points could feature more direct quantitative impact metrics.",
                    "Summary section could articulate target career trajectory more clearly.",
                ],
                missing_sections=[],
                recommendations=[
                    "Quantify project outcomes with specific metrics (e.g. latency, throughput, user base).",
                    "Add explicit testing frameworks and CI/CD tools to project descriptions.",
                ],
            )

        template = self.prompts.get("overall", "")
        if not template:
            raise LLMServiceError("Prompt overall_resume_analysis.txt is missing or empty.", code="MISSING_PROMPT")

        if isinstance(payload, str):
            evidence_json = json.dumps({"resume_text": payload}, indent=2)
            raw_text = payload
        else:
            evidence_json = json.dumps(payload, indent=2)
            raw_text = payload.get("resume_text", "")
            if not raw_text and "resume_sections" in payload:
                raw_text = "\n\n".join(
                    f"### {sec}\n" + "\n".join(blocks)
                    for sec, blocks in payload["resume_sections"].items()
                )

        prompt = (
            template.replace("{evidence_json}", evidence_json)
            .replace("{resume_text}", raw_text or evidence_json)
        )

        raw_output = self._call_gemini_api(prompt)
        res = self._parse_json_model(raw_output, OverallAnalysis)
        return res

    def analyze_target_role(
        self,
        evidence_or_text: Optional[Union[Dict[str, Any], str]] = None,
        target_role: str = "",
        structured_evidence: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> RoleAnalysis:
        """
        Evaluates resume alignment with target role expectations using structured NLP evidence.

        Args:
            evidence_or_text: Dict of custom NLP features or raw resume text.
            target_role: Target job title.
            structured_evidence: Keyword alias for structured NLP features.

        Returns:
            Validated RoleAnalysis Pydantic model.
        """
        payload = structured_evidence if structured_evidence is not None else evidence_or_text
        if payload is None:
            payload = {}

        if self.is_mock:
            return RoleAnalysis(
                target_role=target_role,
                role_compatibility_score=82,
                role_match_score=82,
                strengths=[
                    f"Core programming competencies and tools directly relevant to {target_role}.",
                    "Practical projects demonstrating end-to-end implementation capability.",
                ],
                matching_areas=[
                    f"Core programming competencies and tools directly relevant to {target_role}.",
                    "Practical projects demonstrating end-to-end implementation capability.",
                ],
                weaknesses=[
                    f"Limited explicit mention of production deployment and monitoring for {target_role}.",
                ],
                weak_areas=[
                    f"Limited explicit mention of production deployment and monitoring for {target_role}.",
                ],
                gaps=[
                    f"Advanced cloud infrastructure tools commonly expected for {target_role} roles.",
                ],
                missing_areas=[
                    f"Advanced cloud infrastructure tools commonly expected for {target_role} roles.",
                ],
                recommendations=[
                    f"Highlight end-to-end engineering practices relevant to {target_role}.",
                    "Include unit test coverage and automated deployment workflows in project descriptions.",
                ],
            )

        template = self.prompts.get("role", "")
        if not template:
            raise LLMServiceError("Prompt target_role_analysis.txt is missing or empty.", code="MISSING_PROMPT")

        if isinstance(payload, str):
            evidence_json = json.dumps({"resume_text": payload}, indent=2)
            raw_text = payload
        else:
            evidence_json = json.dumps(payload, indent=2)
            raw_text = payload.get("resume_text", "")
            if not raw_text and "resume_sections" in payload:
                raw_text = "\n\n".join(
                    f"### {sec}\n" + "\n".join(blocks)
                    for sec, blocks in payload["resume_sections"].items()
                )

        prompt = (
            template.replace("{target_role}", target_role)
            .replace("{evidence_json}", evidence_json)
            .replace("{resume_text}", raw_text or evidence_json)
        )

        raw_output = self._call_gemini_api(prompt)
        res = self._parse_json_model(raw_output, RoleAnalysis)
        return res

    def analyze_job_match(
        self,
        evidence_or_text: Optional[Union[Dict[str, Any], str]] = None,
        jd_text: str = "",
        lexical_similarity_score: float = 70.0,
        matching_skills: Optional[List[str]] = None,
        missing_skills: Optional[List[str]] = None,
        structured_evidence: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> JobMatchAnalysis:
        """
        Performs semantic resume-to-JD qualification matching using structured evidence.

        Args:
            evidence_or_text: Dict of custom NLP features or raw resume text.
            jd_text: Job description text.
            lexical_similarity_score: TF-IDF Cosine Similarity percentage.
            matching_skills: Optional verified matching skills.
            missing_skills: Optional verified missing skills.
            structured_evidence: Keyword alias for structured NLP features.

        Returns:
            Validated JobMatchAnalysis Pydantic model.
        """
        payload = structured_evidence if structured_evidence is not None else evidence_or_text
        if payload is None:
            payload = {}
        match_skills = matching_skills or ["Python", "Git", "REST APIs"]
        miss_skills = missing_skills or ["Kubernetes"]
        raw_tfidf = round(lexical_similarity_score / 100.0, 4)

        if self.is_mock:
            return JobMatchAnalysis(
                lexical_similarity_score=lexical_similarity_score,
                tfidf_similarity=raw_tfidf,
                semantic_match_score=80,
                match_score=80,
                matching_skills=match_skills,
                missing_skills=miss_skills,
                explicit_matches=[
                    {"requirement": "REST API Development", "evidence": "Built RESTful services with FastAPI"},
                    {"requirement": "Database Design", "evidence": "Relational data modeling with PostgreSQL"},
                ],
                partial_matches=[
                    {
                        "requirement": "Cloud Deployment",
                        "evidence": "Coursework exposure to AWS",
                        "gap": "Lacks production CI/CD container orchestration",
                    }
                ],
                missing_requirements=[
                    {"requirement": "Kubernetes Orchestration", "importance": "PREFERRED"},
                    {"requirement": "Event Streaming (Kafka)", "importance": "PREFERRED"},
                ],
                recommendations=[
                    "Add explicit mentions of containerization and orchestration tooling.",
                    "Align project descriptions with the core responsibilities emphasized in the JD.",
                ],
            )

        template = self.prompts.get("jd", "")
        if not template:
            raise LLMServiceError("Prompt job_description_analysis.txt is missing or empty.", code="MISSING_PROMPT")

        if isinstance(payload, str):
            evidence_json = json.dumps({"resume_text": payload}, indent=2)
            raw_text = payload
        else:
            evidence_json = json.dumps(payload, indent=2)
            raw_text = payload.get("resume_text", "")
            if not raw_text and "resume_sections" in payload:
                raw_text = "\n\n".join(
                    f"### {sec}\n" + "\n".join(blocks)
                    for sec, blocks in payload["resume_sections"].items()
                )

        prompt = (
            template.replace("{evidence_json}", evidence_json)
            .replace("{resume_text}", raw_text or evidence_json)
            .replace("{job_description}", jd_text)
            .replace("{jd_text}", jd_text)
            .replace("{lexical_similarity_score}", str(lexical_similarity_score))
            .replace("{matching_skills}", ", ".join(match_skills) if match_skills else "None")
            .replace("{missing_skills}", ", ".join(miss_skills) if miss_skills else "None")
        )

        raw_output = self._call_gemini_api(prompt)
        res_dict = json.loads(self._extract_json_substring(raw_output))

        semantic_score = int(res_dict.get("semantic_match_score", 75))
        explicit_matches = res_dict.get("explicit_matches", [])
        partial_matches = res_dict.get("partial_matches", [])
        missing_requirements = res_dict.get("missing_requirements", [])
        recommendations = res_dict.get("recommendations", [])

        return JobMatchAnalysis(
            lexical_similarity_score=lexical_similarity_score,
            tfidf_similarity=raw_tfidf,
            semantic_match_score=semantic_score,
            match_score=semantic_score,
            matching_skills=match_skills,
            missing_skills=miss_skills,
            explicit_matches=explicit_matches,
            partial_matches=partial_matches,
            missing_requirements=missing_requirements,
            recommendations=recommendations,
        )

    def _parse_json_model(self, raw_text: str, model_cls: Any) -> Any:
        """
        Parses and validates JSON text against a Pydantic model.

        Args:
            raw_text: Raw LLM output.
            model_cls: Target Pydantic model class.

        Returns:
            Instance of model_cls.

        Raises:
            LLMServiceError: If JSON is malformed or validation fails.
        """
        cleaned_json = self._extract_json_substring(raw_text)
        try:
            parsed_dict = json.loads(cleaned_json)
        except json.JSONDecodeError as exc:
            logger.error("Malformed JSON from LLM: %s", raw_text[:200])
            raise LLMServiceError(
                "LLM returned an invalid JSON response structure.",
                code="MALFORMED_JSON",
                details={"raw_excerpt": raw_text[:300]},
            ) from exc

        try:
            return model_cls.model_validate(parsed_dict)
        except ValidationError as val_err:
            logger.error("Pydantic validation error: %s", val_err.errors())
            raise LLMServiceError(
                "LLM response failed data contract validation.",
                code="SCHEMA_VALIDATION_ERROR",
                details={"errors": str(val_err.errors())},
            ) from val_err
