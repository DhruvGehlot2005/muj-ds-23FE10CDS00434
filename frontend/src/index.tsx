/**
 * @file index.tsx
 * @description Frontend application entry point
 * @module frontend/index
 */

import React from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";

const rootElement = document.getElementById("root");
if (!rootElement) {
  throw new Error("Failed to find root DOM element with id 'root'.");
}

const root = createRoot(rootElement);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
