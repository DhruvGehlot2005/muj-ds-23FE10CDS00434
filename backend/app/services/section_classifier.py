"""
@file section_classifier.py
@description Inference service for resume block segmentation and supervised section classification
@module backend.app.services.section_classifier
"""

import os
import re
from typing import Dict, List, Optional, Tuple, Any

import joblib
from backend.app.config import settings
from backend.app.utils.logger import logger


# Canonical section header patterns for hybrid deterministic + ML parsing
SECTION_HEADER_PATTERNS: Dict[str, re.Pattern] = {
    "PROJECTS": re.compile(
        r"^(?:#*\s*)?(?:(?:academic|personal|key|technical|selected|featured|software|engineering|capstone|side|recent|major|notable|coursework|undergraduate|representative|hands-on)\s+)?projects?(?:\s*(?:work|portfolio|experience|highlights|undertaken|showcase|&|\+|and|/))?(?:\s*[:\-_|•/])?$",
        re.IGNORECASE,
    ),
    "EXPERIENCE": re.compile(
        r"^(?:#*\s*)?(?:(?:work|professional|employment|industry|relevant|internship|career|job|practical|hands-on)\s+)?(?:experience|history|employment|internships?|appointments?|engagements?)(?:\s*[:\-_|•/])?$",
        re.IGNORECASE,
    ),
    "EDUCATION": re.compile(
        r"^(?:#*\s*)?(?:(?:academic|educational|education\s*(?:&|and|\+|/)\s*training)\s+)?(?:education|qualifications?|background|academics?|degrees?)(?:\s*[:\-_|•/])?$",
        re.IGNORECASE,
    ),
    "SKILLS": re.compile(
        r"^(?:#*\s*)?(?:(?:technical|core|key|professional|software|computer|programming|domain|functional|primary)\s+)?(?:skills|competencies|proficiencies|technologies|tools|stack|strengths|abilities)(?:\s*(?:&|and|\+|/)\s*(?:tools|technologies|frameworks|competencies|abilities))?(?:\s*[:\-_|•/])?$",
        re.IGNORECASE,
    ),
    "ACHIEVEMENTS": re.compile(
        r"^(?:#*\s*)?(?:(?:key|major|academic|scholastic|honors?\s*(?:&|and|\+|/)\s*)?achievements?|awards?(?:\s*(?:&|and|\+|/)\s*honors?)?|honors?|accomplishments?|competitions?|hackathons?|accolades?|extracurricular(?:s|\s+activities)?)(?:\s*[:\-_|•/])?$",
        re.IGNORECASE,
    ),
    "CERTIFICATIONS": re.compile(
        r"^(?:#*\s*)?(?:(?:licenses?\s*(?:&|and|\+|/)\s*)?certifications?|certificates?|credentials?|accreditations?|courses?|training)(?:\s*[:\-_|•/])?$",
        re.IGNORECASE,
    ),
    "SUMMARY": re.compile(
        r"^(?:#*\s*)?(?:(?:professional|career|executive|personal)\s+)?(?:summary|profile|objective|overview|about\s+me|statement|biography)(?:\s*[:\-_|•/])?$",
        re.IGNORECASE,
    ),
    "CONTACT": re.compile(
        r"^(?:#*\s*)?(?:contact(?:\s*(?:info|information|details))?|personal\s+details|personal\s+info)(?:\s*[:\-_|•/])?$",
        re.IGNORECASE,
    ),
}


class SectionClassifierService:
    """Loads trained ML pipeline to segment resume text and predict section classes with confidence thresholding."""

    def __init__(self, model_path: Optional[str] = None):
        """
        Initializes the classifier service.

        @param model_path: Optional custom path to .joblib model artifact
        @raises FileNotFoundError: If model artifact does not exist
        """
        candidate_paths = [
            model_path,
            os.path.join("data", "models", "resume_section_classifier.joblib"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "models", "resume_section_classifier.joblib"),
        ]

        self.model_path = None
        for p in candidate_paths:
            if p and os.path.exists(p):
                self.model_path = p
                break

        if not self.model_path:
            raise FileNotFoundError(
                "Trained section classifier model artifact 'resume_section_classifier.joblib' was not found. "
                "Please run the offline training script 'backend/app/ml/train_section_classifier.py' first."
            )

        logger.info(f"Loading trained section classifier from: {self.model_path}")
        self.pipeline = joblib.load(self.model_path)
        self.classes = list(self.pipeline.classes_)
        self.confidence_threshold = settings.section_classifier_confidence_threshold

    @staticmethod
    def detect_header(line: str) -> Optional[str]:
        """
        Determines if a candidate string matches a standard resume section header.
        Supports markdown markers, trailing punctuation, letter-spaced headings,
        numbered prefixes, and parenthetical qualifiers.

        @param line: Candidate text line
        @return Matching canonical section label or None
        """
        if not line or not isinstance(line, str):
            return None

        # Clean leading and trailing markdown, punctuation, and bullets
        cleaned = re.sub(r"^[\s#*\-_:•|~`\(\)\[\]{}]+|[\s#*\-_:•|~`\(\)\[\]{}]+$", "", line).strip()
        if not cleaned:
            return None

        # Strip optional list numbers: "1. ", "3) ", "IV. "
        cleaned = re.sub(r"^(?:(?:\d+|[ivxIVX]+)[\.\)]\s*)+", "", cleaned).strip()

        # Candidate variants
        cleaned_no_parens = re.sub(r"\s*[\(\[][^\)\]]*[\)\]]$", "", cleaned).strip()
        condensed = re.sub(r"(?<=\b[A-Za-z])\s+(?=[A-Za-z]\b)", "", cleaned)
        condensed_no_parens = re.sub(r"(?<=\b[A-Za-z])\s+(?=[A-Za-z]\b)", "", cleaned_no_parens)

        candidates = [cleaned, cleaned_no_parens, condensed, condensed_no_parens]

        for cand in candidates:
            if not cand or len(cand) > 60:
                continue
            for label, pattern in SECTION_HEADER_PATTERNS.items():
                if pattern.match(cand):
                    return label

        return None

    def segment_text(self, text: str) -> List[str]:
        """
        Segments raw extracted resume text into meaningful logical blocks,
        ensuring explicit section boundaries are cleanly isolated.

        @param text: Raw resume string
        @return List of non-empty text blocks
        """
        if not text or not text.strip():
            return []

        # Isolate recognized section headers onto their own paragraph boundaries
        lines = text.strip().split("\n")
        normalized_lines = []
        for line in lines:
            stripped = line.strip()
            # Check for inline colon separator (e.g., "PROJECTS: MedSecure Platform...")
            if ":" in stripped:
                colon_parts = stripped.split(":", 1)
                prefix_header = self.detect_header(colon_parts[0].strip())
                if prefix_header:
                    normalized_lines.append(f"\n\n{colon_parts[0].strip()}\n\n{colon_parts[1].strip()}\n\n")
                    continue

            if self.detect_header(stripped):
                normalized_lines.append(f"\n\n{stripped}\n\n")
            else:
                normalized_lines.append(line)
        normalized_text = "\n".join(normalized_lines)

        # Split on two or more consecutive newlines (standard paragraph/block delimiter)
        raw_blocks = re.split(r"\n\s*\n+", normalized_text.strip())
        blocks = []

        for b in raw_blocks:
            cleaned = b.strip()
            if len(cleaned) >= 3:
                blocks.append(cleaned)

        # Fallback if no double newlines exist (e.g. single-spaced plain text)
        if len(blocks) <= 1 and "\n" in text:
            single_lines = [line.strip() for line in text.split("\n") if len(line.strip()) >= 3]
            if len(single_lines) > len(blocks):
                blocks = single_lines

        return blocks

    def predict_block(self, block_text: str) -> Dict[str, Any]:
        """
        Predicts section class label and confidence score for a single text block,
        combining deterministic header matching with supervised ML classification.

        @param block_text: Text snippet to classify
        @return Dictionary with text, label, confidence, raw_label, and threshold_applied
        """
        # 1. Deterministic header match on first line or entire block
        first_line = block_text.split("\n")[0].strip()
        header_match = self.detect_header(first_line) or self.detect_header(block_text.strip())
        if header_match:
            return {
                "text": block_text,
                "label": header_match,
                "confidence": 1.0,
                "raw_label": header_match,
                "threshold_applied": False,
            }

        # 2. Supervised ML Pipeline feature extraction and inference
        cleaned = block_text.lower().strip()
        cleaned = re.sub(r"https?://\S+|www\.\S+", "url_token", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned)

        probabilities = self.pipeline.predict_proba([cleaned])[0]
        max_idx = int(probabilities.argmax())
        confidence = float(probabilities[max_idx])
        raw_label = self.classes[max_idx]

        # Apply confidence threshold
        assigned_label = raw_label if confidence >= self.confidence_threshold else "OTHER"

        return {
            "text": block_text,
            "label": assigned_label,
            "confidence": round(confidence, 4),
            "raw_label": raw_label,
            "threshold_applied": confidence < self.confidence_threshold,
        }

    def classify_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Segments resume text, classifies each block with active section-context propagation,
        and groups content by section label.

        @param resume_text: Full resume text
        @return Structured classification summary with sections list and grouped dictionary
        """
        blocks = self.segment_text(resume_text)
        classified_blocks: List[Dict[str, Any]] = []
        grouped: Dict[str, List[str]] = {}
        detected_sections: set = set()

        # Step 1: Scan entire resume for any explicit section headers
        for line in resume_text.split("\n"):
            header = self.detect_header(line.strip())
            if header:
                detected_sections.add(header)

        # Step 2: Context-aware block classification loop
        current_section: Optional[str] = None

        for b in blocks:
            # Check if this block is (or starts with) a section header
            first_line = b.split("\n")[0].strip()
            block_header = self.detect_header(first_line) or self.detect_header(b.strip())

            if block_header:
                current_section = block_header
                detected_sections.add(block_header)
                block_info = {
                    "text": b,
                    "label": block_header,
                    "confidence": 1.0,
                    "raw_label": block_header,
                    "threshold_applied": False,
                }
                classified_blocks.append(block_info)
                if block_header not in grouped:
                    grouped[block_header] = []
                grouped[block_header].append(b)
                continue

            # Content block: run supervised ML inference
            ml_pred = self.predict_block(b)

            if current_section:
                # Inside an explicit section, inherit active section context
                # (e.g., bullet points under PROJECTS belong to PROJECTS)
                assigned_label = current_section
                assigned_conf = max(ml_pred["confidence"], 0.90)
                raw_label = ml_pred["raw_label"]
            else:
                assigned_label = ml_pred["label"]
                assigned_conf = ml_pred["confidence"]
                raw_label = ml_pred["raw_label"]

            if assigned_label != "OTHER":
                detected_sections.add(assigned_label)

            if assigned_label not in grouped:
                grouped[assigned_label] = []
            grouped[assigned_label].append(b)

            classified_blocks.append({
                "text": b,
                "label": assigned_label,
                "confidence": round(assigned_conf, 4),
                "raw_label": raw_label,
                "threshold_applied": assigned_label == "OTHER",
            })

        return {
            "sections": classified_blocks,
            "grouped_sections": grouped,
            "detected_classes": sorted(list(detected_sections)),
            "total_blocks": len(classified_blocks),
            "confidence_threshold": self.confidence_threshold,
        }
