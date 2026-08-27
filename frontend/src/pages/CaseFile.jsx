import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, num, rupees } from "../api.js";
import { Band, Loading, Topbar } from "../components/Bits.jsx";
import { Reveal } from "../components/Reveal.jsx";
import { authority, prettify, riskFill, sevFill } from "../severity.js";
import Insight from "../components/Insight.jsx";
import FieldVerify from "../components/FieldVerify.jsx";
import CaseworkStrip from "../components/CaseworkStrip.jsx";

const FAM_ICON = {
  amount: "₹", duration: "⏱", lifecycle: "⚑",
  behaviour: "📈", multivariate: "◈", duplication: "⧉",
};

function Meter({ value, color }) {
  return (
    <div className="meter">
      <span style={{ width: `${Math.round(value * 100)}%`, background: color }} />
    </div>
  );
}

export default function CaseFile() {
  const { ref } = useParams();
  const [c, setC] = useState(null);
  const [sfCase, setSfCase] = useState(null);
  const [err, setErr] = useState(null);
  const [activeStage, setActiveStage] = useState("New");
  const [sfFinding, setSfFinding] = useState("");
  const [sfUpdating, setSfUpdating] = useState(false);
  const [sfMsg, setSfMsg] = useState("");

  useEffect(() => {
    setC(null); setErr(null); setSfCase(null);
    api.case(ref).then(setC).catch((e) => setErr(String(e)));
    api.salesforceCase(ref)
      .then((data) => {
        setSfCase(data);
        setActiveStage(data.current_stage || "New");
        setSfFinding(data.case?.officer_finding || "");
      })
      .catch(() => setSfCase(null));
  }, [ref]);

  async function updateSfStage(stage, finding = sfFinding) {
    if (sfUpdating) return;
    setSfUpdating(true);
    setSfMsg("");
    try {
      await api.updateSalesforceStage({
        work_ref: ref,
        stage: stage,
        officer_finding: finding,
      });
      setActiveStage(stage);
      setSfMsg(`✅ Updated Salesforce stage to ${stage}`);
    } catch (e) {
      setSfMsg(`❌ Failed to update: ${e}`);
    } finally {
      setSfUpdating(false);
    }
  }

  if (err) return (<><Topbar title="Case File" /><div className="content"><div className="empty">{err}</div></div></>);
  if (!c) return (<><Topbar title="Case File" /><div className="content"><Loading /></div></>);
  if (c.surfaced === false) return <ClearRecord work={c} />;

  const id = c.identity;
  return (
    <>
      <Topbar title="Case File" sub={c.work_ref}
        right={<Band value={c.confidence_band} />} />
      <div className="content">
        <Link to="/worklist" className="back">← Back to worklist</Link>
        <div className="case-actions">
          <a className="btn-report" href={api.caseReportUrl(ref)} target="_blank"
             rel="noreferrer" title="Open the printable case report">
            <span className="btn-report-icon">▤</span>
            Download case report (PDF)
          </a>
        </div>

        <div className="card" style={{ marginBottom: 18, fontSize: 13.5, color: "var(--text-2)" }}>
          <strong style={{ color: "var(--text)" }}>Plain summary:</strong> this work was put on the
          audit list because {c.n_signal_families} independent kinds of evidence agreed something is
          worth checking. About <strong>{rupees(c.exposure_rupees)}</strong> may be tied up if it does
          not finish. Read the evidence below, then see the recommended next step for a human.
        </div>

        <CaseworkStrip workRef={ref} />

        <Insight kind="case" workRef={ref} />

        <div className="case-head">
          <div>
            <div className="case-title">{id.description || "MPLADS Work"}</div>
            <div className="case-meta">
              {id.state} · {id.constituency} · {id.implementing_agency}
            </div>
            <div className="case-meta">
              MP: {id.mp_name} · Recommended {id.recommendation_date || "—"} · Status: {id.status}
            </div>
          </div>
          <div className="roi-badge">
            <div className="v">{rupees(c.audit_roi)}</div>
            <div className="l">Audit-ROI rank score</div>
          </div>
        </div>

        <Reveal><div className="grid cols-4" style={{ marginTop: 20 }}>
          <div className="card stat">
            <div className="label">Recommended</div>
            <div className="value" style={{ fontSize: 24 }}>{rupees(id.recommended_amount)}</div>
          </div>
          <div className="card stat">
            <div className="label">₹ Exposure at risk</div>
            <div className="value accent" style={{ fontSize: 24 }}>{rupees(c.exposure_rupees)}</div>
            <div className="foot">amount × completion risk</div>
          </div>
          <div className="card stat">
            <div className="label">Completion risk</div>
            <div className="value" style={{ fontSize: 24 }}>{Math.round(c.risk.completion_risk * 100)}%</div>
            <Meter value={c.risk.completion_risk} color={riskFill(c.risk.completion_risk)} />
            <div className="foot">basis: {c.risk.basis}</div>
          </div>
          <div className="card stat">
            <div className="label">Corroboration</div>
            <div className="value" style={{ fontSize: 24 }}>{c.n_signal_families} families</div>
            <div className="foot">independent signal families fired</div>
          </div>
        </div></Reveal>

        {sfCase && (
          <div className="card" style={{ marginTop: 18, background: "#fdfbf7", borderColor: "rgba(168, 69, 42, 0.2)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10, flexWrap: "wrap", gap: 8 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ fontSize: 16 }}>⚡</span>
                <strong style={{ fontSize: 14, color: "var(--accent)" }}>Salesforce CRM Casework & Path</strong>
                <span className="fam-tag">{sfCase.case?.escalation_tier}</span>
              </div>
              <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                <Link to="/salesforce" className="link" style={{ fontSize: 12 }}>
                  Open in Salesforce Hub →
                </Link>
              </div>
            </div>

            {/* Path Stepper */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 4, marginBottom: 12 }}>
              {sfCase.stages?.map((st, idx) => {
                const isCurrent = activeStage === st.stage;
                const colors = {
                  New: "#3b82f6", Assigned: "#a8452a", "In Progress": "#d97706",
                  Verified: "#0d9488", Closed: "#15803d",
                };
                return (
                  <button
                    key={st.stage}
                    onClick={() => updateSfStage(st.stage)}
                    disabled={sfUpdating}
                    style={{
                      padding: "6px 2px",
                      fontSize: 11,
                      fontWeight: isCurrent ? 700 : 500,
                      borderRadius: 4,
                      border: "1px solid",
                      borderColor: isCurrent ? colors[st.stage] : "#d1d5db",
                      background: isCurrent ? colors[st.stage] : "#ffffff",
                      color: isCurrent ? "#ffffff" : "var(--text)",
                      cursor: "pointer",
                      textAlign: "center",
                    }}
                  >
                    {st.label}
                  </button>
                );
              })}
            </div>

            {/* Active Stage Guidance */}
            <div style={{ fontSize: 12.5, padding: "8px 12px", background: "#ffffff", borderRadius: 4, borderLeft: "3px solid var(--accent)", color: "var(--text-2)" }}>
              <strong>Officer Guidance:</strong> <em>"{sfCase.stages?.find((s) => s.stage === activeStage)?.guidance}"</em>
            </div>

            {sfMsg && (
              <div style={{ fontSize: 12, fontWeight: 600, color: sfMsg.startsWith("✅") ? "#15803d" : "#b91c1c", marginTop: 8 }}>
                {sfMsg}
              </div>
            )}
          </div>
        )}

        <Reveal delay={80}><div className="grid cols-2" style={{ marginTop: 16 }}>
          <div className="card">
            <h3>Evidence — why this was surfaced</h3>
            {c.evidence.map((e, i) => (
              <div className="evidence-item" key={i} style={{ "--i": i }}>
                <div className="evidence-icon">{FAM_ICON[e.family] || "•"}</div>
                <div className="evidence-body">
                  <div className="s">{e.signal}<span className="fam-tag">{e.family}</span></div>
                  <div className="d">{e.detail}</div>
                </div>
              </div>
            ))}
          </div>

          <div>
            <div className="card" style={{ marginBottom: 16 }}>
              <h3>Peer context</h3>
              <dl className="kv">
                <dt>Archetype</dt><dd>{c.archetype.label}</dd>
                <dt>Peer level</dt><dd>{c.peer_context.level}</dd>
                <dt>Peer group size</dt><dd>{num(c.peer_context.group_size)} works</dd>
                <dt>Amount percentile</dt>
                <dd>{c.peer_context.amount_percentile != null
                  ? `${Math.round(c.peer_context.amount_percentile * 100)}th` : "—"}</dd>
                <dt>Priority score</dt><dd>{c.priority.toFixed(3)}</dd>
              </dl>
            </div>

            {c.early_warning && c.early_warning.level !== "LOW" && (
              <div className="card" style={{ marginBottom: 16 }}>
                <h3>Early warning</h3>
                <Band value={c.early_warning.level} />
                <Meter value={c.early_warning.score} color={sevFill(c.early_warning.level)} />
                <p className="muted" style={{ fontSize: 12.5, marginTop: 10 }}>
                  {c.early_warning.reason}
                </p>
              </div>
            )}

            {c.compliance_findings?.length > 0 && (
              <div className="card" style={{ marginBottom: 16 }}>
                <h3>Compliance findings</h3>
                {c.compliance_findings.map((f, i) => (
                  <div key={i} style={{ marginBottom: 10 }}>
                    <div style={{ fontWeight: 620, fontSize: 13 }}>
                      {f.check}
                      <span className="fam-tag">{authority(f.authority).label}</span>
                      <Band value={f.severity} />
                    </div>
                    <div className="muted" style={{ fontSize: 12 }}>{f.meaning}</div>
                  </div>
                ))}
              </div>
            )}

            {c.duplicate && (
              <div className="card" style={{ marginBottom: 16 }}>
                <h3>Near-duplicate candidate</h3>
                <dl className="kv">
                  <dt>Matched work</dt>
                  <dd><Link to={`/case/${c.duplicate.partner_work_ref}`} className="link">
                    {c.duplicate.partner_work_ref}</Link></dd>
                  <dt>Similarity</dt><dd>{(c.duplicate.similarity * 100).toFixed(1)}%</dd>
                  <dt>Classification</dt><dd>{prettify(c.duplicate.classification)}</dd>
                </dl>
              </div>
            )}

            <FieldVerify workRef={ref} />

            <div className="action-panel">
              <div className="label">Recommended next step</div>
              <div className="text">{c.recommended_next_step}</div>
              {c.suggested_actions?.length > 0 && (
                <ul style={{ margin: "12px 0 0 18px", fontSize: 13, color: "var(--text-2)" }}>
                  {c.suggested_actions.map((a, i) => <li key={i}>{a}</li>)}
                </ul>
              )}
              <div className="note">{c.disclaimer}</div>
            </div>
          </div>
        </div>
        </Reveal>
      </div>
    </>
  );
}


/**
 * A work nothing fired on — 173,288 of the 210,993.
 *
 * These used to 404, which made "we checked and it is fine" look identical to "no such
 * work", and left them unverifiable. That mattered more than it sounds: if only flagged
 * works can be visited, every field record ever written is about a work the system
 * already suspected, and a label set with no negatives in it cannot correct anything.
 */
function ClearRecord({ work }) {
  const id = work.identity;
  return (
    <>
      <Topbar title="Case File" sub={work.work_ref}
        right={<span className="pill pill-clear">Not surfaced</span>} />
      <div className="content">
        <Link to="/worklist" className="back">← Back to worklist</Link>
        <div className="case-actions">
          <a className="btn-report" href={api.caseReportUrl(work.work_ref)} target="_blank"
             rel="noreferrer" title="Open the printable case report">
            <span className="btn-report-icon">▤</span>
            Download case report (PDF)
          </a>
        </div>

        <div className="card clear-note">
          <strong>Nothing was flagged on this work.</strong> It sits inside the norms of
          its peer group on every measure we compute — amount, duration, lifecycle
          conformance, behaviour and duplication. There is no case to answer here and no
          reviewer is needed.
        </div>

        <div className="case-head">
          <div>
            <div className="case-title">{id.description || "MPLADS Work"}</div>
            <div className="case-meta">
              {id.state} · {id.constituency} · {id.implementing_agency}
            </div>
            <div className="case-meta">
              MP: {id.mp_name} · Recommended {id.recommendation_date || "—"} ·{" "}
              {id.is_completed ? `Completed ${id.completion_date || ""}` : "Open"}
            </div>
          </div>
        </div>

        <Reveal><div className="grid cols-2" style={{ margin: "20px 0 18px" }}>
          <div className="card stat">
            <div className="label">Recommended</div>
            <div className="value" style={{ fontSize: 24 }}>{rupees(id.recommended_amount)}</div>
          </div>
          <div className="card stat">
            <div className="label">Work type</div>
            <div className="value" style={{ fontSize: 17 }}>{work.archetype.label}</div>
            <div className="foot">learned from description, not declared</div>
          </div>
        </div></Reveal>

        <CaseworkStrip workRef={work.work_ref} />

        <FieldVerify workRef={work.work_ref} />

        <div className="card next-step">
          <div className="section-label">Recommended next step</div>
          <p>{work.recommended_next_step}</p>
        </div>
      </div>
    </>
  );
}
