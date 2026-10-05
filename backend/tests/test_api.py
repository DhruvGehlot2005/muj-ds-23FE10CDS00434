"""
@file test_api.py
@description Integration tests for FastAPI endpoints, request handling, and error contracts
@module backend.tests.test_api
"""

import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)
TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "tests")


def test_health_check():
    """Verifies health check endpoint returns 200 and healthy status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_security_headers():
    """Verifies essential OWASP security headers are present in responses."""
    response = client.get("/api/health")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"


def test_analyze_valid_pdf_without_role_or_jd():
    """Tests resume analysis with neither target role nor JD."""
    pdf_path = os.path.join(TEST_DATA_DIR, "sample_resume.pdf")
    with open(pdf_path, "rb") as f:
        response = client.post(
            "/api/analyze",
            files={"resume": ("sample_resume.pdf", f, "application/pdf")},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "overall_analysis" in body["data"]
    assert body["data"]["role_analysis"] is None
    assert body["data"]["job_match_analysis"] is None


def test_analyze_target_role_without_jd():
    """Tests resume analysis with target role but no JD."""
    pdf_path = os.path.join(TEST_DATA_DIR, "sample_resume.pdf")
    with open(pdf_path, "rb") as f:
        response = client.post(
            "/api/analyze",
            files={"resume": ("sample_resume.pdf", f, "application/pdf")},
            data={"target_role": "Full Stack Developer"},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["overall_analysis"] is not None
    assert body["data"]["role_analysis"] is not None
    assert body["data"]["role_analysis"]["target_role"] == "Full Stack Developer"
    assert body["data"]["job_match_analysis"] is None


def test_analyze_jd_without_target_role():
    """Tests resume analysis with JD text but no target role."""
    pdf_path = os.path.join(TEST_DATA_DIR, "sample_resume.pdf")
    with open(pdf_path, "rb") as f:
        response = client.post(
            "/api/analyze",
            files={"resume": ("sample_resume.pdf", f, "application/pdf")},
            data={"jd_text": "We are seeking a Python and FastAPI engineer with relational database skills."},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["overall_analysis"] is not None
    assert body["data"]["role_analysis"] is None
    assert body["data"]["job_match_analysis"] is not None
    assert len(body["data"]["job_match_analysis"]["matching_skills"]) > 0


def test_analyze_both_target_role_and_jd():
    """Tests resume analysis with both target role and JD."""
    docx_path = os.path.join(TEST_DATA_DIR, "sample_resume.docx")
    with open(docx_path, "rb") as f:
        response = client.post(
            "/api/analyze",
            files={"resume": ("sample_resume.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
            data={
                "target_role": "Data Analyst",
                "jd_text": "Looking for a Data Analyst with experience in SQL, Python, Pandas, and dashboard design.",
            },
        )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["overall_analysis"] is not None
    assert body["data"]["role_analysis"] is not None
    assert body["data"]["role_analysis"]["target_role"] == "Data Analyst"
    assert body["data"]["job_match_analysis"] is not None


def test_analyze_invalid_file_extension():
    """Tests uploading an unsupported file format (.txt) returns 400 Bad Request."""
    response = client.post(
        "/api/analyze",
        files={"resume": ("test.txt", b"Unsupported plain text file", "text/plain")},
    )
    assert response.status_code == 400
    body = response.json()
    assert body["error"] == "UNSUPPORTED_FORMAT"


def test_analyze_empty_file():
    """Tests uploading a 0-byte file returns 400 Bad Request."""
    response = client.post(
        "/api/analyze",
        files={"resume": ("empty.pdf", b"", "application/pdf")},
    )
    assert response.status_code == 400
    body = response.json()
    assert body["error"] == "EMPTY_FILE"


def test_analyze_non_resume_document():
    """Tests uploading a non-resume document returns 422 Unprocessable Entity."""
    recipe_path = os.path.join(TEST_DATA_DIR, "recipe_not_resume.pdf")
    with open(recipe_path, "rb") as f:
        response = client.post(
            "/api/analyze",
            files={"resume": ("recipe_not_resume.pdf", f, "application/pdf")},
        )
    assert response.status_code == 422
    body = response.json()
    assert body["error"] == "NOT_A_RESUME"
