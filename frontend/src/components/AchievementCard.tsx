/**
 * @file AchievementCard.tsx
 * @description Section 4: Quantified Achievement and Metrics Detection display
 * @module frontend/components
 */

import React from "react";
import { TrendingUp, Award, Percent, DollarSign, Clock, Users } from "lucide-react";
import { AchievementAnalysisData } from "../types";
import { ScoreGauge } from "./ScoreGauge";

interface Props {
  data: AchievementAnalysisData;
}

export const AchievementCard: React.FC<Props> = ({ data }) => {
  const getMetricIcon = (type: string) => {
    switch (type) {
      case "percentage":
        return <Percent className="w-3.5 h-3.5 text-blue-600" />;
      case "monetary":
        return <DollarSign className="w-3.5 h-3.5 text-emerald-600" />;
      case "ranking":
        return <Award className="w-3.5 h-3.5 text-amber-600" />;
      case "time_reduction":
        return <Clock className="w-3.5 h-3.5 text-purple-600" />;
      case "scale_volume":
      case "multiplier_speed":
      default:
        return <Users className="w-3.5 h-3.5 text-indigo-600" />;
    }
  };

  return (
    <div className="bg-white rounded-2xl p-6 sm:p-8 shadow-sm border border-slate-200 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-4">
        <div>
          <h3 className="text-xl font-bold text-slate-900">Quantified Achievement Detection</h3>
        </div>

        <div className="flex items-center gap-4">
          <ScoreGauge score={data.quantification_score} label="Impact Density" size="sm" />
        </div>
      </div>

      {/* Metrics Type Badges */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs font-semibold text-slate-500 mr-1">Detected Metric Categories:</span>
        {data.detected_metric_types && data.detected_metric_types.length > 0 ? (
          data.detected_metric_types.map((type) => (
            <span
              key={type}
              className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-lg bg-blue-50 text-blue-800 border border-blue-200"
            >
              {getMetricIcon(type)}
              {type.replace("_", " ")}
            </span>
          ))
        ) : (
          <span className="text-xs text-slate-400 italic">None detected</span>
        )}
      </div>

      {/* Detected Achievements List */}
      <div className="space-y-2.5">
        <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wide">
          Evidenced Achievement Statements ({data.achievements_count})
        </h4>

        {data.achievements && data.achievements.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {data.achievements.map((item, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/90 space-y-2 flex flex-col justify-between"
              >
                <p className="text-xs text-slate-800 leading-relaxed font-medium">
                  "{item.statement}"
                </p>
                <div className="flex items-center justify-between pt-1 border-t border-slate-200/60 text-[11px]">
                  <span className="inline-flex items-center gap-1 font-mono font-bold text-brand-700 bg-brand-50 px-2 py-0.5 rounded border border-brand-200">
                    <TrendingUp className="w-3 h-3 text-brand-600" />
                    {item.matched_text}
                  </span>
                  <span className="text-slate-500 capitalize">{item.metric_type.replace("_", " ")}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-4 rounded-xl bg-amber-50/60 border border-amber-200 text-xs text-amber-800 space-y-1">
            <p className="font-semibold">No quantitative achievements detected in resume bullet points.</p>
            <p className="text-amber-700 text-[11px]">
              Tip: Strong technical resumes incorporate concrete numbers such as "Reduced latency by 35%" or "Processed 50k+ daily queries".
            </p>
          </div>
        )}
      </div>

      <div className="text-[11px] text-slate-500 bg-slate-50 p-3 rounded-lg border border-slate-200">
        <span className="font-semibold text-slate-700">Academic Note:</span> This component deterministically detects empirical and quantitative phrasing patterns. It does not independently verify the veracity of stated numbers.
      </div>
    </div>
  );
};
