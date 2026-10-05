"""
@file backend/tests/test_achievement_detector.py
@description Unit tests for deterministic quantified achievement language detection.
@module backend.tests
"""

from backend.app.services.achievement_detector import AchievementDetector


def test_detect_percentage_and_time_improvements():
    """Test detecting latency reduction and speedup metrics."""
    text = (
        "• Reduced API latency by 35% by implementing Redis caching.\n"
        "• Saved 15 hours per week by automating manual regression suites."
    )
    detector = AchievementDetector()
    result = detector.detect_achievements(text)

    assert result["achievements_count"] >= 2
    types = result["detected_metric_types"]
    assert "percentage" in types or "time_reduction" in types


def test_detect_scale_volume_and_monetary():
    """Test detecting scale volume and monetary figures."""
    text = (
        "Scaled architecture to handle 50,000 active users concurrently.\n"
        "Managed cloud infrastructure budget of $25,000 annually."
    )
    detector = AchievementDetector()
    result = detector.detect_achievements(text)

    assert result["achievements_count"] >= 2
    types = result["detected_metric_types"]
    assert "scale_volume" in types
    assert "monetary" in types


def test_detect_ranking():
    """Test detecting competition and hackathon rankings."""
    text = "Ranked 2nd in National Collegiate Hackathon among 120 teams."
    detector = AchievementDetector()
    result = detector.detect_achievements(text)

    assert result["achievements_count"] == 1
    assert "ranking" in result["detected_metric_types"]


def test_no_metrics_detected():
    """Test text lacking quantitative phrasing returns 0 achievements."""
    text = "Responsible for writing code and attending daily standups."
    detector = AchievementDetector()
    result = detector.detect_achievements(text)

    assert result["achievements_count"] == 0
    assert result["quantification_score"] == 0
