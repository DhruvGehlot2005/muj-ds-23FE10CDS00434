# Project Overview
**ResLens** (AI-Powered Resume Analyzer and Job Compatibility Assessment System) is an academic hybrid NLP + LLM platform.
It purposefully combines:
1. **Custom Supervised NLP/ML**: Resume section classification using TF-IDF + Logistic Regression trained on a curated academic dataset (405 samples across 9 classes).
2. **Deterministic NLP**: Regex-based contact extraction, vocabulary-driven skill extraction with alias normalization, quantification/achievement detection, and structural completeness scoring.
3. **Statistical NLP**: TF-IDF feature extraction and cosine lexical similarity computation between resumes and job descriptions.
4. **LLM-Based Semantic Reasoning**: Google Gemini API powered by structured evidence outputs from our custom NLP pipeline rather than raw unparsed text.

The system ensures that deterministic and statistical facts are computed locally with zero hallucination, while Gemini performs high-level semantic reasoning, role alignment, and contextual recommendations.

# Tech Stack
- **Frontend Runtime & Tooling**: Bun (strictly no Node/npm/yarn/pnpm/Vite/Webpack)
- **Frontend Core**: React 19, TypeScript, Tailwind CSS, Lucide React
- **Backend Runtime**: Python 3.11 (Conda environment: `reslens`, launcher: `run_backend.ps1`)
- **Backend Framework**: FastAPI, Pydantic v2, SlowAPI, Bleach
- **Document Processing**: PyMuPDF (`fitz` for PDF) and `python-docx` (DOCX) in-memory extraction
- **Machine Learning & NLP**: scikit-learn (`TfidfVectorizer`, `LogisticRegression(C=8.0)`, `Pipeline`), pandas, numpy, joblib
- **LLM Integration**: Google Gemini API (`google-genai` SDK) with prompt externalization and multi-model fallback cascade (`gemini-3.5-flash-lite`, `gemini-flash-latest`, `gemini-3.8-flash`)
- **Testing**: `pytest` for backend unit/integration tests (62 passing); `bun test` for frontend tests (7 passing)

# Architecture
```
                         USER
                          │
                          ▼
                  Resume PDF / DOCX
                          │
                          ▼
                  Text Extraction (PyMuPDF / python-docx)
                          │
                          ▼
                 Resume Preprocessing & Sanitization (bleach)
                          │
            ┌─────────────┴─────────────┐
            ▼                           ▼
      CUSTOM NLP / ML             DETERMINISTIC NLP
            │                           │
   Section Classifier            Skill Extraction (data/skills.json + aliases)
   TF-IDF + Logistic             Contact Extraction (regex)
   Regression (scikit-learn)     Achievement Detection (metrics)
            │                     Completeness Analysis (structural scores)
            └─────────────┬─────────────┘
                          │
                          ▼
                Structured Resume Evidence Data
                          │
             ┌────────────┴─────────────┐
             ▼                          ▼
        Target Role               Job Description
             │                          │
             │                          ▼
             │                   JD Preprocessing & Extraction
             │                          │
             │                          ▼
             │                   TF-IDF Lexical Similarity & JD Skills
             │                          │
             └────────────┬─────────────┘
                          │
                          ▼
                     GEMINI API
             (Operating strictly on structured NLP evidence)
                          │
             ┌────────────┼─────────────┐
             ▼            ▼             ▼
        Overall        Target Role    JD Semantic
        Semantic       Alignment      Match & Gap
        Audit          Reasoning      Analysis
             │            │             │
             └────────────┼─────────────┘
                          │
                          ▼
                    Final Dashboard
        (7 Visually Separated Academic Panels)
```

# Feature Status
- [x] Project inspection
- [x] Dataset creation (`data/training/resume_sections.csv` - 405 samples)
- [x] Dataset validation (`data/training/dataset_statistics.json`)
- [x] Separate unseen test set (`data/tests/resume_section_test_cases.csv` - 63 samples)
- [x] Skills vocabulary and alias normalization (`data/skills.json`)
- [x] Section classifier pipeline (`backend/app/ml/train_section_classifier.py`)
- [x] Model training and artifacts (`data/models/resume_section_classifier.joblib`)
- [x] Model evaluation (85.19% Val Accuracy, 96.83% Unseen Test Accuracy)
- [x] Model inference service with confidence thresholding (`backend/app/services/section_classifier.py`)
- [x] Resume completeness engine (`backend/app/services/resume_quality.py`)
- [x] Deterministic contact extraction (`backend/app/services/contact_extractor.py`)
- [x] Deterministic skill extraction with alias resolution (`backend/app/services/skill_extractor.py`)
- [x] Quantified achievement detection (`backend/app/services/achievement_detector.py`)
- [x] Statistical TF-IDF lexical similarity (`backend/app/services/text_similarity.py`)
- [x] JD deterministic skill overlap & gap analysis
- [x] Structured Gemini evidence pipeline
- [x] Externalized prompt templates in YAML format (`backend/app/prompts/prompts.yaml`, `backend/prompts/prompts.yaml`)
- [x] Central YAML configuration (`backend/config.yaml`, `config.yaml`) integrated with Pydantic BaseSettings
- [x] Structured Gemini output parsing with fallback cascade
- [x] Pydantic v2 schemas and model validators
- [x] Target role semantic analysis
- [x] JD semantic qualification analysis
- [x] Frontend 7-section dashboard integration (React 19 + Bun, clean minimalist ResLens branding)
- [x] Error handling & input validation
- [x] Security (OWASP rate limiting, bleach sanitization, no PII logging)
- [x] Backend unit & integration tests (62 passing)
- [x] Frontend unit tests (7 passing)
- [x] Comprehensive README with academic defense
- [x] Final validation & QA
- [x] Deterministic Section Header Recognition & Context Propagation (eliminates false negative missing sections for PROJECTS and canonical sections)
- [x] Unified Prompt Placeholder Grounding & Contact Auto-Registration (ensures {resume_text} and {evidence_json} are fully populated, eliminating false "no resume text provided" hallucinations and 0/100 score drops)

# Data Models
### Structured Evidence Sent to Gemini
```json
{
  "resume_text": "Jane Doe \n Software Engineer...",
  "resume_sections": {
    "EDUCATION": ["..."],
    "SKILLS": ["..."],
    "EXPERIENCE": ["..."],
    "PROJECTS": ["..."]
  },
  "explicit_skills": ["Python", "React", "PostgreSQL", "Docker"],
  "categorized_skills": {
    "Programming Languages": ["Python"],
    "Frameworks": ["React"],
    "Databases": ["PostgreSQL"]
  },
  "structural_completeness": {
    "score": 100,
    "present_sections": ["CONTACT", "EDUCATION", "SKILLS", "PROJECTS"],
    "missing_sections": []
  },
  "contact_analysis": {
    "email": true,
    "phone": true,
    "linkedin": true,
    "github": true
  },
  "quantified_achievements": [
    "Reduced API latency by 35%",
    "Served 10,000 active users"
  ],
  "quantification_density_score": 55,
  "target_role": "Software Developer",
  "job_description_summary": {
    "lexical_similarity_score": 68.5,
    "matching_skills": ["Python", "React"],
    "missing_skills": ["Kubernetes"]
  }
}
```

### Complete Unified API Contract (`POST /api/analyze`)
```json
{
  "success": true,
  "data": {
    "resume_structure": {
      "completeness_score": 100,
      "present_sections": ["CONTACT", "EDUCATION", "SKILLS", "PROJECTS"],
      "missing_sections": [],
      "optional_missing_sections": ["CERTIFICATIONS", "ACHIEVEMENTS"],
      "classified_blocks": [
        {
          "text": "Programming Languages: Python, Java, C++, TypeScript, SQL",
          "label": "SKILLS",
          "confidence": 0.8509
        }
      ]
    },
    "contact_analysis": {
      "email": "jane.doe@example.com",
      "phone": "+1-555-0199",
      "linkedin": "https://linkedin.com/in/janedoe",
      "github": "https://github.com/janedoe"
    },
    "skill_analysis": {
      "explicit_skills": ["Docker", "Git", "PostgreSQL", "Python", "React"],
      "categorized_skills": {
        "Programming Languages": ["Python"],
        "Frameworks": ["React"],
        "Databases": ["PostgreSQL"],
        "DevOps": ["Docker", "Git"]
      },
      "total_skills_count": 5
    },
    "achievement_analysis": {
      "achievements_count": 2,
      "achievements": [
        {
          "statement": "AI Resume Analyzer: Built with FastAPI. Reduced parsing latency by 35%.",
          "metric_type": "percentage",
          "matched_text": "by 35%"
        }
      ],
      "detected_metric_types": ["percentage", "scale_volume"],
      "quantification_score": 55
    },
    "overall_analysis": {
      "overall_quality_score": 84,
      "clarity_score": 86,
      "professionalism_score": 88,
      "ats_compatibility_score": 85,
      "strengths": ["Clearly identified core technical skills."],
      "weaknesses": ["Project bullet points could feature more direct metrics."],
      "recommendations": ["Quantify project outcomes with specific metrics."]
    },
    "role_analysis": {
      "target_role": "Full Stack Engineer",
      "role_compatibility_score": 82,
      "strengths": ["Core programming competencies directly relevant."],
      "weaknesses": ["Limited explicit mention of production monitoring."],
      "gaps": ["Advanced cloud infrastructure tools commonly expected."],
      "recommendations": ["Include unit test coverage in project descriptions."]
    },
    "job_match_analysis": {
      "lexical_similarity_score": 68.5,
      "tfidf_similarity": 0.685,
      "semantic_match_score": 80,
      "matching_skills": ["Python", "React"],
      "missing_skills": ["Kubernetes"],
      "explicit_matches": [
        { "requirement": "REST APIs", "evidence": "Built RESTful services with FastAPI" }
      ],
      "partial_matches": [
        { "requirement": "Cloud", "evidence": "AWS coursework", "gap": "Lacks production CI/CD" }
      ],
      "missing_requirements": [
        { "requirement": "Kubernetes", "importance": "PREFERRED" }
      ],
      "recommendations": ["Add explicit mentions of containerization tooling."]
    }
  }
}
```

# API Contracts
- `POST /api/analyze`: Multipart form input with `resume` (PDF/DOCX, max 10MB), optional `target_role`, optional `jd_file` (PDF/DOCX), optional `jd_text`.
- `GET /api/health`: Returns system status (`healthy`), version (`2.0.0`), architecture (`HYBRID NLP + LLM`), classifier load status, and LLM configuration.

# Technical Debt & Resiliency Notes
- Integrated API reverse proxy in `frontend/server.ts` to forward `/api/*` to `127.0.0.1:8000` solving cross-origin connectivity.
- Implemented multi-model fallback cascade in `llm_service.py` (`gemini-3.5-flash-lite`, `gemini-flash-latest`, `gemini-3.8-flash`) with exponential backoff retry.
- Supervised Section classifier uses scikit-learn Pipeline with `TfidfVectorizer` + `LogisticRegression(C=8.0, max_iter=1000)` and confidence thresholding (0.60, falls back to `OTHER`).
- Hybrid Deterministic + ML Section Parsing: Augmented raw statistical classifier with regex-based canonical header detection (`detect_header`) supporting diverse formatting (markdown markers, parenthetical annotations, letter-spacing, and numbered prefixes). Added full-document pre-scanning and active section-context propagation so technical bullets under `PROJECTS` remain accurately attributed rather than misclassified as `EXPERIENCE`.
- Prompt Template Synchronization & Fallback Safety: Unified prompt library in `prompts.yaml` and modular YAML files providing both `{evidence_json}` and `{resume_text}` placeholders. `llm_service.py` ensures both structured evidence and raw resume text are comprehensively substituted across all analysis endpoints, eliminating prompt placeholder mismatch bugs.
- Contact Auto-Registration: `routes.py` registers extracted contact items (email, phone, LinkedIn, GitHub) into `detected_sections` before structural completeness scoring, preventing false negative "missing contact" flags.
- Frontend Hero Headline: Refined hero header in `App.tsx` from generic system label to high-impact value proposition: *"Bridge the gap between your resume and your dream job."*
- UploadZone UI Streamlining: Removed redundant secondary helper descriptions, `(Optional)` label tags, the red asterisk, and the `(Supported formats: PDF, DOCX)` subtext from the resume document label in `UploadZone.tsx` for a clean, minimal interface.
- Subtle & Compact Input Placeholders: Replaced long placeholder text with short hints (`e.g. Software Engineer` and `Paste job description...`) styled with subtle opacity globally in `index.css` and `UploadZone.tsx` matching modern job board ergonomics (Joblet style).
- Results Dashboard Streamlining: Removed academic metadata tags (`Section 1 • LLM Semantic Analysis`, `Section 2 • Deterministic + ML`, `Section 3 • Deterministic NLP`, `Section 4 • Deterministic Pattern NLP`, `Section 5 • Target Role Alignment`, `Section 6 • Statistical + Semantic Match`) and their verbose methodology description paragraphs across `OverallScoreCard.tsx`, `ResumeStructureCard.tsx`, `ExplicitSkillsCard.tsx`, `AchievementCard.tsx`, `RoleCompatibilityCard.tsx`, and `JobMatchCard.tsx` for a clean, product-grade UI.
- Frontend Dev Server Auto-Build & Watch Mode: Enhanced `frontend/server.ts` to automatically run `build.ts` on startup and watch `src/` for file changes with debounced automatic recompilation, eliminating the need to manually invoke `bun run build`.
- Documentation Streamlining: Fully refactored `README.md` into a concise, easy-to-read developer guide featuring an intuitive architecture diagram, clear description of the custom TF-IDF + Logistic Regression Section Classifier, clear Anaconda/venv setup instructions, explicit documentation on targeted LLM usage (conveying core independence), and eliminating extraneous academic defense text.






