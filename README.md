# ResLens: Resume Analyzer & Job Matcher

ResLens is a practical Natural Language Processing (NLP) system designed to evaluate resume quality and match candidate qualifications against job descriptions.

It uses local, deterministic NLP and custom machine learning for all factual data processing (skills, sections, achievements, and keyword similarity), and uses a targeted LLM API call exclusively for contextual feedback and synthesis.

---

## 1. Simple Architecture

```
                      +-------------------------+
                      |   Resume (PDF / DOCX)   |
                      +-------------------------+
                                   |
                                   v
                      +-------------------------+
                      |   Text Extraction       |
                      |   (PyMuPDF / docx)      |
                      +-------------------------+
                                   |
            +----------------------+----------------------+
            |                                             |
            v                                             v
+-----------------------+                     +-----------------------+
|  Custom NLP & ML      |                     |  Job Matching (NLP)   |
|-----------------------|                     |-----------------------|
| - Section Classifier  |                     | - TF-IDF Overlap      |
|   (TF-IDF + LogReg)   |                     | - Skill Gap Analysis  |
| - Skill Extraction    |                     | - Keyword Match %     |
| - Achievement Metrics |                     +-----------------------+
| - Contact Detection   |                                 |
+-----------------------+                                 |
            |                                             |
            +----------------------+----------------------+
                                   |
                                   v
                      +-------------------------+
                      | Structured Evidence     |
                      | (Facts, Counts, Scores) |
                      +-------------------------+
                                   |
                                   v  (Sent only for qualitative feedback)
                      +-------------------------+
                      | LLM API (Google Gemini) |
                      | - Qualitative Advice    |
                      | - Role Alignment Tips   |
                      +-------------------------+
                                   |
                                   v
                      +-------------------------+
                      |  React Web Dashboard    |
                      |  (Score & Feedback UI)  |
                      +-------------------------+
```

### How to Explain This Architecture
1. **Local NLP & ML does the heavy lifting**: The system extracts text, classifies sections using a custom machine learning model, identifies verified skills, and computes keyword similarity.
2. **Data-first evidence**: All scores, detected sections, and matched skills are calculated locally with 100% mathematical consistency (no hallucinations).
3. **Targeted LLM use**: The LLM API receives the extracted facts to write helpful qualitative recommendations. The core functionality does not depend on the LLM to understand or parse the document.

---

## 2. The Machine Learning Model

ResLens uses a **custom-trained Supervised Text Classifier** built with `scikit-learn`:

- **Algorithm**: `TF-IDF Vectorizer` (word & bi-gram features) paired with `Logistic Regression`.
- **Purpose**: Automatically identifies and categorizes resume blocks into 9 canonical sections (`CONTACT`, `EDUCATION`, `EXPERIENCE`, `PROJECTS`, `SKILLS`, `CERTIFICATIONS`, `SUMMARY`, `PUBLICATIONS`, `OTHER`).
- **Confidence Guard**: Uses a 0.60 probability threshold to ensure reliable classification, safely categorizing ambiguous text as `OTHER`.
- **Why It Matters**: Instead of relying on rigid keyword searches or slow API prompts to read the resume, this local ML pipeline accurately segments the document in milliseconds with consistent, verifiable results.

---

## 3. Where the LLM API is Used 

The system is **not** a simple wrapper around an AI prompt. The entire document parsing, section identification, skill cataloging, and lexical overlap calculations run completely locally.

The Google Gemini API is used for a single, specific purpose:
- **Qualitative Advice & Synthesis**: Reviewing the structured evidence produced by our NLP pipeline to provide actionable writing suggestions, identify qualitative gaps, and offer role-specific guidance.

> **Key Takeaway**: If the LLM API is unavailable, the core system still parses the resume, classifies every section, extracts all verified skills, computes structural completeness, and calculates job match percentages.

---

## 4. Getting Started & Setup

You can run ResLens using **any Python environment** (Anaconda, Miniconda, `venv`, or system Python).

### Prerequisites
- **Python**: Version 3.10 or 3.11
- **Node/Runtime**: [Bun](https://bun.sh/) (recommended) or any modern browser for the frontend

---

### Step 1: Environment Setup

#### Option A: Using Anaconda / Miniconda (Recommended)
Open Anaconda Prompt (or your terminal) and run:

```bash
# 1. Create a clean Python 3.11 environment
conda create -n reslens python=3.11 -y

# 2. Activate the environment
conda activate reslens

# 3. Navigate to the project root directory
cd path/to/NLP_Project

# 4. Install backend dependencies
pip install -r backend/requirements.txt
```

#### Option B: Using Standard Python Virtual Environment (`venv`)
If you prefer not to use Conda:

```bash
# 1. Create a virtual environment
python -m venv venv

# 2. Activate it
# On Windows:
.\venv\Scripts\activate
# On macOS / Linux:
source venv/bin/activate

# 3. Install backend dependencies
pip install -r backend/requirements.txt
```

---

### Step 2: Configure Environment Variables

Create a `.env` file in the project root:

```env
# Google Gemini API key (used for qualitative recommendations)
GEMINI_API_KEY=your_gemini_api_key_here
```

*(Note: If you run without an API key, the system operates in mock/fallback mode for testing).*

---

### Step 3: Run the Application

You will run two small processes in separate terminal windows:

#### Terminal 1 — Backend (FastAPI)
Ensure your environment (`reslens` or `venv`) is active:

```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
*Backend API will run at: `http://127.0.0.1:8000`*

#### Terminal 2 — Frontend (React UI)
From the project root:

```bash
cd frontend
bun run dev
```
*Frontend interface will run at: `http://localhost:3000`*

---

## 5. Using the System

1. Open your browser to `http://localhost:3000`.
2. Drag and drop or select a resume (**PDF** or **DOCX**).
3. *(Optional)* Enter a target job title or paste a Job Description.
4. Click **Analyze Resume** to view:
   - Overall Quality and ATS readiness score
   - Structural Completeness & identified sections
   - Verified skills grouped by category
   - Quantified achievements and metrics detected
   - Job match alignment and skill gap breakdown
