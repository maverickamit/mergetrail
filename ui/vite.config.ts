import path from "node:path";
import { fileURLToPath } from "node:url";

import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const root = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      "/review": "http://127.0.0.1:8765",
      "/files": "http://127.0.0.1:8765",
    },
  },
  build: {
    outDir: path.resolve(root, "../src/mergetrail/static"),
    emptyOutDir: true,
  },
});
