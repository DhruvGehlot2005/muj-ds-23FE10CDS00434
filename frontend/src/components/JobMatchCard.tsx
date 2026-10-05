/**
 * @file JobMatchCard.tsx
 * @description Section 6: Comparative Job Description Match showing Lexical vs Semantic similarity and skill overlap
 * @module frontend/components/JobMatchCard
 */

import React from "react";
import {
  FileCheck2,
  CheckCircle,
  AlertCircle,
  XCircle,
  Sparkles,
  Binary,
  BrainCircuit,
} from "lucide-react";
import { JobMatchAnalysis } from "../types";
import { ScoreGauge } from "./ScoreGauge";

interface JobMatchCardProps {
  data: JobMatchAnalysis;
}

export const JobMatchCard: React.FC<JobMatchCardProps> = ({ data }) => {
  const semanticScore = data.semantic_match_score ?? data.match_score ?? 70;
  const lexicalScore = Math.round(data.lexical_similarity_score ?? 0);

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 sm:p-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-100 pb-4 gap-2">
        <div>
          <div className="flex items-center gap-2">
            <FileCheck2 className="w-5 h-5 text-purple-600" />
            <h2 className="text-xl font-bold text-slate-900 tracking-tight">
              Job Description Compatibility Assessment
            </h2>
          </div>
        </div>
      </div>

      {/* Dual Gauges: Lexical vs Semantic */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Lexical Similarity Gauge */}
        <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 flex items-center justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-1.5 text-xs font-bold text-amber-700 uppercase tracking-wide">
              <Binary className="w-4 h-4 text-amber-600" />
              Lexical Similarity
            </div>
            <p className="text-[11px] text-slate-500 leading-tight">
              TF-IDF + Cosine Similarity (Word & N-Gram Overlap)
            </p>
          </div>
          <ScoreGauge score={lexicalScore} label="TF-IDF Match" size="sm" />
        </div>

        {/* Semantic Match Gauge */}
        <div className="p-4 bg-purple-50/50 rounded-2xl border border-purple-200 flex items-center justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-1.5 text-xs font-bold text-purple-800 uppercase tracking-wide">
              <BrainCircuit className="w-4 h-4 text-purple-600" />
              Semantic Match
            </div>
            <p className="text-[11px] text-slate-500 leading-tight">
              Gemini LLM Contextual Qualification Reasoning
            </p>
          </div>
          <ScoreGauge score={semanticScore} label="Semantic Fit" size="sm" />
        </div>
      </div>

      {/* Skills Gap Analysis Badges */}
      <div className="space-y-4 pt-2">
        {/* Matching Skills */}
        {data.matching_skills && data.matching_skills.length > 0 && (
          <div>
            <h4 className="text-xs font-bold text-emerald-800 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
              Matching Skills ({data.matching_skills.length}) • Deterministic Overlap
            </h4>
            <div className="flex flex-wrap gap-2">
              {data.matching_skills.map((skill, idx) => (
                <span
                  key={idx}
                  className="bg-emerald-50 text-emerald-800 border border-emerald-200 px-3 py-1 rounded-lg text-xs font-semibold"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Missing Skills */}
        {data.missing_skills && data.missing_skills.length > 0 && (
          <div>
            <h4 className="text-xs font-bold text-rose-800 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <XCircle className="w-3.5 h-3.5 text-rose-600" />
              Missing JD Skills ({data.missing_skills.length}) • Deterministic Vocabulary Gap
            </h4>
            <div className="flex flex-wrap gap-2">
              {data.missing_skills.map((skill, idx) => (
                <span
                  key={idx}
                  className="bg-rose-50 text-rose-800 border border-rose-200 px-3 py-1 rounded-lg text-xs font-medium"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Partial Matches (Semantic) */}
        {data.partial_matches && data.partial_matches.length > 0 && (
          <div>
            <h4 className="text-xs font-bold text-amber-800 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
              Partial / Indirect Matches ({data.partial_matches.length})
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
              {data.partial_matches.map((item, idx) => {
                const isObj = typeof item === "object" && item !== null;
                const req = isObj ? (item as any).requirement : item;
                const ev = isObj ? (item as any).evidence : "";
                const gap = isObj ? (item as any).gap : "";

                return (
                  <div
                    key={idx}
                    className="p-3 bg-amber-50/60 rounded-xl border border-amber-200/80 text-xs space-y-1"
                  >
                    <div className="font-semibold text-amber-900">{req}</div>
                    {ev && <div className="text-[11px] text-slate-700">Evidence: {ev}</div>}
                    {gap && <div className="text-[11px] text-amber-800 font-medium">Gap: {gap}</div>}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Recommendations */}
      {data.recommendations && data.recommendations.length > 0 && (
        <div className="pt-4 border-t border-slate-100">
          <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-purple-600" />
            Job-Specific Optimization Recommendations
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {data.recommendations.map((rec, idx) => (
              <div
                key={idx}
                className="p-3 bg-purple-50/40 rounded-xl border border-purple-100 text-xs text-slate-800 leading-relaxed"
              >
                {rec}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
