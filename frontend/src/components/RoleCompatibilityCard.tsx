/**
 * @file RoleCompatibilityCard.tsx
 * @description Section 5: Target Role Compatibility Card
 * @module frontend/components/RoleCompatibilityCard
 */

import React from "react";
import { Briefcase, CheckCircle, AlertTriangle, XCircle, Lightbulb } from "lucide-react";
import { RoleAnalysis } from "../types";
import { ScoreGauge } from "./ScoreGauge";

interface RoleCompatibilityCardProps {
  data: RoleAnalysis;
}

export const RoleCompatibilityCard: React.FC<RoleCompatibilityCardProps> = ({ data }) => {
  const score = data.role_compatibility_score ?? data.role_match_score ?? 75;
  const strengths = data.strengths || data.matching_areas || [];
  const weaknesses = data.weaknesses || data.weak_areas || [];
  const gaps = data.gaps || data.missing_areas || [];

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 sm:p-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-100 pb-4 gap-2">
        <div>
          <div className="flex items-center gap-2">
            <Briefcase className="w-5 h-5 text-indigo-600" />
            <h2 className="text-xl font-bold text-slate-900 tracking-tight">
              Target Role Compatibility
            </h2>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Evaluated against industry expectations for:{" "}
            <span className="font-semibold text-indigo-700">{data.target_role}</span>
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 items-center">
        {/* Score column */}
        <div className="md:col-span-1 flex flex-col items-center justify-center p-4 bg-slate-50 rounded-2xl border border-slate-100">
          <ScoreGauge score={score} label="Role Alignment" size="md" />
        </div>

        {/* Alignment summary lists */}
        <div className="md:col-span-3 space-y-4">
          {/* Matching Areas */}
          {strengths.length > 0 && (
            <div>
              <h4 className="text-xs font-bold text-emerald-800 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
                Demonstrated Strengths for this Role
              </h4>
              <ul className="space-y-1.5">
                {strengths.map((item, idx) => (
                  <li
                    key={idx}
                    className="text-xs text-slate-700 flex items-start gap-2 bg-emerald-50/50 p-2 rounded-lg border border-emerald-100/60"
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 flex-shrink-0" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Weak Areas */}
          {weaknesses.length > 0 && (
            <div>
              <h4 className="text-xs font-bold text-amber-800 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                Areas Needing Additional Depth
              </h4>
              <ul className="space-y-1.5">
                {weaknesses.map((item, idx) => (
                  <li
                    key={idx}
                    className="text-xs text-slate-700 flex items-start gap-2 bg-amber-50/50 p-2 rounded-lg border border-amber-100/60"
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-1.5 flex-shrink-0" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Missing Gaps */}
          {gaps.length > 0 && (
            <div>
              <h4 className="text-xs font-bold text-rose-800 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <XCircle className="w-3.5 h-3.5 text-rose-600" />
                Commonly Expected Capabilities Missing
              </h4>
              <ul className="space-y-1.5">
                {gaps.map((item, idx) => (
                  <li
                    key={idx}
                    className="text-xs text-slate-700 flex items-start gap-2 bg-rose-50/50 p-2 rounded-lg border border-rose-100/60"
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-rose-500 mt-1.5 flex-shrink-0" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Role Recommendations */}
      {data.recommendations && data.recommendations.length > 0 && (
        <div className="pt-4 border-t border-slate-100">
          <h4 className="text-xs font-bold text-indigo-900 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <Lightbulb className="w-3.5 h-3.5 text-indigo-600" />
            Target Role Recommendations
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {data.recommendations.map((rec, idx) => (
              <div
                key={idx}
                className="p-3 bg-indigo-50/40 rounded-xl border border-indigo-100/80 text-xs text-slate-800 leading-relaxed"
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
