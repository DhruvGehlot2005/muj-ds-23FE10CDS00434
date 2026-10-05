/**
 * @file TechnicalPipelineCard.tsx
 * @description Section 7: Technical Pipeline and Hybrid NLP Architecture demonstration display
 * @module frontend/components
 */

import React from "react";
import { Cpu, Database, Binary, Sparkles, ShieldCheck } from "lucide-react";

export const TechnicalPipelineCard: React.FC = () => {
  return (
    <div className="bg-slate-900 text-white rounded-2xl p-6 sm:p-8 shadow-md border border-slate-800 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider rounded bg-brand-500/20 text-brand-400 border border-brand-500/30">
              Section 7 • Academic Architecture
            </span>
          </div>
          <h3 className="text-xl font-bold text-white mt-1">Hybrid NLP + LLM Execution Pipeline</h3>
          <p className="text-xs text-slate-400">
            Visible separation of custom deterministic/statistical NLP from semantic LLM reasoning.
          </p>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-800 border border-slate-700 text-xs text-slate-300">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>Zero LLM Hallucination for Deterministic Facts</span>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Module 1: ML Section Classifier */}
        <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/80 space-y-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
            <Cpu className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wide">
              Resume Section Classifier
            </h4>
            <div className="text-xs font-semibold text-indigo-400 mt-0.5">
              TF-IDF + Logistic Regression
            </div>
          </div>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            Supervised scikit-learn pipeline trained on 405 academic synthetic samples across 9 classes with confidence thresholding (0.60).
          </p>
        </div>

        {/* Module 2: Skill & Contact Extractor */}
        <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/80 space-y-3">
          <div className="w-8 h-8 rounded-lg bg-teal-500/20 border border-teal-500/30 flex items-center justify-center text-teal-400">
            <Database className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wide">
              Skill & Contact Extraction
            </h4>
            <div className="text-xs font-semibold text-teal-400 mt-0.5">
              Dictionary + Normalization
            </div>
          </div>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            Curated 8-category vocabulary with alias normalization (JS → JavaScript) and RFC-compliant regex for verifiable contact info.
          </p>
        </div>

        {/* Module 3: Lexical Similarity */}
        <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/80 space-y-3">
          <div className="w-8 h-8 rounded-lg bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-400">
            <Binary className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wide">
              Lexical Similarity Engine
            </h4>
            <div className="text-xs font-semibold text-amber-400 mt-0.5">
              TF-IDF + Cosine Similarity
            </div>
          </div>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            Statistical n-gram frequency matrix computation comparing raw vocabulary overlap between resume and JD independently of LLM.
          </p>
        </div>

        {/* Module 4: Gemini LLM */}
        <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/80 space-y-3">
          <div className="w-8 h-8 rounded-lg bg-brand-500/20 border border-brand-500/30 flex items-center justify-center text-brand-400">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wide">
              Semantic Reasoning
            </h4>
            <div className="text-xs font-semibold text-brand-400 mt-0.5">
              Google Gemini API
            </div>
          </div>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            Receives structured evidence JSON (not unparsed text) to generate nuanced role compatibility, qualitative insights, and advice.
          </p>
        </div>
      </div>
    </div>
  );
};
