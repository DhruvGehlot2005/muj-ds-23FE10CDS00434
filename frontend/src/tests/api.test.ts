/**
 * @file api.test.ts
 * @description Frontend unit tests for file validation and service contracts
 * @module frontend/tests/api.test
 */

import { describe, expect, test } from "bun:test";
import { validateUploadFile } from "../services/api";

describe("Frontend File Validation", () => {
  test("validates valid PDF file without error", () => {
    const validPdf = new File(["test pdf content"], "resume.pdf", {
      type: "application/pdf",
    });
    expect(() => validateUploadFile(validPdf)).not.toThrow();
  });

  test("validates valid DOCX file without error", () => {
    const validDocx = new File(["test docx content"], "resume.docx", {
      type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    });
    expect(() => validateUploadFile(validDocx)).not.toThrow();
  });

  test("rejects unsupported text file", () => {
    const textFile = new File(["plain text"], "resume.txt", {
      type: "text/plain",
    });
    expect(() => validateUploadFile(textFile)).toThrow("Only PDF and DOCX files are supported.");
  });

  test("rejects unsupported image file", () => {
    const imageFile = new File(["image data"], "scan.png", {
      type: "image/png",
    });
    expect(() => validateUploadFile(imageFile)).toThrow("Only PDF and DOCX files are supported.");
  });

  test("rejects oversized file (>10MB)", () => {
    const elevenMb = 11 * 1024 * 1024;
    const oversizedFile = {
      name: "large_resume.pdf",
      size: elevenMb,
      type: "application/pdf",
    } as unknown as File;

    expect(() => validateUploadFile(oversizedFile)).toThrow("exceeds 10MB limit");
  });
});
