const base = "";

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
    fetch("/api/auth/login", {
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
    return fetch("/api/ocr", { method: "POST", headers: authHeaders(), body: form })
      .then((r) => { if (!r.ok) throw new Error(String(r.status)); return r.json(); });
  },
  verifications: (ref) => get(`/api/verify/${encodeURIComponent(ref)}`),
  verify: (ref, body) =>
    fetch(`/api/verify/${encodeURIComponent(ref)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify(body),
    }).then((r) => { if (!r.ok) throw new Error(String(r.status)); return r.json(); }),
  fieldSummary: () => get("/api/field/summary"),
  casework: (ref) => get(`/api/case/${encodeURIComponent(ref)}/casework`),
  auditPlan: (budgetDays) => get(`/api/audit-plan?budget_days=${budgetDays}`),
  // The report opens in a tab rather than downloading through fetch: the browser renders
  // a PDF natively, and an officer usually wants to read it before deciding to keep it.
  caseReportUrl: (ref) => `/api/case/${encodeURIComponent(ref)}/report.pdf`,
  languages: () => get("/api/languages"),
  chatCapabilities: () => get("/api/chat/capabilities"),
  chat: (body) =>
    fetch("/api/chat", {
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
    fetch("/api/salesforce/update-stage", {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify(body),
    }).then((r) => {
      if (!r.ok) throw new Error(String(r.status));
      return r.json();
    }),
  agentforceQuery: (question, lang = "en") =>
    fetch("/api/agentforce/query", {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({ question, lang }),
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
