/**
 * @file server.ts
 * @description Native Bun dev/production static file server with SPA routing and API reverse proxy
 * @module frontend/server
 */

import { existsSync, mkdirSync, watch } from "fs";
import { join } from "path";

const PORT = 3000;
const BACKEND_PORT = 8000;
const PUBLIC_DIR = join(import.meta.dir, "public");
const SRC_DIR = join(import.meta.dir, "src");

// Ensure initial build is performed
const buildScript = join(import.meta.dir, "build.ts");
async function runBuild() {
  const proc = Bun.spawn(["bun", "run", buildScript], {
    cwd: import.meta.dir,
    stdout: "inherit",
    stderr: "inherit",
  });
  await proc.exited;
}

// Build once before serving
await runBuild();

// Watch src/ directory and rebuild on change with debouncing
let debounceTimer: ReturnType<typeof setTimeout> | null = null;
try {
  watch(SRC_DIR, { recursive: true }, (_eventType, filename) => {
    if (debounceTimer) clearTimeout(debounceTimer);
    debounceTimer = setTimeout(async () => {
      console.log(`\n[watch] File change detected: ${filename}. Rebuilding...`);
      await runBuild();
      console.log("[watch] Rebuild completed successfully. Refresh your browser!\n");
    }, 150);
  });
  console.log(`[watch] Watching ${SRC_DIR} for changes...`);
} catch (e: any) {
  console.warn(`[watch] Directory watching setup note: ${e.message}`);
}

console.log(`Starting Bun frontend server on http://localhost:${PORT}...`);

Bun.serve({
  port: PORT,
  async fetch(req) {
    const url = new URL(req.url);

    // 1. Reverse proxy /api/* requests to FastAPI backend on port 8000
    if (url.pathname.startsWith("/api/")) {
      const targetUrl = `http://127.0.0.1:${BACKEND_PORT}${url.pathname}${url.search}`;
      try {
        const body =
          req.method === "GET" || req.method === "HEAD" ? undefined : req.body;
        const proxyResponse = await fetch(targetUrl, {
          method: req.method,
          headers: req.headers,
          body,
        });

        const headers = new Headers(proxyResponse.headers);
        headers.set("Access-Control-Allow-Origin", "*");

        return new Response(proxyResponse.body, {
          status: proxyResponse.status,
          headers,
        });
      } catch (err: any) {
        return new Response(
          JSON.stringify({
            success: false,
            error: "BACKEND_NOT_RUNNING",
            message:
              "FastAPI backend server is not running on http://127.0.0.1:8000. Please start the backend in a separate terminal: python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000",
            details: { reason: err.message },
          }),
          {
            status: 503,
            headers: {
              "Content-Type": "application/json",
              "Access-Control-Allow-Origin": "*",
            },
          }
        );
      }
    }

    // 2. Serve static files from public directory
    let filePath = join(PUBLIC_DIR, url.pathname);

    // Default to index.html for root path
    if (url.pathname === "/" || url.pathname === "") {
      filePath = join(PUBLIC_DIR, "index.html");
    }

    const file = Bun.file(filePath);
    if (await file.exists()) {
      return new Response(file, {
        headers: {
          "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate",
          "Pragma": "no-cache",
          "Expires": "0",
        },
      });
    }

    // SPA fallback: return index.html for unknown frontend routes
    const indexFile = Bun.file(join(PUBLIC_DIR, "index.html"));
    if (await indexFile.exists()) {
      return new Response(indexFile, {
        headers: {
          "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate",
          "Pragma": "no-cache",
          "Expires": "0",
        },
      });
    }

    return new Response("Not Found", { status: 404 });
  },
});

console.log(`Bun frontend server active at http://localhost:${PORT}`);
