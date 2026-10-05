/**
 * @file ScoreGauge.tsx
 * @description Accessible circular SVG gauge visualizer for percentage scores
 * @module frontend/components/ScoreGauge
 */

import React from "react";

interface ScoreGaugeProps {
  score: number;
  label: string;
  size?: "sm" | "md" | "lg";
  subtext?: string;
}

export const ScoreGauge: React.FC<ScoreGaugeProps> = ({
  score,
  label,
  size = "md",
  subtext,
}) => {
  const boundedScore = Math.max(0, Math.min(100, Math.round(score)));

  // SVG Geometry
  const dimensions = {
    sm: { size: 90, stroke: 8, fontSize: "text-lg", labelSize: "text-xs" },
    md: { size: 130, stroke: 10, fontSize: "text-2xl", labelSize: "text-xs" },
    lg: { size: 170, stroke: 14, fontSize: "text-4xl", labelSize: "text-sm" },
  }[size];

  const radius = (dimensions.size - dimensions.stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (boundedScore / 100) * circumference;

  // Semantic color selection
  let strokeColor = "stroke-emerald-500";
  let textColor = "text-emerald-700";
  let bgColor = "bg-emerald-50";

  if (boundedScore < 60) {
    strokeColor = "stroke-rose-500";
    textColor = "text-rose-700";
    bgColor = "bg-rose-50";
  } else if (boundedScore < 80) {
    strokeColor = "stroke-amber-500";
    textColor = "text-amber-700";
    bgColor = "bg-amber-50";
  }

  return (
    <div className="flex flex-col items-center justify-center p-2 text-center">
      <div className="relative inline-flex items-center justify-center">
        <svg
          width={dimensions.size}
          height={dimensions.size}
          className="transform -rotate-90"
        >
          {/* Background Track */}
          <circle
            cx={dimensions.size / 2}
            cy={dimensions.size / 2}
            r={radius}
            className="stroke-slate-100"
            strokeWidth={dimensions.stroke}
            fill="transparent"
          />
          {/* Progress Arc */}
          <circle
            cx={dimensions.size / 2}
            cy={dimensions.size / 2}
            r={radius}
            className={`${strokeColor} transition-all duration-1000 ease-out`}
            strokeWidth={dimensions.stroke}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
          />
        </svg>

        {/* Center Text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`font-bold tracking-tight ${dimensions.fontSize} ${textColor}`}>
            {boundedScore}
          </span>
          <span className="text-[10px] text-slate-400 font-medium">/ 100</span>
        </div>
      </div>

      <span className={`mt-2 font-semibold text-slate-800 ${dimensions.labelSize}`}>
        {label}
      </span>
      {subtext && <span className="text-[11px] text-slate-500 mt-0.5">{subtext}</span>}
    </div>
  );
};
