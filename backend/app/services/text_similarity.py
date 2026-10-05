"""
@file backend/app/services/text_similarity.py
@description Statistical NLP lexical similarity using TF-IDF and Cosine Similarity, plus deterministic JD skill comparison.
@module backend/app/services
"""

import logging
from typing import Any, Dict, List, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend.app.services.skill_extractor import SkillExtractor

logger = logging.getLogger(__name__)


class TextSimilarityEngine:
    """
    Statistical NLP engine for calculating lexical similarity between resume and job description.
    Uses TF-IDF feature extraction with Cosine Similarity, alongside deterministic skill overlap.
    """

    def __init__(self, skill_extractor: Optional[SkillExtractor] = None) -> None:
        """
        Initialize the similarity engine.

        Args:
            skill_extractor: Optional instance of SkillExtractor.
        """
        self.skill_extractor = skill_extractor or SkillExtractor()

    def compute_lexical_similarity(self, resume_text: str, jd_text: str) -> float:
        """
        Calculate TF-IDF Cosine Similarity between resume text and job description.

        Args:
            resume_text: Extracted resume text.
            jd_text: Target job description text.

        Returns:
            Cosine similarity score as float between 0.0 and 1.0.
        """
        if not resume_text.strip() or not jd_text.strip():
            return 0.0

        try:
            vectorizer = TfidfVectorizer(
                stop_words="english",
                ngram_range=(1, 2),
                max_features=5000,
                lowercase=True
            )
            tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
            similarity = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
            return max(0.0, min(1.0, similarity))
        except Exception as e:
            logger.error("Failed to compute TF-IDF similarity: %s", e)
            return 0.0

    def analyze_job_description(
        self,
        resume_text: str,
        jd_text: str,
        resume_skills: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Perform complete deterministic and statistical comparison between resume and job description.

        Args:
            resume_text: Resume text content.
            jd_text: Job description text.
            resume_skills: Optional pre-extracted canonical skills from resume.

        Returns:
            Dict containing:
                - lexical_similarity_score: Percentage score (0 - 100).
                - tfidf_similarity: Raw cosine similarity (0.0 - 1.0).
                - jd_skills: Canonical skills extracted from JD.
                - matching_skills: Skills found in both resume and JD.
                - missing_skills: Skills required in JD but not present in resume.
                - match_ratio: Fraction of JD skills matched (0.0 - 1.0).
        """
        # 1. Statistical TF-IDF cosine similarity
        raw_similarity = self.compute_lexical_similarity(resume_text, jd_text)
        lexical_score = round(raw_similarity * 100, 1)

        # 2. Extract JD skills
        jd_extracted = self.skill_extractor.extract_skills(jd_text)
        jd_skills = jd_extracted.get("explicit_skills", [])

        # 3. Compare with resume skills
        if resume_skills is None:
            resume_extracted = self.skill_extractor.extract_skills(resume_text)
            res_skills_set = set(resume_extracted.get("explicit_skills", []))
        else:
            res_skills_set = set(resume_skills)

        jd_skills_set = set(jd_skills)
        matching = sorted(list(res_skills_set.intersection(jd_skills_set)))
        missing = sorted(list(jd_skills_set.difference(res_skills_set)))

        match_ratio = round(len(matching) / len(jd_skills_set), 2) if jd_skills_set else 1.0

        return {
            "lexical_similarity_score": lexical_score,
            "tfidf_similarity": round(raw_similarity, 4),
            "jd_skills": jd_skills,
            "matching_skills": matching,
            "missing_skills": missing,
            "match_ratio": match_ratio,
        }
