/**
 * @file ResumeStructureCard.tsx
 * @description Section 2: Resume Structure and Supervised Section Classification display
 * @module frontend/components
 */

import React, { useState } from "react";
import { CheckCircle2, XCircle, AlertTriangle, Cpu, ChevronDown, ChevronUp } from "lucide-react";
import { ScoreGauge } from "./ScoreGauge";
import { ResumeStructureData } from "../types";

interface Props {
  data: ResumeStructureData;
}

export const ResumeStructureCard: React.FC<Props> = ({ data }) => {
  const [showBlocks, setShowBlocks] = useState(false);

  return (
    <div className="bg-white rounded-2xl p-6 sm:p-8 shadow-sm border border-slate-200 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-4">
        <div>
          <h3 className="text-xl font-bold text-slate-900">Resume Structural Completeness</h3>
        </div>

        <div className="flex items-center gap-3">
          <ScoreGauge score={data.completeness_score} label="Structural Score" size="sm" />
        </div>
      </div>

      {/* Grid of Present, Missing, and Optional Sections */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Present Sections */}
        <div className="p-4 rounded-xl bg-emerald-50/60 border border-emerald-200/80 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-emerald-900 uppercase tracking-wide flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              Present Sections ({data.present_sections.length})
            </span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {data.present_sections.length > 0 ? (
              data.present_sections.map((sec) => (
                <span
                  key={sec}
                  className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-emerald-100 text-emerald-800 border border-emerald-300/60"
                >
                  {sec}
                </span>
              ))
            ) : (
              <span className="text-xs text-emerald-700 italic">No standard sections detected</span>
            )}
          </div>
        </div>

        {/* Missing Core Sections */}
        <div className="p-4 rounded-xl bg-rose-50/60 border border-rose-200/80 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-rose-900 uppercase tracking-wide flex items-center gap-1.5">
              <XCircle className="w-4 h-4 text-rose-600" />
              Missing Core Sections ({data.missing_sections.length})
            </span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {data.missing_sections.length > 0 ? (
              data.missing_sections.map((sec) => (
                <span
                  key={sec}
                  className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-rose-100 text-rose-800 border border-rose-300/60"
                >
                  {sec}
                </span>
              ))
            ) : (
              <span className="text-xs text-rose-700 italic">All core sections present!</span>
            )}
          </div>
        </div>

        {/* Optional Missing Sections */}
        <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-700 uppercase tracking-wide flex items-center gap-1.5">
              <AlertTriangle className="w-4 h-4 text-amber-500" />
              Optional Sections ({data.optional_missing_sections.length})
            </span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {data.optional_missing_sections.length > 0 ? (
              data.optional_missing_sections.map((sec) => (
                <span
                  key={sec}
                  className="px-2.5 py-1 text-xs font-medium rounded-lg bg-slate-200/70 text-slate-700 border border-slate-300/60"
                >
                  {sec}
                </span>
              ))
            ) : (
              <span className="text-xs text-slate-500 italic">All optional sections found</span>
            )}
          </div>
        </div>
      </div>

      {/* Supervised ML Classified Blocks Accordion */}
      {data.classified_blocks && data.classified_blocks.length > 0 && (
        <div className="pt-2">
          <button
            type="button"
            onClick={() => setShowBlocks(!showBlocks)}
            className="w-full flex items-center justify-between p-3 rounded-xl bg-slate-50 hover:bg-slate-100 border border-slate-200 text-xs font-semibold text-slate-700 transition-colors"
          >
            <div className="flex items-center gap-2">
              <Cpu className="w-4 h-4 text-brand-600" />
              <span>Inspect ML Classified Blocks ({data.classified_blocks.length} blocks analyzed)</span>
            </div>
            {showBlocks ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>

          {showBlocks && (
            <div className="mt-3 space-y-2 max-h-80 overflow-y-auto pr-1">
              {data.classified_blocks.map((block, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-lg bg-slate-50/80 border border-slate-200 text-xs space-y-1.5"
                >
                  <div className="flex items-center justify-between">
                    <span className="px-2 py-0.5 font-mono text-[11px] font-bold rounded bg-brand-100 text-brand-800">
                      {block.label}
                    </span>
                    <span className="text-[11px] text-slate-500 font-mono">
                      Confidence: {(block.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                  <p className="text-slate-700 font-mono text-[11px] line-clamp-2 bg-white p-2 rounded border border-slate-100">
                    {block.text}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
