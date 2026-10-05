"""
@file backend/tests/test_analyze_endpoint.py
@description Integration tests for /api/analyze and /api/health endpoints covering hybrid NLP.
@module backend.tests
"""

import io
import fitz  # PyMuPDF
from docx import Document
from fastapi.testclient import TestClient
import pytest

from backend.app.main import app
from backend.app.api.routes import llm_service

client = TestClient(app)


@pytest.fixture(autouse=True)
def ensure_mock_llm():
    """Ensure LLM service runs in mock mode during unit tests to conserve quota."""
    original_mode = llm_service.is_mock
    llm_service.is_mock = True
    yield
    llm_service.is_mock = original_mode


def create_sample_pdf_bytes(text: str) -> bytes:
    """Helper creating minimal in-memory PDF file."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def create_sample_docx_bytes(text: str) -> bytes:
    """Helper creating minimal in-memory DOCX file."""
    doc = Document()
    doc.add_paragraph(text)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


SAMPLE_RESUME = (
    "Jane Doe\n"
    "jane.doe@example.com | +1-555-0199 | github.com/janedoe | linkedin.com/in/janedoe\n\n"
    "Professional Summary\n"
    "Motivated Software Engineer with focus on full stack web applications.\n\n"
    "Education\n"
    "Bachelor of Science in Computer Science, State University, 2024\n\n"
    "Skills\n"
    "Python, JavaScript, TypeScript, React, FastAPI, Docker, PostgreSQL, Git\n\n"
    "Projects\n"
    "AI Resume Analyzer: Built with FastAPI, scikit-learn, and React. Reduced parsing latency by 35%.\n"
    "Cloud Microservices: Deployed containerized services on Docker for 10,000 active users.\n"
)


def test_health_check_endpoint():
    """Test /api/health returns 200 and indicates Hybrid NLP architecture."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["architecture"] == "HYBRID NLP + LLM"


def test_analyze_pdf_success_all_sections():
    """Test analyzing valid PDF with role and JD yields full 7-section payload."""
    pdf_bytes = create_sample_pdf_bytes(SAMPLE_RESUME)
    files = {"resume": ("resume.pdf", pdf_bytes, "application/pdf")}
    data = {
        "target_role": "Full Stack Engineer",
        "jd_text": "We need a Full Stack Engineer with Python, React, and Docker.",
    }

    response = client.post("/api/analyze", files=files, data=data)
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True

    payload = res["data"]
    # Check deterministic/custom NLP outputs
    assert "resume_structure" in payload
    assert payload["resume_structure"]["completeness_score"] > 0
    assert "contact_analysis" in payload
    assert payload["contact_analysis"]["email"] == "jane.doe@example.com"
    assert "skill_analysis" in payload
    assert "Python" in payload["skill_analysis"]["explicit_skills"]
    assert "achievement_analysis" in payload
    assert payload["achievement_analysis"]["achievements_count"] > 0

    # Check LLM / hybrid outputs
    assert "overall_analysis" in payload
    assert "role_analysis" in payload
    assert payload["role_analysis"]["target_role"] == "Full Stack Engineer"
    assert "job_match_analysis" in payload
    assert "Python" in payload["job_match_analysis"]["matching_skills"]


def test_analyze_docx_success():
    """Test analyzing valid DOCX resume without optional role or JD."""
    docx_bytes = create_sample_docx_bytes(SAMPLE_RESUME)
    files = {"resume": ("resume.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}

    response = client.post("/api/analyze", files=files)
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    payload = res["data"]
    assert payload["overall_analysis"] is not None
    assert payload["role_analysis"] is None
    assert payload["job_match_analysis"] is None


def test_analyze_invalid_extension():
    """Test uploading unsupported file format is rejected with 400."""
    files = {"resume": ("resume.txt", b"Unsupported plain text", "text/plain")}
    response = client.post("/api/analyze", files=files)
    assert response.status_code == 400
    assert "UNSUPPORTED_FORMAT" in response.text


def test_analyze_empty_resume_rejected():
    """Test empty document is rejected with 400 extraction error."""
    pdf_bytes = create_sample_pdf_bytes(" ")
    files = {"resume": ("empty.pdf", pdf_bytes, "application/pdf")}
    response = client.post("/api/analyze", files=files)
    assert response.status_code == 400
    assert "NO_TEXT_FOUND" in response.text or "EMPTY_DOCUMENT" in response.text


def test_analyze_too_short_resume_rejected():
    """Test resume with insufficient text content is rejected with 422 validation error."""
    pdf_bytes = create_sample_pdf_bytes("Just three words.")
    files = {"resume": ("short.pdf", pdf_bytes, "application/pdf")}
    response = client.post("/api/analyze", files=files)
    assert response.status_code == 422
    assert "TOO_SHORT" in response.text
