import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api, num, rupees } from "../api.js";
import { Band, Loading, Topbar } from "../components/Bits.jsx";
import { Reveal } from "../components/Reveal.jsx";
import { sevFill } from "../severity.js";

/**
 * The five investigation stages are an *ordinal* progression, not five unrelated
 * categories — so the colour carries the order: untouched neutral, through brass and
 * terracotta while a human is working it, into green as it is verified and closed.
 *
 * These are design-system tokens. The previous set (blue / teal / amber) was a parallel
 * palette, and blue in particular is ruled out project-wide.
 */
const STAGE_COLORS = {
  New: "#c4b8a2",            // nobody has looked at it yet
  Assigned: "#9a6b1f",       // brass — it has an owner
  "In Progress": "#a8452a",  // terracotta — actively being worked
  Verified: "#43976a",       // green — an officer confirmed it on site
  Closed: "#2f5d3f",         // deep forest — finished
};
const STAGE_FALLBACK = "#c4b8a2";

export default function SalesforceHub() {
  const [overview, setOverview] = useState(null);
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCase, setSelectedCase] = useState(null);
  const [selectedEvidence, setSelectedEvidence] = useState([]);
  const [stageFilter, setStageFilter] = useState("all");
  const [tierFilter, setTierFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [activeStage, setActiveStage] = useState("New");
  const [selectedFinding, setSelectedFinding] = useState("");
  const [updating, setUpdating] = useState(false);
  const [updateMsg, setUpdateMsg] = useState("");

  // Agentforce chat state
  const [agentQuery, setAgentQuery] = useState("");
  const [agentHistory, setAgentHistory] = useState([
    {
      role: "assistant",
      content:
        "**Welcome to Agentforce for MPLADS**.\nI answer questions about investigation cases, exposure at risk, escalation tiers, and officer next steps. Cases are investigation leads with evidence, never findings of wrongdoing.",
    },
  ]);
  const [agentBusy, setAgentBusy] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setLoading(true);
    try {
      const [ov, cs] = await Promise.all([
        api.salesforceOverview(),
        api.salesforceCases({ limit: 500 }),
      ]);
      setOverview(ov);
      setCases(cs.items || []);
      if (cs.items?.length > 0) {
        selectCaseRecord(cs.items[0]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  async function selectCaseRecord(c) {
    setSelectedCase(c);
    setActiveStage(c.investigation_status || "New");
    setSelectedFinding(c.officer_finding || "");
    setUpdateMsg("");
    try {
      const detail = await api.salesforceCase(c.work_ref);
      setSelectedEvidence(detail.evidence || []);
    } catch {
      setSelectedEvidence([]);
    }
  }

  async function handleStageUpdate(newStage, finding = selectedFinding) {
    if (!selectedCase || updating) return;
    setUpdating(true);
    setUpdateMsg("");
    try {
      const res = await api.updateSalesforceStage({
        work_ref: selectedCase.work_ref,
        stage: newStage,
        officer_finding: finding,
      });
      setActiveStage(newStage);
      setUpdateMsg(`✅ Case updated to Stage: ${newStage}`);
      // Refresh local list
      setCases((prev) =>
        prev.map((item) =>
          item.work_ref === selectedCase.work_ref
            ? { ...item, investigation_status: newStage, officer_finding: finding }
            : item
        )
      );
      setSelectedCase((prev) => ({
        ...prev,
        investigation_status: newStage,
        officer_finding: finding,
      }));
    } catch (e) {
      setUpdateMsg(`❌ Failed to update stage: ${e}`);
    } finally {
      setUpdating(false);
    }
  }

  async function askAgentforce(q) {
    const question = (q || agentQuery).trim();
    if (!question || agentBusy) return;
    setAgentQuery("");
    setAgentHistory((prev) => [...prev, { role: "user", content: question }]);
    setAgentBusy(true);
    try {
      const res = await api.agentforceQuery(question);
      setAgentHistory((prev) => [
        ...prev,
        { role: "assistant", content: res.answer || "No response received." },
      ]);
    } catch {
      setAgentHistory((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "I could not query Agentforce at this moment. Ensure the backend API is active.",
        },
      ]);
    } finally {
      setAgentBusy(false);
    }
  }

  const filteredCases = useMemo(() => {
    return cases.filter((c) => {
      if (stageFilter !== "all" && c.investigation_status !== stageFilter) return false;
      if (tierFilter !== "all" && c.escalation_tier !== tierFilter) return false;
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matches =
          (c.work_ref || "").toLowerCase().includes(q) ||
          (c.description || "").toLowerCase().includes(q) ||
          (c.implementing_agency || "").toLowerCase().includes(q) ||
          (c.state || "").toLowerCase().includes(q);
        if (!matches) return false;
      }
      return true;
    });
  }, [cases, stageFilter, tierFilter, searchQuery]);

  if (loading || !overview) {
    return (
      <>
        <Topbar title="Salesforce CRM & Agentforce" />
        <div className="content">
          <Loading />
        </div>
      </>
    );
  }

  const org = overview.org;
  const stages = overview.path.stages;
  const activeStageGuidance =
    stages.find((s) => s.stage === activeStage)?.guidance || "";

  return (
    <>
      <Topbar
        title="Salesforce CRM & Agentforce"
        sub="Field Casework, Governance Path & Ministry Reports"
        right={
          <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
            <span className="pill pill-green" style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <span className="pulse-dot" style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--sev-low)", display: "inline-block" }} />
              Live Org: {org.alias}
            </span>
          </div>
        }
      />

      <div className="content">
        {/* Org Banner */}
        <div
          className="card"
          style={{
            marginBottom: 20,
            background: "linear-gradient(135deg, #fdfbf7 0%, #f4eee1 100%)",
            borderColor: "rgba(168, 69, 42, 0.25)",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 16 }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
                <h3 style={{ margin: 0, fontSize: 18, color: "var(--accent)" }}>⚡ Salesforce Connected Org</h3>
                <span className="fam-tag" style={{ background: "#e0f2fe", color: "#0369a1", fontWeight: 700 }}>
                  Org ID: {org.org_id}
                </span>
              </div>
              <div className="muted" style={{ fontSize: 13 }}>
                Connected as <strong>{org.username}</strong> · App: <strong>{overview.app.name}</strong> · Agentforce Topic: <strong>{overview.agentforce.topic}</strong>
              </div>
            </div>

            <div style={{ display: "flex", gap: 10 }}>
              <button
                className="btn btn-primary"
                onClick={() => window.open(org.instance_url, "_blank")}
                title="Launch Salesforce Lightning Console"
                style={{ display: "flex", alignItems: "center", gap: 6 }}
              >
                <span>☁ Launch Salesforce</span>
              </button>
            </div>
          </div>
        </div>

        {/* 4 Metric Cards */}
        <Reveal>
          <div className="grid cols-4" style={{ marginBottom: 24 }}>
            <div className="card stat">
              <div className="label">CRM Cases Loaded</div>
              <div className="value" style={{ fontSize: 24 }}>
                {overview.objects.Investigation_Case__c.records_loaded} HIGH
              </div>
              <div className="foot">Top prioritized leads for casework</div>
            </div>

            <div className="card stat">
              <div className="label">₹ Exposure at Risk</div>
              <div className="value accent" style={{ fontSize: 24 }}>
                {rupees(overview.objects.Investigation_Case__c.total_exposure_rupees)}
              </div>
              <div className="foot">500 high-risk cases exposure</div>
            </div>

            <div className="card stat">
              <div className="label">Evidence Items Linked</div>
              <div className="value" style={{ fontSize: 24 }}>
                {overview.objects.Evidence__c.records_loaded} items
              </div>
              <div className="foot">Master-Detail multi-signal proof</div>
            </div>

            <div className="card stat">
              <div className="label">Governance Path</div>
              <div className="value" style={{ fontSize: 24, color: "var(--sev-low-ink)" }}>
                5 Active Stages
              </div>
              <div className="foot">Officer guidance & ML label feedback</div>
            </div>
          </div>
        </Reveal>

        {/* Main Grid: Interactive Path & Casework + Agentforce */}
        <div className="grid cols-2" style={{ gap: 20, marginBottom: 24 }}>
          {/* Left Column: Interactive 5-Stage Path Console */}
          <div className="card" style={{ display: "flex", flexDirection: "column" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
              <h3 style={{ margin: 0 }}>🎯 Auditor Casework & 5-Stage Path</h3>
              {selectedCase && (
                <Link to={`/case/${selectedCase.work_ref}`} className="link" style={{ fontSize: 13 }}>
                  Open Case File →
                </Link>
              )}
            </div>

            {selectedCase ? (
              <>
                <div style={{ padding: "10px 14px", background: "var(--card-subtle, #f0ebd8)", borderRadius: 6, marginBottom: 16 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                    <div>
                      <strong style={{ fontSize: 15, color: "var(--text)" }}>{selectedCase.work_ref}</strong>
                      <span className="muted" style={{ fontSize: 12, marginLeft: 8 }}>
                        {selectedCase.state} · {selectedCase.constituency}
                      </span>
                    </div>
                    <span className="pill" style={{ background: STAGE_COLORS[selectedCase.investigation_status] || STAGE_FALLBACK, color: "#fff", fontWeight: 700, fontSize: 11 }}>
                      {selectedCase.investigation_status}
                    </span>
                  </div>
                  <div style={{ fontSize: 13, color: "var(--text-2)", marginTop: 4 }}>
                    {selectedCase.description?.slice(0, 140)}…
                  </div>
                  <div style={{ display: "flex", gap: 14, marginTop: 6, fontSize: 12 }}>
                    <span>Exposure: <strong style={{ color: "var(--accent)" }}>{rupees(selectedCase.exposure)}</strong></span>
                    <span>Tier: <strong>{selectedCase.escalation_tier}</strong></span>
                    <span>Review Target: <strong>{selectedCase.target_review_date}</strong></span>
                  </div>
                </div>

                {/* 5-Stage Visual Stepper */}
                <div style={{ marginBottom: 14 }}>
                  <div className="section-label" style={{ marginBottom: 8 }}>Investigation Path (Salesforce Standard)</div>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 4 }}>
                    {stages.map((st, idx) => {
                      const isCurrent = activeStage === st.stage;
                      const isPast = stages.findIndex((s) => s.stage === activeStage) >= idx;
                      return (
                        <button
                          key={st.stage}
                          onClick={() => handleStageUpdate(st.stage)}
                          disabled={updating}
                          style={{
                            padding: "8px 4px",
                            fontSize: 11,
                            fontWeight: isCurrent ? 700 : 500,
                            borderRadius: 4,
                            border: "1px solid",
                            borderColor: isCurrent ? STAGE_COLORS[st.stage] : "#d1d5db",
                            background: isCurrent ? STAGE_COLORS[st.stage] : isPast ? "#f3f4f6" : "#ffffff",
                            color: isCurrent ? "#ffffff" : "var(--text)",
                            cursor: "pointer",
                            transition: "all 0.15s ease",
                            textAlign: "center",
                          }}
                        >
                          {st.label}
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Stage Guidance Box */}
                <div
                  style={{
                    padding: "12px 14px",
                    background: "#fefcf6",
                    borderLeft: `4px solid ${STAGE_COLORS[activeStage] || "var(--accent)"}`,
                    borderRadius: "0 6px 6px 0",
                    marginBottom: 16,
                  }}
                >
                  <div style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", color: STAGE_COLORS[activeStage] || "var(--accent)" }}>
                    Officer Guidance for Stage: {activeStage}
                  </div>
                  <div style={{ fontSize: 13, color: "var(--text)", marginTop: 4, fontStyle: "italic" }}>
                    "{activeStageGuidance}"
                  </div>
                </div>

                {/* Officer Finding Selector for Verified & Closed Stages */}
                {(activeStage === "Verified" || activeStage === "Closed") && (
                  <div style={{ marginBottom: 16, padding: "10px 12px", background: "#f8fafc", borderRadius: 6, border: "1px solid #e2e8f0" }}>
                    <label style={{ fontSize: 12, fontWeight: 600, display: "block", marginBottom: 6 }}>
                      Officer Ground-Truth Finding (ML Label Output):
                    </label>
                    <div style={{ display: "flex", gap: 8 }}>
                      <select
                        className="input"
                        style={{ flex: 1, padding: "6px 10px", fontSize: 13 }}
                        value={selectedFinding}
                        onChange={(e) => {
                          setSelectedFinding(e.target.value);
                          handleStageUpdate(activeStage, e.target.value);
                        }}
                      >
                        <option value="">-- Select Officer Finding --</option>
                        {overview.findings?.map((f) => (
                          <option key={f} value={f}>
                            {f}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                )}

                {updateMsg && (
                  <div style={{ fontSize: 12, fontWeight: 600, color: updateMsg.startsWith("✅") ? sevFill("LOW") : sevFill("HIGH"), marginBottom: 12 }}>
                    {updateMsg}
                  </div>
                )}

                {/* Evidence Related List */}
                <div>
                  <div className="section-label" style={{ marginBottom: 8 }}>
                    Evidence Items ({selectedEvidence.length} Linked Records)
                  </div>
                  <div style={{ maxHeight: 150, overflowY: "auto", border: "1px solid #e5e7eb", borderRadius: 6 }}>
                    {selectedEvidence.length === 0 ? (
                      <div className="muted" style={{ padding: 12, fontSize: 12 }}>No explicit evidence rows loaded.</div>
                    ) : (
                      selectedEvidence.map((ev, i) => (
                        <div
                          key={i}
                          style={{
                            padding: "8px 12px",
                            borderBottom: i < selectedEvidence.length - 1 ? "1px solid #f1f5f9" : "none",
                            fontSize: 12,
                          }}
                        >
                          <span className="fam-tag" style={{ marginRight: 6 }}>{ev.family}</span>
                          <strong>{ev.signal}:</strong> <span className="muted">{ev.detail}</span>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </>
            ) : (
              <div className="empty">Select a case below to view and update its Path stage.</div>
            )}
          </div>

          {/* Right Column: Agentforce AI Copilot Terminal */}
          <div className="card" style={{ display: "flex", flexDirection: "column", height: "100%" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ fontSize: 20 }}>🤖</span>
                <div>
                  <h3 style={{ margin: 0, fontSize: 16 }}>Agentforce Investigation Assistant</h3>
                  <div className="muted" style={{ fontSize: 11 }}>
                    Topic: <strong>{overview.agentforce.topic}</strong> (Non-Fraud Protocol)
                  </div>
                </div>
              </div>
              <button
                className="btn btn-secondary"
                style={{ padding: "4px 10px", fontSize: 11 }}
                onClick={() => setAgentHistory([])}
              >
                Clear
              </button>
            </div>

            {/* Quick Prompts */}
            <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 12 }}>
              {[
                "Show HIGH priority cases in Bihar",
                "Which case has the highest exposure?",
                "Show cases in Ministry Review tier",
                `Next step for ${selectedCase?.work_ref || "MP3018356-W86316"}`,
              ].map((p) => (
                <button
                  key={p}
                  className="chat-chip"
                  style={{ fontSize: 11, padding: "4px 10px" }}
                  onClick={() => askAgentforce(p)}
                >
                  → {p}
                </button>
              ))}
            </div>

            {/* Chat Messages */}
            <div
              style={{
                flex: 1,
                minHeight: 280,
                maxHeight: 340,
                overflowY: "auto",
                background: "#faf8f2",
                border: "1px solid #e7e2d4",
                borderRadius: 8,
                padding: 12,
                marginBottom: 12,
                display: "flex",
                flexDirection: "column",
                gap: 10,
              }}
            >
              {agentHistory.map((msg, i) => (
                <div
                  key={i}
                  style={{
                    alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
                    maxWidth: "88%",
                    background: msg.role === "user" ? "var(--accent)" : "#ffffff",
                    color: msg.role === "user" ? "#ffffff" : "var(--text)",
                    padding: "8px 12px",
                    borderRadius: 8,
                    fontSize: 12.5,
                    lineHeight: 1.45,
                    border: msg.role === "user" ? "none" : "1px solid #e2ded5",
                    whiteSpace: "pre-line",
                  }}
                >
                  {msg.content}
                </div>
              ))}
              {agentBusy && (
                <div style={{ alignSelf: "flex-start", color: "var(--text-3)", fontSize: 12, fontStyle: "italic" }}>
                  Agentforce is querying Investigation Cases…
                </div>
              )}
            </div>

            {/* Input Row */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                askAgentforce();
              }}
              style={{ display: "flex", gap: 8 }}
            >
              <input
                className="input"
                placeholder="Ask Agentforce about cases, exposure, states, or next steps…"
                value={agentQuery}
                onChange={(e) => setAgentQuery(e.target.value)}
                style={{ flex: 1, fontSize: 13 }}
                disabled={agentBusy}
              />
              <button className="btn btn-primary" type="submit" disabled={agentBusy || !agentQuery.trim()}>
                Ask
              </button>
            </form>
          </div>
        </div>

        {/* Filterable Investigation Cases Queue */}
        <div className="card" style={{ marginBottom: 24 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14, flexWrap: "wrap", gap: 10 }}>
            <div>
              <h3 style={{ margin: 0 }}>📋 Salesforce Case Queue ({filteredCases.length} records)</h3>
              <div className="muted" style={{ fontSize: 12 }}>
                High-priority investigation leads synchronized to Salesforce `Investigation_Case__c`
              </div>
            </div>

            {/* Filters */}
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
              <input
                className="input"
                placeholder="Search case, agency, state…"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{ width: 200, fontSize: 12, padding: "6px 10px" }}
              />

              <select
                className="input"
                value={stageFilter}
                onChange={(e) => setStageFilter(e.target.value)}
                style={{ fontSize: 12, padding: "6px 10px" }}
              >
                <option value="all">All Stages ({cases.length})</option>
                {stages.map((s) => (
                  <option key={s.stage} value={s.stage}>
                    {s.label} ({overview.path.distribution[s.stage] || 0})
                  </option>
                ))}
              </select>

              <select
                className="input"
                value={tierFilter}
                onChange={(e) => setTierFilter(e.target.value)}
                style={{ fontSize: 12, padding: "6px 10px" }}
              >
                <option value="all">All Escalation Tiers</option>
                <option value="District Monitoring">District Monitoring</option>
                <option value="State Nodal">State Nodal</option>
                <option value="Ministry Review">Ministry Review</option>
              </select>
            </div>
          </div>

          {/* Table */}
          <div style={{ overflowX: "auto" }}>
            <table className="table" style={{ width: "100%", fontSize: 13 }}>
              <thead>
                <tr>
                  <th>Work Reference</th>
                  <th>State & Agency</th>
                  <th>Exposure at Risk</th>
                  <th>Escalation Tier</th>
                  <th>Stage</th>
                  <th>Finding</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredCases.slice(0, 15).map((c) => {
                  const isSelected = selectedCase?.work_ref === c.work_ref;
                  return (
                    <tr
                      key={c.work_ref}
                      style={{
                        background: isSelected ? "var(--card-subtle, #f5f0e3)" : "transparent",
                        cursor: "pointer",
                      }}
                      onClick={() => selectCaseRecord(c)}
                    >
                      <td>
                        <strong style={{ color: "var(--accent)" }}>{c.work_ref}</strong>
                      </td>
                      <td>
                        <div>{c.state}</div>
                        <div className="muted" style={{ fontSize: 11 }}>{c.implementing_agency}</div>
                      </td>
                      <td>
                        <strong>{rupees(c.exposure)}</strong>
                      </td>
                      <td>
                        <span className="fam-tag" style={{ fontSize: 11 }}>{c.escalation_tier}</span>
                      </td>
                      <td>
                        <span
                          className="pill"
                          style={{
                            background: STAGE_COLORS[c.investigation_status] || STAGE_FALLBACK,
                            color: "#fff",
                            fontWeight: 600,
                            fontSize: 10.5,
                            padding: "2px 8px",
                          }}
                        >
                          {c.investigation_status}
                        </span>
                      </td>
                      <td>
                        <span style={{ fontSize: 12, color: c.officer_finding ? "var(--text)" : "var(--text-3)" }}>
                          {c.officer_finding || "—"}
                        </span>
                      </td>
                      <td>
                        <button
                          className="btn btn-secondary"
                          style={{ padding: "3px 8px", fontSize: 11 }}
                          onClick={(e) => {
                            e.stopPropagation();
                            selectCaseRecord(c);
                          }}
                        >
                          Manage Path
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          {filteredCases.length > 15 && (
            <div className="muted" style={{ textAlign: "center", fontSize: 12, marginTop: 12 }}>
              Showing top 15 of {filteredCases.length} matching Salesforce investigation cases.
            </div>
          )}
        </div>

        {/* Ministry Executive Reports & Dashboards Preview */}
        <Reveal delay={60}>
          <div className="card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
              <div>
                <h3 style={{ margin: 0 }}>📊 Ministry Executive Reports & Dashboard</h3>
                <div className="muted" style={{ fontSize: 12 }}>
                  Deployed Salesforce Metadata Reports: `Exposure_at_Risk_by_State`, `Cases_by_Escalation_Tier`, `Top_Exposure_by_Agency`
                </div>
              </div>
              <span className="pill pill-green">Dashboard Deployed</span>
            </div>

            <div className="grid cols-3" style={{ gap: 16 }}>
              {/* Report 1: State Exposure */}
              <div style={{ padding: 14, background: "#faf8f2", borderRadius: 8, border: "1px solid #e8e3d6" }}>
                <div style={{ fontWeight: 700, fontSize: 13, marginBottom: 4 }}>Exposure at Risk by State</div>
                <div className="muted" style={{ fontSize: 11, marginBottom: 10 }}>Summary with Horizontal Bar</div>
                {overview.top_states.slice(0, 5).map((st) => (
                  <div key={st.state} style={{ marginBottom: 6 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12 }}>
                      <span>{st.state}</span>
                      <strong>{rupees(st.exposure)}</strong>
                    </div>
                    <div className="meter" style={{ height: 5, marginTop: 2 }}>
                      <span style={{ width: `${Math.min(100, (st.exposure / overview.top_states[0].exposure) * 100)}%`, background: "var(--accent)" }} />
                    </div>
                  </div>
                ))}
              </div>

              {/* Report 2: Escalation Tiers */}
              <div style={{ padding: 14, background: "#faf8f2", borderRadius: 8, border: "1px solid #e8e3d6" }}>
                <div style={{ fontWeight: 700, fontSize: 13, marginBottom: 4 }}>Cases by Escalation Tier</div>
                <div className="muted" style={{ fontSize: 11, marginBottom: 10 }}>Summary with Donut Chart</div>
                {Object.entries(overview.escalation_tiers).map(([tier, count]) => (
                  <div key={tier} style={{ marginBottom: 10, padding: 8, background: "#ffffff", borderRadius: 6, border: "1px solid #eee" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12 }}>
                      <strong>{tier}</strong>
                      <span className="fam-tag">{count} Cases</span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Report 3: Deployed Metadata Info */}
              <div style={{ padding: 14, background: "#faf8f2", borderRadius: 8, border: "1px solid #e8e3d6" }}>
                <div style={{ fontWeight: 700, fontSize: 13, marginBottom: 4 }}>Salesforce Deployment Artifacts</div>
                <div className="muted" style={{ fontSize: 11, marginBottom: 10 }}>Verified in org `mplads`</div>
                <ul style={{ margin: 0, paddingLeft: 18, fontSize: 12, color: "var(--text-2)", lineHeight: 1.6 }}>
                  <li><strong>App:</strong> MPLADS Investigations</li>
                  <li><strong>Custom Object 1:</strong> Investigation_Case__c</li>
                  <li><strong>Custom Object 2:</strong> Evidence__c</li>
                  <li><strong>Path Assistant:</strong> Investigation_Path</li>
                  <li><strong>Dashboard:</strong> MPLADS Executive Summary</li>
                  <li><strong>Agentforce Topic:</strong> Investigation Lookup</li>
                </ul>
              </div>
            </div>
          </div>
        </Reveal>
      </div>
    </>
  );
}
