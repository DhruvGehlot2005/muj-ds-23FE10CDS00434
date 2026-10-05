/**
 * @file build.ts
 * @description Bun build script compiling TypeScript/React bundle and Tailwind CSS
 * @module frontend/build
 */

import { existsSync, mkdirSync } from "fs";
import { join } from "path";

const outDir = join(import.meta.dir, "public", "dist");
if (!existsSync(outDir)) {
  mkdirSync(outDir, { recursive: true });
}

console.log("Building React bundle with Bun...");
const buildResult = await Bun.build({
  entrypoints: [join(import.meta.dir, "src", "index.tsx")],
  outdir: outDir,
  naming: "bundle.[ext]",
  target: "browser",
  minify: process.env.NODE_ENV === "production",
  sourcemap: "inline",
});

if (!buildResult.success) {
  console.error("Bun build failed:");
  for (const message of buildResult.logs) {
    console.error(message);
  }
  process.exit(1);
}

console.log("React bundle built successfully at public/dist/bundle.js");

// Build Tailwind CSS
console.log("Compiling Tailwind CSS with Bun...");
const tailwindProc = Bun.spawn([
  "bunx",
  "tailwindcss",
  "-i",
  join(import.meta.dir, "src", "index.css"),
  "-o",
  join(outDir, "index.css"),
  "--minify",
], {
  cwd: import.meta.dir,
  stdout: "inherit",
  stderr: "inherit",
});

const tailwindExit = await tailwindProc.exited;
if (tailwindExit !== 0) {
  console.error(`Tailwind compilation exited with code ${tailwindExit}`);
  process.exit(tailwindExit);
}

console.log("Tailwind CSS compiled successfully at public/dist/index.css");
