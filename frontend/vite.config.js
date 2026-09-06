import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

/**
 * Ports live here, in one place, and nowhere else.
 *
 * They moved off 5173/8000 because those are the two most contended ports on a developer's
 * machine — every other React app and every other FastAPI service wants them. A stale
 * process holding one is how "the site is slow" turns out to mean "you are looking at a
 * dead tab", which has already happened on this project more than once.
 */
const WEB_PORT = Number(process.env.PORT) || 4300;
const API_PORT = Number(process.env.API_PORT) || 8020;
const API_TARGET = `http://127.0.0.1:${API_PORT}`;

export default defineConfig({
  plugins: [react()],
  server: {
    port: WEB_PORT,

    // Listen on every interface, so a phone or a judge's laptop on the same wifi can open
    // the demo. The browser still only ever talks to *this* server: the app calls
    // `/api/...` relatively and Vite proxies it onward, so a visitor never needs to know
    // the API's address and nothing has to be reconfigured per device.
    host: true,

    // Fail loudly rather than silently sliding to the next port. A second server on a
    // second port is how half the team ends up looking at a stale build and calling it a
    // bug — and it is exactly what happened here: Vite quietly moved to 5174 while every
    // link still pointed at 5173.
    strictPort: true,

    proxy: {
      "/api": {
        // The API is reached over loopback even when the browser came in over the LAN —
        // it stays a local service, and only this server is exposed.
        target: API_TARGET,
        changeOrigin: true,
        // A PDF (case report, field day pack) is served in one response and can take a
        // moment on a cold cache; the default proxy timeout would cut it off mid-file.
        timeout: 120000,
        proxyTimeout: 120000,
        configure: (proxy) => {
          // Without this, an API that is not running produces a hung request and a page
          // that appears to load forever. A 502 with a readable body tells whoever is
          // looking what is actually wrong, which is that uvicorn is not up.
          proxy.on("error", (err, _req, res) => {
            const message =
              `The MPLADS API is not reachable on ${API_TARGET}. `
              + `Start it with:  python -m uvicorn mplads.api.app:app --host 0.0.0.0 --port ${API_PORT}`;
            console.error(`[api proxy] ${err.code || err.message} — ${message}`);
            if (res && !res.headersSent && res.writeHead) {
              res.writeHead(502, { "Content-Type": "application/json" });
              res.end(JSON.stringify({ detail: message }));
            }
          });
        },
      },
    },
  },

  // `npm run build && npm run preview` serves the compiled bundle instead of streaming
  // hundreds of individual modules over the network. On a phone across wifi that is the
  // difference between a demo that feels instant and one that feels like a dev server,
  // so the preview server gets the same host and proxy settings as dev.
  preview: {
    port: WEB_PORT,
    host: true,
    strictPort: true,
    proxy: {
      "/api": {
        target: API_TARGET,
        changeOrigin: true,
        timeout: 120000,
        proxyTimeout: 120000,
      },
    },
  },
});
