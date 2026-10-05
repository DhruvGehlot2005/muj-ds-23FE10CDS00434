"""
@file backend/app/services/achievement_detector.py
@description Deterministic detection of quantified achievement language in resume bullet points.
@module backend/app/services
"""

import re
from typing import Any, Dict, List, Set


# Patterns for identifying quantitative achievement statements
PATTERNS = {
    "percentage": re.compile(
        r"(?:(?:improved|reduced|increased|boosted|decreased|cut|by)\s+)?\b\d+(?:\.\d+)?%",
        re.IGNORECASE
    ),
    "monetary": re.compile(
        r"(?:[\$\€\£\₹]|USD|INR|EUR)\s*\d+(?:,\d{3})*(?:\.\d+)?(?:\s*(?:k|m|b|million|billion|lakh|crore))?",
        re.IGNORECASE
    ),
    "ranking": re.compile(
        r"\b(?:ranked|rank|placed)\s*(?:#|\b)?\d+(?:st|nd|rd|th)?\b|\b(?:top\s*\d+%?|1st|2nd|3rd)\s*(?:place|tier|prize|position)?\b",
        re.IGNORECASE
    ),
    "multiplier_speed": re.compile(
        r"\b\d+(?:\.\d+)?x\s*(?:faster|speedup|increase|throughput|reduction|boost)?\b",
        re.IGNORECASE
    ),
    "scale_volume": re.compile(
        r"\b\d+(?:,\d{3})*(?:\+)?\s*(?:users|active\s+users|requests|qps|rps|transactions|downloads|records|queries|data\s+points|customers|clients|subscribers)\b",
        re.IGNORECASE
    ),
    "time_reduction": re.compile(
        r"\b(?:reduced|saved|cut)\s+(?:time\s+by\s+)?\d+\s*(?:hours|hrs|minutes|mins|ms|seconds|days|weeks)\b",
        re.IGNORECASE
    ),
}


class AchievementDetector:
    """
    Deterministic detector for quantitative achievement language in resume texts.
    Detects percentages, metrics, monetary amounts, scale counts, and performance rankings.
    """

    def __init__(self) -> None:
        """Initialize achievement detection patterns."""
        self.patterns = PATTERNS

    def _split_into_statements(self, text: str) -> List[str]:
        """Split text into individual bullet points or sentences."""
        if not text:
            return []

        # Split on line breaks, standard bullet characters, or punctuation followed by space
        raw_lines = re.split(r"[\n\r•\*\-\–]+|(?<=[.!?])\s+", text)
        statements = []
        for line in raw_lines:
            cleaned = line.strip()
            # Must have at least 15 characters to be a meaningful achievement statement
            if len(cleaned) >= 15:
                statements.append(cleaned)
        return statements

    def detect_achievements(self, text: str) -> Dict[str, Any]:
        """
        Detect quantified achievements across resume statements.

        Args:
            text: Text to scan for achievements.

        Returns:
            Dict containing:
                - achievements_count: Total unique quantitative statements found.
                - achievements: List of dicts with sentence, metric_type, matched_text.
                - detected_metric_types: List of distinct metric types found.
                - quantification_score: Calibrated score from 0 to 100 based on quantitative density.
        """
        if not text or not text.strip():
            return {
                "achievements_count": 0,
                "achievements": [],
                "detected_metric_types": [],
                "quantification_score": 0,
            }

        statements = self._split_into_statements(text)
        detected_achievements: List[Dict[str, str]] = []
        seen_sentences: Set[str] = set()
        matched_types: Set[str] = set()

        for stmt in statements:
            if stmt in seen_sentences:
                continue

            for metric_type, pattern in self.patterns.items():
                match = pattern.search(stmt)
                if match:
                    seen_sentences.add(stmt)
                    matched_types.add(metric_type)
                    # Limit statement length for clean display
                    display_stmt = stmt if len(stmt) <= 220 else stmt[:217] + "..."
                    detected_achievements.append({
                        "statement": display_stmt,
                        "metric_type": metric_type,
                        "matched_text": match.group(0).strip(),
                    })
                    break  # One match per statement is enough

        count = len(detected_achievements)

        # Calibrated quantification score (0-100):
        # 0 = 0, 1 = 30, 2 = 55, 3 = 75, 4 = 90, 5+ = 100
        score_map = {0: 0, 1: 30, 2: 55, 3: 75, 4: 90}
        quantification_score = score_map.get(count, 100 if count >= 5 else 0)

        return {
            "achievements_count": count,
            "achievements": detected_achievements,
            "detected_metric_types": sorted(list(matched_types)),
            "quantification_score": quantification_score,
        }
