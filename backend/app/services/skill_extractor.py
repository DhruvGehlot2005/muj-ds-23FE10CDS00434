"""
@file backend/app/services/skill_extractor.py
@description Deterministic skill extraction and alias normalization using a curated vocabulary.
@module backend/app/services
"""

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)

DEFAULT_SKILLS_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "skills.json")
)


class SkillExtractor:
    """
    Deterministic skill extraction engine with alias normalization and category mapping.
    Matches explicitly evidenced skills against the vocabulary in data/skills.json.
    """

    def __init__(self, skills_vocab_path: Optional[str] = None) -> None:
        """
        Initialize the skill extractor with vocabulary from data/skills.json.

        Args:
            skills_vocab_path: Optional custom path to skills.json.
        """
        self.skills_path = skills_vocab_path or DEFAULT_SKILLS_PATH
        self.categories: Dict[str, List[str]] = {}
        self.aliases: Dict[str, str] = {}
        self.canonical_to_category: Dict[str, str] = {}
        self._compiled_patterns: List[Tuple[re.Pattern, str]] = []
        self._load_vocabulary()

    def _load_vocabulary(self) -> None:
        """Load vocabulary, establish canonical maps, and precompile regex patterns."""
        if not os.path.exists(self.skills_path):
            logger.warning("Skills vocabulary file not found at %s. Initializing empty vocabulary.", self.skills_path)
            return

        try:
            with open(self.skills_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.categories = data.get("categories", {})
            self.aliases = data.get("aliases", {})

            # Map canonical name to category
            for category, skills in self.categories.items():
                for skill in skills:
                    self.canonical_to_category[skill] = category

            # Build patterns list: (token, canonical, case_sensitive)
            # We sort candidates by length descending to match multi-word terms first
            pattern_candidates: List[Tuple[str, str, bool]] = []

            # Add canonical skills
            for category, skills in self.categories.items():
                for skill in skills:
                    is_case_sensitive = skill in {"C", "R", "Go", "AI"}
                    pattern_candidates.append((skill, skill, is_case_sensitive))

            # Add aliases
            for alias, canonical in self.aliases.items():
                is_case_sensitive = alias in {"C", "R", "Go", "AI"}
                pattern_candidates.append((alias, canonical, is_case_sensitive))

            # Sort by candidate length descending to prioritize longer phrases
            pattern_candidates.sort(key=lambda x: len(x[0]), reverse=True)

            compiled: List[Tuple[re.Pattern, str]] = []
            seen_tokens: Set[str] = set()

            for token, canonical, case_sens in pattern_candidates:
                token_clean = token.strip()
                token_key = token_clean if case_sens else token_clean.lower()
                if not token_clean or token_key in seen_tokens:
                    continue
                seen_tokens.add(token_key)

                escaped = re.escape(token_clean)

                if token_clean.endswith("+") or token_clean.endswith("#"):
                    pattern_str = r"(?<!\w)" + escaped + r"(?!\w)"
                elif token_clean.startswith("."):
                    pattern_str = r"(?<!\w)" + escaped + r"\b"
                else:
                    pattern_str = r"\b" + escaped + r"\b"

                flags = 0 if case_sens else re.IGNORECASE
                pattern = re.compile(pattern_str, flags)
                compiled.append((pattern, canonical))

            self._compiled_patterns = compiled

        except Exception as e:
            logger.error("Failed to load skills vocabulary from %s: %s", self.skills_path, e)

    def extract_skills(self, text: str) -> Dict[str, Any]:
        """
        Extract explicitly evidenced skills from text with alias normalization.

        Args:
            text: Text to extract skills from (resume or job description).

        Returns:
            Dict containing:
                - explicit_skills: Sorted list of canonical skill names found.
                - categorized_skills: Dict mapping category to list of canonical skills.
                - total_skills_count: Total unique canonical skills detected.
        """
        if not text or not text.strip():
            return {
                "explicit_skills": [],
                "categorized_skills": {},
                "total_skills_count": 0,
            }

        detected_canonical: Set[str] = set()

        for pattern, canonical in self._compiled_patterns:
            if pattern.search(text):
                detected_canonical.add(canonical)

        # Categorize detected skills
        categorized: Dict[str, List[str]] = {}
        for skill in detected_canonical:
            cat = self.canonical_to_category.get(skill, "Other")
            if cat not in categorized:
                categorized[cat] = []
            categorized[cat].append(skill)

        # Sort skills within each category
        for cat in categorized:
            categorized[cat].sort()

        sorted_skills = sorted(list(detected_canonical))

        return {
            "explicit_skills": sorted_skills,
            "categorized_skills": categorized,
            "total_skills_count": len(sorted_skills),
        }
