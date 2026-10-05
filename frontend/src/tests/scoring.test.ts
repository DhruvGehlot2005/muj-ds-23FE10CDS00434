/**
 * @file scoring.test.ts
 * @description Frontend unit tests for score clamping and hybrid NLP model contracts.
 * @module frontend/tests/scoring.test
 */

import { describe, expect, test } from "bun:test";
import { AnalyzeResponseData } from "../types";

describe("Score Clamping & Data Structure", () => {
  test("clamps scores correctly between 0 and 100", () => {
    const clamp = (val: number) => Math.max(0, Math.min(100, Math.round(val)));

    expect(clamp(85.4)).toBe(85);
    expect(clamp(-10)).toBe(0);
    expect(clamp(150)).toBe(100);
    expect(clamp(0)).toBe(0);
    expect(clamp(100)).toBe(100);
  });

  test("verifies hybrid AnalyzeResponseData contract", () => {
    const mockData: AnalyzeResponseData = {
      resume_structure: {
        completeness_score: 92,
        present_sections: ["EDUCATION", "SKILLS", "PROJECTS", "CONTACT"],
        missing_sections: [],
        optional_missing_sections: ["CERTIFICATIONS", "ACHIEVEMENTS"],
        classified_blocks: [
          { text: "Python, React", label: "SKILLS", confidence: 0.88 },
        ],
      },
      contact_analysis: {
        email: "test@example.com",
        phone: "+1-555-0199",
        linkedin: "https://linkedin.com/in/test",
        github: "https://github.com/test",
      },
      skill_analysis: {
        explicit_skills: ["Python", "React", "PostgreSQL"],
        categorized_skills: {
          "Programming Languages": ["Python"],
          "Frameworks": ["React"],
          "Databases": ["PostgreSQL"],
        },
        total_skills_count: 3,
      },
      achievement_analysis: {
        achievements_count: 1,
        achievements: [
          {
            statement: "Reduced latency by 35%",
            metric_type: "percentage",
            matched_text: "35%",
          },
        ],
        detected_metric_types: ["percentage"],
        quantification_score: 30,
      },
      overall_analysis: {
        overall_quality_score: 85,
        overall_score: 85,
        completeness_score: 90,
        clarity_score: 80,
        professionalism_score: 88,
        ats_compatibility_score: 82,
        ats_score: 82,
        strengths: ["Strong academic background"],
        weaknesses: ["Needs more quantifiable impact"],
        recommendations: ["Add metrics"],
      },
      role_analysis: {
        target_role: "Software Developer",
        role_compatibility_score: 80,
        role_match_score: 80,
        strengths: ["Python", "FastAPI"],
        weaknesses: ["CI/CD"],
        gaps: ["Kubernetes"],
        recommendations: ["Deploy a sample microservice"],
      },
      job_match_analysis: {
        lexical_similarity_score: 65.5,
        tfidf_similarity: 0.655,
        semantic_match_score: 82,
        match_score: 82,
        matching_skills: ["Python", "React"],
        missing_skills: ["Docker"],
        explicit_matches: [
          { requirement: "Python", evidence: "Built Python web apps" },
        ],
        partial_matches: [],
        missing_requirements: [],
        recommendations: ["Add Docker container experience"],
      },
    };

    expect(mockData.resume_structure.completeness_score).toBe(92);
    expect(mockData.skill_analysis.total_skills_count).toBe(3);
    expect(mockData.achievement_analysis.achievements_count).toBe(1);
    expect(mockData.overall_analysis.overall_quality_score).toBe(85);
    expect(mockData.job_match_analysis?.lexical_similarity_score).toBe(65.5);
    expect(mockData.job_match_analysis?.semantic_match_score).toBe(82);
  });
});
