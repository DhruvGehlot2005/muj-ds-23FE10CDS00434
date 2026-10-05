/**
 * @file App.tsx
 * @description Main application component integrating upload, hybrid NLP analysis, and 7-section results dashboard.
 * @module frontend/App
 */

import React, { useEffect, useState } from "react";
import { Header } from "./components/Header";
import { UploadZone } from "./components/UploadZone";
import { OverallScoreCard } from "./components/OverallScoreCard";
import { ResumeStructureCard } from "./components/ResumeStructureCard";
import { ExplicitSkillsCard } from "./components/ExplicitSkillsCard";
import { AchievementCard } from "./components/AchievementCard";
import { RoleCompatibilityCard } from "./components/RoleCompatibilityCard";
import { JobMatchCard } from "./components/JobMatchCard";
import { StrengthsWeaknesses } from "./components/StrengthsWeaknesses";
import { analyzeResume, checkHealth } from "./services/api";
import { AnalyzeResponseData } from "./types";
import { AlertCircle, RotateCcw } from "lucide-react";

export const App: React.FC = () => {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [analysisData, setAnalysisData] = useState<AnalyzeResponseData | null>(null);
  const [isMockMode, setIsMockMode] = useState<boolean>(false);

  useEffect(() => {
    checkHealth()
      .then((res) => setIsMockMode(res.llm_mock_mode))
      .catch(() => setIsMockMode(false));
  }, []);

  const handleAnalyze = async (params: {
    resumeFile: File;
    targetRole?: string;
    jdFile?: File | null;
    jdText?: string;
  }) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await analyzeResume(
        params.resumeFile,
        params.targetRole,
        params.jdFile,
        params.jdText
      );
      setAnalysisData(data);
      // Smooth scroll down to results
      setTimeout(() => {
        const resultsEl = document.getElementById("analysis-results");
        if (resultsEl) {
          resultsEl.scrollIntoView({ behavior: "smooth" });
        }
      }, 100);
    } catch (err: any) {
      setError(err.message || "Failed to analyze resume. Please check the backend server.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setAnalysisData(null);
    setError(null);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 font-sans selection:bg-brand-500 selection:text-white">
      <Header isMockMode={isMockMode} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10 space-y-10">
        {/* Hero Section */}
        <section className="text-center max-w-3xl mx-auto space-y-3">
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-slate-950 tracking-tight">
            Bridge the gap between your resume and your dream job.
          </h1>
        </section>

        {/* Global Error Banner */}
        {error && (
          <div className="max-w-4xl mx-auto p-4 bg-rose-50 border border-rose-200 rounded-2xl text-rose-800 flex items-start justify-between gap-3 shadow-sm">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-bold">Analysis Failed</h4>
                <p className="text-xs mt-0.5 text-rose-700 leading-relaxed">{error}</p>
              </div>
            </div>
            <button
              onClick={() => setError(null)}
              className="text-rose-500 hover:text-rose-800 text-xs font-semibold px-2 py-1 rounded-lg hover:bg-rose-100 transition-colors"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Form Upload Input */}
        <section className="max-w-4xl mx-auto">
          <UploadZone isLoading={isLoading} onAnalyze={handleAnalyze} />
        </section>

        {/* 7-Section Results Dashboard */}
        {analysisData && (
          <section id="analysis-results" className="space-y-8 pt-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-4">
              <div>
                <h2 className="text-2xl font-bold text-slate-950 tracking-tight">
                  Hybrid NLP Analysis & Evaluation Report
                </h2>
                <p className="text-xs sm:text-sm text-slate-500 mt-1">
                  Custom NLP feature extraction combined with structured evidence-based LLM inference.
                </p>
              </div>
              <button
                onClick={handleReset}
                className="inline-flex items-center gap-1.5 px-4 py-2 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-semibold rounded-xl shadow-sm transition-colors"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                Analyze Another Resume
              </button>
            </div>

            {/* SECTION 1: OVERALL RESUME ANALYSIS */}
            <div className="space-y-6">
              <OverallScoreCard data={analysisData.overall_analysis} />
              <StrengthsWeaknesses
                strengths={analysisData.overall_analysis.strengths}
                weaknesses={analysisData.overall_analysis.weaknesses}
                missingSections={analysisData.resume_structure?.missing_sections || []}
                recommendations={analysisData.overall_analysis.recommendations}
              />
            </div>

            {/* SECTION 2: RESUME STRUCTURE */}
            {analysisData.resume_structure && (
              <ResumeStructureCard data={analysisData.resume_structure} />
            )}

            {/* SECTION 3: EXPLICIT SKILLS */}
            {analysisData.skill_analysis && (
              <ExplicitSkillsCard data={analysisData.skill_analysis} />
            )}

            {/* SECTION 4: ACHIEVEMENT ANALYSIS */}
            {analysisData.achievement_analysis && (
              <AchievementCard data={analysisData.achievement_analysis} />
            )}

            {/* SECTION 5: TARGET ROLE (Conditional) */}
            {analysisData.role_analysis && (
              <RoleCompatibilityCard data={analysisData.role_analysis} />
            )}

            {/* SECTION 6: JOB DESCRIPTION MATCH (Conditional) */}
            {analysisData.job_match_analysis && (
              <JobMatchCard data={analysisData.job_match_analysis} />
            )}
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-4 mt-12 text-center text-xs text-slate-500">
      </footer>
    </div>
  );
};
