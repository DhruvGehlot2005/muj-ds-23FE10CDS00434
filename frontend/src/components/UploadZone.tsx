/**
 * @file UploadZone.tsx
 * @description Input and file upload form with native drag-and-drop support for Resume and Job Description
 * @module frontend/components/UploadZone
 */

import React, { useRef, useState } from "react";
import {
  Upload,
  FileText,
  Briefcase,
  X,
  FileCode,
  Search,
  Sparkles,
  AlertCircle,
} from "lucide-react";

interface UploadZoneProps {
  isLoading: boolean;
  onAnalyze: (params: {
    resumeFile: File;
    targetRole?: string;
    jdFile?: File | null;
    jdText?: string;
  }) => void;
}

export const UploadZone: React.FC<UploadZoneProps> = ({ isLoading, onAnalyze }) => {
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [targetRole, setTargetRole] = useState<string>("");
  const [jdMode, setJdMode] = useState<"paste" | "upload">("paste");
  const [jdFile, setJdFile] = useState<File | null>(null);
  const [jdText, setJdText] = useState<string>("");
  const [validationError, setValidationError] = useState<string | null>(null);

  // Drag-and-drop visual states
  const [isDraggingResume, setIsDraggingResume] = useState<boolean>(false);
  const [isDraggingJd, setIsDraggingJd] = useState<boolean>(false);

  const resumeInputRef = useRef<HTMLInputElement>(null);
  const jdFileInputRef = useRef<HTMLInputElement>(null);

  const validateAndProcessFile = (file: File, type: "resume" | "jd"): boolean => {
    setValidationError(null);
    const name = file.name.toLowerCase();
    if (!name.endsWith(".pdf") && !name.endsWith(".docx")) {
      setValidationError(
        `Invalid file type for ${type === "resume" ? "resume" : "Job Description"}. Only PDF and DOCX documents are supported.`
      );
      return false;
    }
    if (file.size > 10 * 1024 * 1024) {
      setValidationError("File exceeds maximum allowed size of 10MB.");
      return false;
    }

    if (type === "resume") {
      setResumeFile(file);
    } else {
      setJdFile(file);
    }
    return true;
  };

  const handleResumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndProcessFile(e.target.files[0], "resume");
    }
  };

  const handleJdFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndProcessFile(e.target.files[0], "jd");
    }
  };

  // Resume Drag & Drop Handlers
  const handleResumeDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (!isDraggingResume) setIsDraggingResume(true);
  };

  const handleResumeDragEnter = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDraggingResume(true);
  };

  const handleResumeDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDraggingResume(false);
  };

  const handleResumeDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDraggingResume(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndProcessFile(e.dataTransfer.files[0], "resume");
    }
  };

  // JD Drag & Drop Handlers
  const handleJdDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (!isDraggingJd) setIsDraggingJd(true);
  };

  const handleJdDragEnter = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDraggingJd(true);
  };

  const handleJdDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDraggingJd(false);
  };

  const handleJdDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDraggingJd(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndProcessFile(e.dataTransfer.files[0], "jd");
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!resumeFile) {
      setValidationError("Please upload or drag & drop a resume file (PDF or DOCX) to proceed.");
      return;
    }
    setValidationError(null);
    onAnalyze({
      resumeFile,
      targetRole: targetRole.trim() || undefined,
      jdFile: jdMode === "upload" ? jdFile : null,
      jdText: jdMode === "paste" ? jdText.trim() : undefined,
    });
  };

  const handleClearResume = () => {
    setResumeFile(null);
    if (resumeInputRef.current) resumeInputRef.current.value = "";
  };

  const handleClearJdFile = () => {
    setJdFile(null);
    if (jdFileInputRef.current) jdFileInputRef.current.value = "";
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 sm:p-8 space-y-6"
    >
      <div className="border-b border-slate-100 pb-4">
        <h2 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <FileText className="w-5 h-5 text-brand-600" />
          Candidate Input & Assessment Scope
        </h2>
      </div>

      {validationError && (
        <div className="p-3.5 bg-rose-50 border border-rose-200 rounded-xl text-rose-700 text-sm flex items-center gap-2.5">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{validationError}</span>
        </div>
      )}

      {/* 1. Resume Upload (Required with Drag & Drop) */}
      <div className="space-y-2">
        <label className="block text-sm font-semibold text-slate-800">
          Resume Document
        </label>

        {!resumeFile ? (
          <div
            onClick={() => resumeInputRef.current?.click()}
            onDragOver={handleResumeDragOver}
            onDragEnter={handleResumeDragEnter}
            onDragLeave={handleResumeDragLeave}
            onDrop={handleResumeDrop}
            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all group ${
              isDraggingResume
                ? "border-brand-600 bg-brand-50/60 ring-4 ring-brand-500/20 scale-[1.01]"
                : "border-slate-300 hover:border-brand-500 hover:bg-brand-50/20"
            }`}
          >
            <input
              type="file"
              ref={resumeInputRef}
              onChange={handleResumeChange}
              accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              className="hidden"
            />
            <div
              className={`w-12 h-12 mx-auto mb-3 rounded-full flex items-center justify-center transition-colors ${
                isDraggingResume
                  ? "bg-brand-600 text-white animate-bounce"
                  : "bg-slate-100 group-hover:bg-brand-100 text-slate-500 group-hover:text-brand-600"
              }`}
            >
              <Upload className="w-6 h-6" />
            </div>
            <p
              className={`text-sm font-medium transition-colors ${
                isDraggingResume ? "text-brand-700 font-semibold" : "text-slate-700 group-hover:text-brand-700"
              }`}
            >
              {isDraggingResume
                ? "Drop your resume file here!"
                : "Click to select or drag and drop your resume"}
            </p>
            <p className="text-xs text-slate-400 mt-1">PDF or DOCX (up to 10MB)</p>
          </div>
        ) : (
          <div className="flex items-center justify-between p-4 bg-slate-50 border border-slate-200 rounded-xl">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-brand-100 text-brand-700 flex items-center justify-center">
                <FileCode className="w-5 h-5" />
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-800">{resumeFile.name}</p>
                <p className="text-xs text-slate-500">
                  {(resumeFile.size / 1024).toFixed(1)} KB • Ready for extraction
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={handleClearResume}
              className="text-slate-400 hover:text-rose-600 p-1.5 rounded-lg hover:bg-rose-50 transition-colors"
              title="Remove file"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
        {/* 2. Target Role (Optional) */}
        <div className="space-y-2">
          <label className="block text-sm font-semibold text-slate-800">
            Target Role
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
              <Briefcase className="w-4 h-4" />
            </div>
            <input
              type="text"
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              placeholder="e.g. Software Engineer"
              className="w-full pl-10 pr-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm placeholder:text-slate-400/70 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-colors"
            />
          </div>
        </div>

        {/* 3. Job Description (Optional) */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="block text-sm font-semibold text-slate-800">
              Job Description
            </label>
            <div className="flex items-center bg-slate-100 p-0.5 rounded-lg text-xs">
              <button
                type="button"
                onClick={() => setJdMode("paste")}
                className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                  jdMode === "paste"
                    ? "bg-white text-slate-800 shadow-sm"
                    : "text-slate-500 hover:text-slate-700"
                }`}
              >
                Paste Text
              </button>
              <button
                type="button"
                onClick={() => setJdMode("upload")}
                className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                  jdMode === "upload"
                    ? "bg-white text-slate-800 shadow-sm"
                    : "text-slate-500 hover:text-slate-700"
                }`}
              >
                Upload File
              </button>
            </div>
          </div>

          {jdMode === "paste" ? (
            <textarea
              rows={3}
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
              placeholder="Paste job description..."
              className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl text-sm placeholder:text-slate-400/70 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-colors resize-none"
            />
          ) : (
            <div>
              {!jdFile ? (
                <div
                  onClick={() => jdFileInputRef.current?.click()}
                  onDragOver={handleJdDragOver}
                  onDragEnter={handleJdDragEnter}
                  onDragLeave={handleJdDragLeave}
                  onDrop={handleJdDrop}
                  className={`border border-dashed rounded-xl p-4 text-center cursor-pointer transition-all ${
                    isDraggingJd
                      ? "border-brand-600 bg-brand-50/60 ring-2 ring-brand-500/20"
                      : "border-slate-300 hover:border-brand-500 bg-slate-50/50 hover:bg-brand-50/20"
                  }`}
                >
                  <input
                    type="file"
                    ref={jdFileInputRef}
                    onChange={handleJdFileChange}
                    accept=".pdf,.docx"
                    className="hidden"
                  />
                  <p className="text-xs font-medium text-slate-700">
                    {isDraggingJd
                      ? "Drop Job Description file here!"
                      : "Click to upload or drag & drop Job Description (PDF/DOCX)"}
                  </p>
                </div>
              ) : (
                <div className="flex items-center justify-between p-3 bg-slate-50 border border-slate-200 rounded-xl">
                  <div className="flex items-center gap-2">
                    <FileText className="w-4 h-4 text-brand-600" />
                    <span className="text-xs font-medium text-slate-800 truncate max-w-[180px]">
                      {jdFile.name}
                    </span>
                  </div>
                  <button
                    type="button"
                    onClick={handleClearJdFile}
                    className="text-slate-400 hover:text-rose-600 p-1"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Action Button */}
      <div className="pt-4 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-end gap-4">
        <button
          type="submit"
          disabled={isLoading || !resumeFile}
          className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-700 hover:to-indigo-700 text-white font-semibold text-sm shadow-md shadow-brand-500/25 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          {isLoading ? (
            <>
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              <span>Analyzing Document...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              <span>Analyze Resume</span>
            </>
          )}
        </button>
      </div>
    </form>
  );
};
