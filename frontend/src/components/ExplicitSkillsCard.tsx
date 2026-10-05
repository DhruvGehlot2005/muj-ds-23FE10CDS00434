/**
 * @file ExplicitSkillsCard.tsx
 * @description Section 3: Explicit Skill Extraction and Categorization display
 * @module frontend/components
 */

import React from "react";
import { Wrench, CheckCircle } from "lucide-react";
import { SkillAnalysisData } from "../types";

interface Props {
  data: SkillAnalysisData;
}

export const ExplicitSkillsCard: React.FC<Props> = ({ data }) => {
  const categories = Object.keys(data.categorized_skills || {});

  return (
    <div className="bg-white rounded-2xl p-6 sm:p-8 shadow-sm border border-slate-200 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-4">
        <div>
          <h3 className="text-xl font-bold text-slate-900">Explicit Skills Extracted</h3>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-teal-50 border border-teal-200 text-teal-800 text-xs font-bold">
          <Wrench className="w-3.5 h-3.5 text-teal-600" />
          <span>{data.total_skills_count} Skills Evidenced</span>
        </div>
      </div>

      {categories.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {categories.map((category) => {
            const skills = data.categorized_skills[category];
            if (!skills || skills.length === 0) return null;

            return (
              <div
                key={category}
                className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-2.5"
              >
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wide">
                    {category}
                  </h4>
                  <span className="text-[11px] font-semibold text-slate-500 bg-white px-2 py-0.5 rounded-full border border-slate-200">
                    {skills.length}
                  </span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {skills.map((skill) => (
                    <span
                      key={skill}
                      className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-lg bg-white text-slate-800 border border-slate-200 shadow-2xs hover:border-teal-300 transition-colors"
                    >
                      <CheckCircle className="w-3 h-3 text-teal-500" />
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-6 bg-slate-50 rounded-xl border border-dashed border-slate-200">
          <p className="text-xs text-slate-500">No explicit technical skills matched the standard vocabulary.</p>
        </div>
      )}

      <div className="text-[11px] text-slate-500 bg-slate-50 p-3 rounded-lg border border-slate-200">
        <span className="font-semibold text-slate-700">Audit Rule:</span> Skills are strictly identified from direct textual evidence in the resume with canonical alias resolution (e.g., <code className="text-teal-700 font-mono">JS → JavaScript</code>, <code className="text-teal-700 font-mono">k8s → Kubernetes</code>). The LLM is prohibited from hallucinating skills.
      </div>
    </div>
  );
};
