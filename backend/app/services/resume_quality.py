"""
@file resume_quality.py
@description Deterministic structural completeness engine evaluating resume section presence
@module backend.app.services.resume_quality
"""

from typing import Dict, List, Set, Any

# Section weighting tailored for student and technical candidates
# Core technical sections receive higher weight; professional certifications/honors are optional.
SECTION_WEIGHTS: Dict[str, int] = {
    "CONTACT": 15,
    "EDUCATION": 20,
    "SKILLS": 25,
    "PROJECTS": 20,
    "EXPERIENCE": 10,
    "SUMMARY": 5,
    "CERTIFICATIONS": 3,
    "ACHIEVEMENTS": 2,
}

CORE_SECTIONS: Set[str] = {"CONTACT", "EDUCATION", "SKILLS", "PROJECTS"}
OPTIONAL_SECTIONS: Set[str] = {"EXPERIENCE", "SUMMARY", "CERTIFICATIONS", "ACHIEVEMENTS"}


def calculate_structural_completeness(detected_sections: List[str]) -> Dict[str, Any]:
    """
    Deterministically computes the Structural Completeness Score based on detected sections.

    @param detected_sections: List of section labels detected by ML classifier or heuristics
    @return Dictionary containing structural completeness score, present, missing, and optional missing sections
    """
    detected_set = {s.upper() for s in detected_sections if s and s.upper() != "OTHER"}

    present_sections = []
    missing_sections = []
    optional_missing_sections = []
    earned_weight = 0
    total_core_and_standard_weight = sum(
        weight for sec, weight in SECTION_WEIGHTS.items() if sec in CORE_SECTIONS or sec in ["EXPERIENCE", "SUMMARY"]
    )

    for section, weight in SECTION_WEIGHTS.items():
        if section in detected_set:
            present_sections.append(section)
            earned_weight += weight
        else:
            if section in CORE_SECTIONS:
                missing_sections.append(section)
            else:
                optional_missing_sections.append(section)

    # Scale score out of 100 based on core & standard expectations
    # If candidate has certifications and achievements, it can boost score up to max 100.
    raw_score = (earned_weight / total_core_and_standard_weight) * 100
    bounded_score = max(0, min(100, round(raw_score)))

    return {
        "completeness_score": bounded_score,
        "metric_name": "STRUCTURAL COMPLETENESS SCORE",
        "present_sections": sorted(present_sections),
        "missing_sections": sorted(missing_sections),
        "optional_missing_sections": sorted(optional_missing_sections),
        "total_detected_count": len(present_sections),
    }
