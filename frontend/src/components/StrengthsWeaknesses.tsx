/**
 * @file StrengthsWeaknesses.tsx
 * @description Cards for Strengths, Areas for Improvement, Missing Sections, and Recommendations
 * @module frontend/components/StrengthsWeaknesses
 */

import React from "react";
import { CheckCircle2, AlertTriangle, Lightbulb, AlertOctagon } from "lucide-react";

interface StrengthsWeaknessesProps {
  strengths: string[];
  weaknesses: string[];
  missingSections: string[];
  recommendations: string[];
}

export const StrengthsWeaknesses: React.FC<StrengthsWeaknessesProps> = ({
  strengths,
  weaknesses,
  missingSections,
  recommendations,
}) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* 1. Strengths */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 space-y-4">
        <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center">
            <CheckCircle2 className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900 tracking-tight">
              Evidence-Based Strengths
            </h3>
            <p className="text-xs text-slate-500">Verified factual accomplishments in resume</p>
          </div>
        </div>

        {strengths.length === 0 ? (
          <p className="text-xs text-slate-400 italic">No clear strengths detected.</p>
        ) : (
          <ul className="space-y-2">
            {strengths.map((item, idx) => (
              <li
                key={idx}
                className="text-xs text-slate-700 bg-emerald-50/40 border border-emerald-100 p-2.5 rounded-xl flex items-start gap-2.5"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 flex-shrink-0" />
                <span className="leading-relaxed">{item}</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* 2. Areas for Improvement */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 space-y-4">
        <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
          <div className="w-8 h-8 rounded-lg bg-amber-100 text-amber-700 flex items-center justify-center">
            <AlertTriangle className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900 tracking-tight">
              Areas for Improvement
            </h3>
            <p className="text-xs text-slate-500">Elements that could be strengthened or expanded</p>
          </div>
        </div>

        {weaknesses.length === 0 ? (
          <p className="text-xs text-slate-400 italic">No critical weaknesses noted.</p>
        ) : (
          <ul className="space-y-2">
            {weaknesses.map((item, idx) => (
              <li
                key={idx}
                className="text-xs text-slate-700 bg-amber-50/40 border border-amber-100 p-2.5 rounded-xl flex items-start gap-2.5"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-1.5 flex-shrink-0" />
                <span className="leading-relaxed">{item}</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* 3. Missing Sections */}
      {missingSections.length > 0 && (
        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
            <div className="w-8 h-8 rounded-lg bg-rose-100 text-rose-700 flex items-center justify-center">
              <AlertOctagon className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900 tracking-tight">
                Missing Sections / Content
              </h3>
              <p className="text-xs text-slate-500">Components expected in competitive resumes</p>
            </div>
          </div>

          <ul className="space-y-2">
            {missingSections.map((item, idx) => (
              <li
                key={idx}
                className="text-xs text-slate-700 bg-rose-50/40 border border-rose-100 p-2.5 rounded-xl flex items-start gap-2.5"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-rose-500 mt-1.5 flex-shrink-0" />
                <span className="leading-relaxed">{item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* 4. Actionable Recommendations */}
      <div className={`bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 space-y-4 ${missingSections.length === 0 ? "md:col-span-2" : ""}`}>
        <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-100 text-indigo-700 flex items-center justify-center">
            <Lightbulb className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900 tracking-tight">
              Actionable Recommendations
            </h3>
            <p className="text-xs text-slate-500">Prioritized enhancements to boost score and callbacks</p>
          </div>
        </div>

        {recommendations.length === 0 ? (
          <p className="text-xs text-slate-400 italic">No recommendations required.</p>
        ) : (
          <ul className="space-y-2">
            {recommendations.map((item, idx) => (
              <li
                key={idx}
                className="text-xs text-slate-700 bg-indigo-50/40 border border-indigo-100 p-2.5 rounded-xl flex items-start gap-2.5"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 mt-1.5 flex-shrink-0" />
                <span className="leading-relaxed">{item}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};
