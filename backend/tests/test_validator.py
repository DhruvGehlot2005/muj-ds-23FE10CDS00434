"""
@file test_validator.py
@description Unit tests for resume content heuristic validation
@module backend.tests.test_validator
"""

import pytest
from backend.app.services.validator import (
    ResumeValidationError,
    validate_resume_content,
)


def test_validate_valid_resume():
    """Verifies that standard resume text passes validation."""
    resume_text = """
    Alex Morgan
    Email: alex.morgan@testdomain.edu | Phone: +1-555-0144
    EDUCATION
    Bachelor of Science in Computer Science, State University, 2024
    SKILLS
    Python, TypeScript, SQL, React, Docker, Git
    EXPERIENCE
    Software Engineering Intern at TechCorp. Built REST APIs using FastAPI and reduced latency by 30%.
    PROJECTS
    NLP Resume Parser with ATS compatibility engine.
    """
    assert validate_resume_content(resume_text) is True


def test_validate_empty_resume():
    """Verifies that empty string raises ResumeValidationError."""
    with pytest.raises(ResumeValidationError) as exc_info:
        validate_resume_content("")
    assert exc_info.value.code == "EMPTY_RESUME"


def test_validate_short_resume():
    """Verifies that short snippet (< 150 chars) raises ResumeValidationError."""
    with pytest.raises(ResumeValidationError) as exc_info:
        validate_resume_content("Alex Morgan. Looking for a software engineering job.")
    assert exc_info.value.code == "RESUME_TOO_SHORT"


def test_validate_non_resume_content():
    """Verifies that non-resume text (e.g., cooking recipe) fails validation."""
    recipe_text = """
    Chocolate Chip Cookies Recipe
    Ingredients: 2 cups all-purpose flour, 1 cup granulated sugar, 1 cup brown sugar,
    2 large eggs, 1 teaspoon baking soda, 1 cup chocolate chips, softened butter.
    Instructions: Preheat oven to 375 degrees Fahrenheit. Mix ingredients in a bowl.
    Bake on baking sheet for 10 to 12 minutes until golden brown. Cool on wire rack.
    """
    with pytest.raises(ResumeValidationError) as exc_info:
        validate_resume_content(recipe_text)
    assert exc_info.value.code == "NOT_A_RESUME"
