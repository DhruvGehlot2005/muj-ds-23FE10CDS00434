/**
 * @file api.ts
 * @description Frontend API service for dispatching resume analysis requests
 * @module frontend/services/api
 */

import { AnalyzeResponseData, ApiResponse } from "../types";

// Use relative path in browser to leverage same-origin proxy, fallback to port 8000 for SSR/tests
const API_BASE_URL = typeof window !== "undefined" ? "" : "http://127.0.0.1:8000";

/**
 * Validates file size and MIME type before transmission.
 *
 * @param file Uploaded file instance
 * @throws Error if file violates size or type constraints
 */
export function validateUploadFile(file: File): void {
  const maxSizeBytes = 10 * 1024 * 1024; // 10MB
  if (file.size > maxSizeBytes) {
    throw new Error(`File size (${(file.size / (1024 * 1024)).toFixed(1)}MB) exceeds 10MB limit.`);
  }

  const name = file.name.toLowerCase();
  if (!name.endsWith(".pdf") && !name.endsWith(".docx")) {
    throw new Error("Only PDF and DOCX files are supported.");
  }
}

/**
 * Submits the resume and optional criteria to the backend analyzer endpoint.
 *
 * @param resumeFile Resume file (PDF or DOCX)
 * @param targetRole Optional target role string
 * @param jdFile Optional Job Description file
 * @param jdText Optional Job Description text
 * @returns Parsed AnalyzeResponseData
 */
export async function analyzeResume(
  resumeFile: File,
  targetRole?: string,
  jdFile?: File | null,
  jdText?: string
): Promise<AnalyzeResponseData> {
  validateUploadFile(resumeFile);

  const formData = new FormData();
  formData.append("resume", resumeFile);

  if (targetRole && targetRole.trim()) {
    formData.append("target_role", targetRole.trim());
  }

  if (jdFile) {
    validateUploadFile(jdFile);
    formData.append("jd_file", jdFile);
  }

  if (jdText && jdText.trim()) {
    formData.append("jd_text", jdText.trim());
  }

  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: "POST",
    body: formData,
  });

  const json: ApiResponse<AnalyzeResponseData> = await response.json();

  if (!response.ok || !json.success || !json.data) {
    const errorMsg = json.message || json.error || `Analysis failed with HTTP ${response.status}`;
    throw new Error(errorMsg);
  }

  return json.data;
}

/**
 * Fetches system health and LLM mode status.
 */
export async function checkHealth(): Promise<{ status: string; llm_mock_mode: boolean }> {
  const response = await fetch(`${API_BASE_URL}/api/health`);
  if (!response.ok) {
    throw new Error("Backend server is unreachable");
  }
  return response.json();
}
