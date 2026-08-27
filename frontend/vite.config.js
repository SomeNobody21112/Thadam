import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    // An assigned port wins. A stale process holding 5173 otherwise sends the
    // server to 5174 while everything else still points at 5173.
    port: Number(process.env.PORT) || 5173,
    proxy: {
      "/api": { target: "http://127.0.0.1:8000", changeOrigin: true },
    },
  },
});
