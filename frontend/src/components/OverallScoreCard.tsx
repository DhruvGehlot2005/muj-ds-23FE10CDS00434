/**
 * @file OverallScoreCard.tsx
 * @description Section 1: Overall Resume Qualitative Evaluation Card
 * @module frontend/components/OverallScoreCard
 */

import React from "react";
import { ShieldCheck, Sparkles } from "lucide-react";
import { OverallAnalysis } from "../types";
import { ScoreGauge } from "./ScoreGauge";

interface OverallScoreCardProps {
  data: OverallAnalysis;
}

export const OverallScoreCard: React.FC<OverallScoreCardProps> = ({ data }) => {
  const overallScore = data.overall_quality_score ?? data.overall_score ?? 80;
  const atsScore = data.ats_compatibility_score ?? data.ats_score ?? 80;

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 sm:p-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-100 pb-4 gap-2">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-brand-600" />
            Overall Resume Quality & ATS Readiness
          </h2>
        </div>
      </div>

      {/* Main Score & Sub-scores */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6 items-center">
        {/* Primary Overall Score Gauge */}
        <div className="md:col-span-2 flex flex-col items-center justify-center p-6 bg-slate-50/60 rounded-2xl border border-slate-100">
          <ScoreGauge score={overallScore} label="Qualitative Score" size="lg" />
          <p className="text-xs text-slate-500 text-center mt-3 max-w-xs">
            Synthesized evaluation based on content depth, articulation, ATS structure, and professionalism.
          </p>
        </div>

        {/* 3 Dimension Breakdown Gauges */}
        <div className="md:col-span-3 grid grid-cols-3 gap-3">
          <div className="p-4 bg-slate-50/60 rounded-xl border border-slate-100 flex flex-col items-center">
            <ScoreGauge score={data.clarity_score} label="Clarity" size="sm" />
          </div>
          <div className="p-4 bg-slate-50/60 rounded-xl border border-slate-100 flex flex-col items-center">
            <ScoreGauge score={data.professionalism_score} label="Professionalism" size="sm" />
          </div>
          <div className="p-4 bg-slate-50/60 rounded-xl border border-slate-100 flex flex-col items-center">
            <ScoreGauge score={atsScore} label="ATS Readiness" size="sm" />
          </div>
        </div>
      </div>

      {/* Strengths & Weaknesses quick preview */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
        <div className="p-4 bg-emerald-50/60 rounded-xl border border-emerald-200/80 space-y-2">
          <h4 className="text-xs font-bold text-emerald-900 uppercase tracking-wide flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
            Key Qualitative Strengths
          </h4>
          <ul className="space-y-1.5">
            {data.strengths && data.strengths.slice(0, 3).map((s, idx) => (
              <li key={idx} className="text-xs text-slate-700 flex items-start gap-1.5">
                <span className="text-emerald-500 font-bold">•</span>
                <span>{s}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="p-4 bg-amber-50/60 rounded-xl border border-amber-200/80 space-y-2">
          <h4 className="text-xs font-bold text-amber-900 uppercase tracking-wide flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-amber-500" />
            Areas For Improvement
          </h4>
          <ul className="space-y-1.5">
            {data.weaknesses && data.weaknesses.slice(0, 3).map((w, idx) => (
              <li key={idx} className="text-xs text-slate-700 flex items-start gap-1.5">
                <span className="text-amber-500 font-bold">•</span>
                <span>{w}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};
