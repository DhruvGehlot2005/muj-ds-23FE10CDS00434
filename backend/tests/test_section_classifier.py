"""
@file backend/tests/test_section_classifier.py
@description Unit tests for supervised section classification and text segmentation.
@module backend.tests
"""

import pytest
from backend.app.services.section_classifier import SectionClassifierService


@pytest.fixture
def classifier_service():
    """Returns an initialized SectionClassifierService instance."""
    return SectionClassifierService()


def test_classifier_service_initialization(classifier_service):
    """Test that classifier service loads trained pipeline and classes."""
    assert classifier_service is not None
    assert classifier_service.pipeline is not None
    assert len(classifier_service.classes) == 9
    assert "SKILLS" in classifier_service.classes
    assert "EDUCATION" in classifier_service.classes
    assert "EXPERIENCE" in classifier_service.classes


def test_segment_text(classifier_service):
    """Test text block segmentation on paragraph breaks."""
    text = (
        "B.Tech in Computer Science\nUniversity Institute of Technology\n\n"
        "Python, React, TypeScript, SQL\nDocker, Git, FastApi\n\n"
        "Software Engineer Intern\nDeveloped REST APIs"
    )
    blocks = classifier_service.segment_text(text)
    assert len(blocks) == 3
    assert "B.Tech in Computer Science" in blocks[0]
    assert "Python, React" in blocks[1]


def test_predict_known_sections(classifier_service):
    """Test predicting obvious known section blocks."""
    skill_block = "Programming Languages: Python, Java, C++, TypeScript, SQL, React, Docker, Kubernetes"
    pred = classifier_service.predict_block(skill_block)
    assert pred["label"] == "SKILLS"
    assert pred["confidence"] > 0.60

    edu_block = "Bachelor of Science in Computer Science and Engineering, CGPA 8.9"
    pred_edu = classifier_service.predict_block(edu_block)
    assert pred_edu["label"] == "EDUCATION"
    assert pred_edu["confidence"] > 0.60


def test_low_confidence_fallback_to_other(classifier_service):
    """Test that ambiguous text below confidence threshold falls back to OTHER."""
    ambiguous_block = "xyz lorem ipsum foo bar 123456"
    pred = classifier_service.predict_block(ambiguous_block)
    if pred["confidence"] < classifier_service.confidence_threshold:
        assert pred["label"] == "OTHER"
        assert pred["threshold_applied"] is True


def test_classify_resume(classifier_service):
    """Test end-to-end resume text block classification and grouping."""
    resume_text = (
        "john.doe@example.com | +1-555-0199 | github.com/johndoe\n\n"
        "Seeking software engineering opportunities in backend systems.\n\n"
        "Bachelor of Technology in Computer Science\n\n"
        "Proficient in Python, SQL, FastAPI, Docker, and PostgreSQL.\n\n"
        "Software Developer Intern at Acme Corp. Built API endpoints."
    )
    result = classifier_service.classify_resume(resume_text)
    assert "sections" in result
    assert "grouped_sections" in result
    assert "detected_classes" in result
    assert len(result["sections"]) >= 3
    assert len(result["detected_classes"]) > 0


def test_detect_header_variations(classifier_service):
    """Test deterministic header detection on diverse formatting styles."""
    # PROJECTS variations
    assert classifier_service.detect_header("PROJECTS") == "PROJECTS"
    assert classifier_service.detect_header("Projects") == "PROJECTS"
    assert classifier_service.detect_header("KEY PROJECTS") == "PROJECTS"
    assert classifier_service.detect_header("ACADEMIC PROJECTS") == "PROJECTS"
    assert classifier_service.detect_header("PERSONAL PROJECTS") == "PROJECTS"
    assert classifier_service.detect_header("PROJECTS & EXPERIENCE") == "PROJECTS"
    assert classifier_service.detect_header("## PROJECTS") == "PROJECTS"
    assert classifier_service.detect_header("PROJECTS:") == "PROJECTS"
    assert classifier_service.detect_header("PROJECTS (Selected)") == "PROJECTS"
    assert classifier_service.detect_header("P R O J E C T S") == "PROJECTS"
    assert classifier_service.detect_header("3. PROJECTS") == "PROJECTS"

    # Other canonical section headers
    assert classifier_service.detect_header("TECHNICAL SKILLS") == "SKILLS"
    assert classifier_service.detect_header("WORK EXPERIENCE") == "EXPERIENCE"
    assert classifier_service.detect_header("EDUCATION") == "EDUCATION"
    assert classifier_service.detect_header("ACHIEVEMENTS") == "ACHIEVEMENTS"
    assert classifier_service.detect_header("CERTIFICATIONS") == "CERTIFICATIONS"
    assert classifier_service.detect_header("SUMMARY") == "SUMMARY"
    assert classifier_service.detect_header("CONTACT INFORMATION") == "CONTACT"


def test_classify_resume_user_exact_structure(classifier_service):
    """
    Test resume with user's exact structure containing:
    TECHNICAL SKILLS, WORK EXPERIENCE, PROJECTS, and ACHIEVEMENTS.
    Ensures PROJECTS is deterministically detected and its blocks grouped correctly.
    """
    resume_text = (
        "TECHNICAL SKILLS\n"
        "Languages: Python, Java, JavaScript, TypeScript, C++, C, SQL, HTML/CSS\n"
        "Frameworks: React, Next.js, Node.js, Express.js, Flask\n"
        "Developer Tools: Git, GitHub, Docker, VS Code, Postman, CI/CD\n"
        "Technologies: REST APIs, NumPy, Pandas, TensorFlow, GCP\n\n"
        "WORK EXPERIENCE\n"
        "Software Engineering Intern, ProHance (Remote)\n"
        "• Developed and integrated interactive frontend features improving workflow efficiency.\n"
        "• Identified and resolved performance bottlenecks, reducing latency.\n"
        "• Contributed to backend API workflows ensuring modular architecture.\n\n"
        "PROJECTS\n"
        "MedSecure – HIPAA-Compliant Medical Records Platform\n"
        "• Built secure healthcare platform with role-based access control (RBAC), JWT authentication, and encrypted data storage.\n"
        "• Architected normalized relational database schema with optimized queries for efficient data retrieval.\n"
        "• Implemented secure API endpoints ensuring compliant data exchange and access control mechanisms.\n\n"
        "N.E.W.S – IoT Health Monitoring System\n"
        "• Developed distributed system processing real-time sensor data from 50+ IoT devices with 99.9% uptime.\n"
        "• Implemented ETL pipelines using Python to process sensor data.\n\n"
        "ACHIEVEMENTS\n"
        "• Smart India Hackathon 2025 – Grand Finalist (Top 5 in India)\n"
        "• Hackerzstreet (IEEE CS) – Finalist"
    )

    result = classifier_service.classify_resume(resume_text)

    # Core assertion: PROJECTS MUST be detected
    assert "PROJECTS" in result["detected_classes"]
    assert "SKILLS" in result["detected_classes"]
    assert "EXPERIENCE" in result["detected_classes"]
    assert "ACHIEVEMENTS" in result["detected_classes"]

    # Ensure projects content is grouped under PROJECTS
    assert "PROJECTS" in result["grouped_sections"]
    projects_content = " ".join(result["grouped_sections"]["PROJECTS"])
    assert "MedSecure" in projects_content
    assert "N.E.W.S" in projects_content

    # Validate integration with structural completeness engine
    from backend.app.services.resume_quality import calculate_structural_completeness
    completeness = calculate_structural_completeness(result["detected_classes"])
    assert "PROJECTS" in completeness["present_sections"]
    assert "PROJECTS" not in completeness["missing_sections"]

