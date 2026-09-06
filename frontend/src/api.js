/**
 * Where the API lives.
 *
 * Empty in development, where Vite proxies `/api` to localhost:8000 and same-origin means
 * no CORS. In a split deployment — the static site on one host, FastAPI on another — set
 * `VITE_API_BASE` at build time to the API's origin, with no trailing slash.
 */
const base = (import.meta.env?.VITE_API_BASE || "").replace(/\/+$/, "");

let authToken = null;
export function _setToken(tok) { authToken = tok; }
const authHeaders = () => (authToken ? { Authorization: `Bearer ${authToken}` } : {});

async function get(path) {
  const res = await fetch(base + path, { headers: authHeaders() });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

export const api = {
  stats: (params = {}) => {
    const q = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== "" && v != null)
    ).toString();
    return get(`/api/stats?${q}`);
  },
  states: () => get("/api/states"),
  models: () => get("/api/models"),
  roles: () => get("/api/roles"),
  setToken: _setToken,
  login: (username, password) =>
    fetch(base + "/api/auth/login", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    }).then((r) => { if (!r.ok) throw new Error(String(r.status)); return r.json(); }),
  demoAccounts: () => get("/api/auth/accounts"),
  ocr: (file, workRef) => {
    const form = new FormData();
    form.append("file", file);
    // The work the officer is standing on, so a photograph already submitted for a
    // *different* sanction is reported and one re-taken for this work is not.
    if (workRef) form.append("work_ref", workRef);
    return fetch(base + "/api/ocr", { method: "POST", headers: authHeaders(), body: form })
      .then((r) => { if (!r.ok) throw new Error(String(r.status)); return r.json(); });
  },
  verifications: (ref) => get(`/api/verify/${encodeURIComponent(ref)}`),
  verify: (ref, body) =>
    fetch(base + `/api/verify/${encodeURIComponent(ref)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify(body),
    }).then((r) => { if (!r.ok) throw new Error(String(r.status)); return r.json(); }),
  fieldSummary: () => get("/api/field/summary"),
  languages: () => get("/api/languages"),
  chatCapabilities: () => get("/api/chat/capabilities"),
  chat: (body) =>
    fetch(base + "/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify(body),
    }).then((r) => {
      if (!r.ok) throw new Error(`${r.status}`);
      return r.json();
    }),
  strings: (lang) => get(`/api/strings?lang=${encodeURIComponent(lang)}`),
  portfolioInsight: (p = {}) => {
    const q = new URLSearchParams(
      Object.entries(p).filter(([, v]) => v !== "" && v != null)
    ).toString();
    return get(`/api/insight/portfolio?${q}`);
  },
  caseInsight: (ref, lang = "en") =>
    get(`/api/insight/case/${encodeURIComponent(ref)}?lang=${encodeURIComponent(lang)}`),
  temporal: () => get("/api/temporal"),
  transparency: () => get("/api/transparency"),
  compliance: () => get("/api/compliance"),
  earlyWarning: () => get("/api/early-warning"),
  healthIndex: () => get("/api/health-index"),
  archetypes: () => get("/api/archetypes"),
  duplicates: (params = {}) => {
    const q = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== "" && v != null)
    ).toString();
    return get(`/api/duplicates?${q}`);
  },
  worklist: (params = {}) => {
    const q = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== "" && v != null)
    ).toString();
    return get(`/api/worklist?${q}`);
  },
  case: (ref) => get(`/api/case/${encodeURIComponent(ref)}`),
  salesforceOverview: () => get("/api/salesforce/overview"),
  salesforceCases: (params = {}) => {
    const q = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== "" && v != null)
    ).toString();
    return get(`/api/salesforce/cases?${q}`);
  },
  salesforceCase: (ref) => get(`/api/salesforce/case/${encodeURIComponent(ref)}`),
  updateSalesforceStage: (body) =>
    fetch(base + "/api/salesforce/update-stage", {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify(body),
    }).then((r) => {
      if (!r.ok) throw new Error(String(r.status));
      return r.json();
    }),
  agentforceQuery: (question) =>
    fetch(base + "/api/agentforce/query", {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({ question }),
    }).then((r) => {
      if (!r.ok) throw new Error(String(r.status));
      return r.json();
    }),
};

/**
 * Indian-convention rupee figure. Large crore values are grouped, so the national
 * total reads "₹11,565 Cr" rather than "₹11565.47 Cr" — and drops the paise, which
 * are noise at that magnitude.
 */
export function rupees(n) {
  if (n == null) return "—";
  const grouped = (v, digits) =>
    v.toLocaleString("en-IN", { minimumFractionDigits: digits, maximumFractionDigits: digits });
  if (n >= 1e7) {
    const cr = n / 1e7;
    return `₹${grouped(cr, cr >= 1000 ? 0 : 2)} Cr`;
  }
  if (n >= 1e5) return `₹${grouped(n / 1e5, 2)} L`;
  if (n >= 1e3) return `₹${grouped(n / 1e3, 0)}K`;
  return `₹${grouped(Math.round(n), 0)}`;
}

export function num(n) {
  return n == null ? "—" : Number(n).toLocaleString("en-IN");
}
