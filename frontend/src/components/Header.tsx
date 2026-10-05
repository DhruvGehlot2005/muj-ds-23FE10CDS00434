/**
 * @file Header.tsx
 * @description Application top navigation bar and academic banner
 * @module frontend/components/Header
 */

import React from "react";
import { FileCheck } from "lucide-react";

interface HeaderProps {
  isMockMode?: boolean;
}

/**
 * Top navigation header showcasing project identity.
 */
export const Header: React.FC<HeaderProps> = ({ isMockMode = false }) => {
  return (
    <header className="border-b border-slate-200 bg-white/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-brand-500/20">
            <FileCheck className="w-5 h-5" />
          </div>
          <span className="font-bold text-slate-900 tracking-tight text-xl">
            ResLens
          </span>
        </div>

        {isMockMode && (
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse" />
              Demo Mode
            </span>
          </div>
        )}
      </div>
    </header>
  );
};
