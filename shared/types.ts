/**
 * @file types.ts
 * @description Shared TypeScript interfaces representing the Hybrid NLP Resume Analyzer API contract.
 * @module shared/types
 */

export interface ClassifiedBlock {
  text: string;
  label: string;
  confidence: number;
}

export interface ResumeStructureData {
  completeness_score: number;
  present_sections: string[];
  missing_sections: string[];
  optional_missing_sections: string[];
  classified_blocks: ClassifiedBlock[];
}

export interface ContactAnalysisData {
  email: string | null;
  phone: string | null;
  linkedin: string | null;
  github: string | null;
}

export interface SkillAnalysisData {
  explicit_skills: string[];
  categorized_skills: Record<string, string[]>;
  total_skills_count: number;
}

export interface AchievementItem {
  statement: string;
  metric_type: string;
  matched_text: string;
}

export interface AchievementAnalysisData {
  achievements_count: number;
  achievements: AchievementItem[];
  detected_metric_types: string[];
  quantification_score: number;
}

export interface OverallAnalysis {
  overall_quality_score: number;
  overall_score?: number;
  clarity_score: number;
  professionalism_score: number;
  ats_compatibility_score: number;
  ats_score?: number;
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
}

export interface RoleAnalysis {
  target_role: string;
  role_compatibility_score: number;
  role_match_score?: number;
  strengths: string[];
  matching_areas?: string[];
  weaknesses: string[];
  weak_areas?: string[];
  gaps: string[];
  missing_areas?: string[];
  recommendations: string[];
}

export interface ExplicitMatchItem {
  requirement: string;
  evidence: string;
}

export interface PartialMatchItem {
  requirement: string;
  evidence: string;
  gap?: string;
}

export interface MissingRequirementItem {
  requirement: string;
  importance?: string;
}

export interface JobMatchAnalysis {
  lexical_similarity_score: number;
  tfidf_similarity: number;
  semantic_match_score: number;
  match_score?: number;
  matching_skills: string[];
  missing_skills: string[];
  explicit_matches: (ExplicitMatchItem | string)[];
  partial_matches: (PartialMatchItem | string)[];
  missing_requirements: (MissingRequirementItem | string)[];
  recommendations: string[];
}

export interface AnalyzeResponseData {
  resume_structure: ResumeStructureData;
  contact_analysis: ContactAnalysisData;
  skill_analysis: SkillAnalysisData;
  achievement_analysis: AchievementAnalysisData;
  overall_analysis: OverallAnalysis;
  role_analysis?: RoleAnalysis | null;
  job_match_analysis?: JobMatchAnalysis | null;
}

export interface ApiResponse<T = AnalyzeResponseData> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  details?: Record<string, string>;
}
