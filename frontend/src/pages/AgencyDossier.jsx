import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api, num, rupees } from "../api.js";
import { Band, Loading, Topbar } from "../components/Bits.jsx";
import { Reveal } from "../components/Reveal.jsx";

/**
 * The page an auditor reads on the way to a visit.
 *
 * Every other screen here is organised around a work. An auditor's day is not — they
 * travel to an implementing agency and see whatever that body is building, which is
 * exactly why the plan batches by agency and the rota is dealt out in whole agencies.
 *
 * The care this page needs is in the comparison. A district office with four thousand
 * works surfaces more leads than one with forty, and reading the raw count as a signal is
 * how a large agency gets investigated for being large. So every figure that could be read
 * as an accusation is shown beside the national rate for the same measure, and where the
 * agency is ordinary the page says so in words rather than leaving a bar to imply
 * otherwise.
 */

function Rate({ label, value, national, format = (v) => `${(v * 100).toFixed(1)}%` }) {
  return (
    <div className="card stat">
      <div className="label">{label}</div>
      <div className="value">{value == null ? "—" : format(value)}</div>
      <div className="foot">
        {national == null ? "—" : `${format(national)} across the portfolio`}
      </div>
    </div>
  );
}

export default function AgencyDossier() {
  const { name } = useParams();
  const navigate = useNavigate();
  const [list, setList] = useState(null);
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("");

  useEffect(() => {
    api.agencies(60).then((d) => setList(d.items)).catch(console.error);
  }, []);

  useEffect(() => {
    if (!name) { setData(null); return; }
    let live = true;
    setData(null);
    setError("");
    api.agency(name)
      .then((d) => { if (live) setData(d); })
      .catch(() => { if (live) setError("No such implementing agency in this portfolio."); });
    return () => { live = false; };
  }, [name]);

  const filtered = useMemo(() => {
    if (!list) return [];
    const needle = filter.trim().toLowerCase();
    return needle
      ? list.filter((row) =>
          row.implementing_agency.toLowerCase().includes(needle)
          || (row.state || "").toLowerCase().includes(needle))
      : list;
  }, [list, filter]);

  /* ------------------------------------------------------------------ the picker */
  if (!name) {
    return (
      <>
        <Topbar title="Agency Dossier" sub="Who implements the work, and what we know about them" />
        <div className="content">
          <div className="hitl">
            <span>◈</span>
            <span>
              <strong>A briefing on a body, not a case against it.</strong> Agencies are
              listed by the exposure they carry, which tracks size as much as anything
              else. Open one to see the rate, which is the only version of this comparison
              worth acting on.
            </span>
          </div>

          <div className="card">
            <input
              className="input"
              placeholder="Filter by agency or state…"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              aria-label="Filter agencies"
            />
          </div>

          {!list ? <Loading /> : (
            <div className="card">
              <div className="table-wrap">
                <table className="plan-table">
                  <thead>
                    <tr>
                      <th>Implementing agency</th><th>State</th>
                      <th style={{ textAlign: "right" }}>Works</th>
                      <th style={{ textAlign: "right" }}>Exposure carried</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filtered.map((row) => (
                      <tr
                        key={row.implementing_agency}
                        className="row-click"
                        onClick={() =>
                          navigate(`/agency/${encodeURIComponent(row.implementing_agency)}`)}
                      >
                        <td className="plan-agency">{row.implementing_agency}</td>
                        <td>{row.state}</td>
                        <td style={{ textAlign: "right" }}>{num(row.works)}</td>
                        <td style={{ textAlign: "right" }}>{rupees(row.exposure_rupees)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </>
    );
  }

  /* ------------------------------------------------------------------ one dossier */
  if (error) {
    return (
      <>
        <Topbar title="Agency Dossier" />
        <div className="content">
          <div className="empty">
            {error} <Link to="/agency" className="link">Back to the list</Link>
          </div>
        </div>
      </>
    );
  }
  if (!data) {
    return (<><Topbar title="Agency Dossier" /><div className="content"><Loading /></div></>);
  }
  if (!data.available) {
    return (
      <>
        <Topbar title="Agency Dossier" />
        <div className="content"><div className="empty">{data.note}</div></div>
      </>
    );
  }

  const p = data.portfolio;
  const s = data.surfaced;

  return (
    <>
      <Topbar
        title={data.implementing_agency}
        sub={`${data.states.join(", ")} · ${num(p.works)} works`}
        right={<Link to="/agency" className="pill">All agencies</Link>}
      />

      <div className="content">
        <div className="hitl">
          <span>◈</span>
          <span><strong>A briefing, not a finding.</strong> {data.contract}</span>
        </div>

        {/* ------------------------------------------------------ the comparison */}
        <Reveal>
          <div className="section-title">How this agency compares</div>
          <div className="card dossier-reading">{s.reading}</div>
          <div className="grid cols-4 plan-figures" style={{ marginTop: 12 }}>
            <Rate label="Works surfaced as leads" value={s.rate} national={s.national_rate} />
            <Rate label="Still open" value={p.open_rate} national={p.national_open_rate} />
            <div className="card stat">
              <div className="label">Exposure in surfaced works</div>
              <div className="value accent">{rupees(s.exposure_rupees)}</div>
              <div className="foot">{num(s.high)} HIGH · {num(s.medium)} MEDIUM</div>
            </div>
            <div className="card stat">
              <div className="label">Median work</div>
              <div className="value">{rupees(p.median_work_rupees)}</div>
              <div className="foot">
                {rupees(p.national_median_work_rupees)} across the portfolio
              </div>
            </div>
          </div>
        </Reveal>

        {/* -------------------------------------------------- what officers found */}
        <Reveal delay={70}>
          <div className="section-title">What officers found here</div>
          <div className="card">
            <p className="plan-cost-note" style={{ marginTop: 0 }}>
              {data.field_history_note}
            </p>
            {data.field_history.length > 0 && (
              <div className="table-wrap">
                <table className="plan-table">
                  <thead>
                    <tr><th>Work</th><th>Outcome</th><th>Officer</th><th>When</th><th>Note</th></tr>
                  </thead>
                  <tbody>
                    {data.field_history.map((row, i) => (
                      <tr key={`${row.work_ref}-${i}`}>
                        <td>
                          <Link to={`/case/${row.work_ref}`} className="plan-ref">
                            {row.work_ref}
                          </Link>
                        </td>
                        <td>{row.outcome.replaceAll("_", " ").toLowerCase()}</td>
                        <td>
                          {row.actor}
                          {row.demo && <span className="chip" style={{ marginLeft: 6 }}>seeded</span>}
                        </td>
                        <td>{row.when}</td>
                        <td className="plan-agency">{row.notes}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </Reveal>

        {/* ------------------------------------------------------------ the leads */}
        <Reveal delay={130}>
          <div className="section-title">
            What is worth looking at while you are there
          </div>
          <div className="card">
            {data.top_leads.length === 0 ? (
              <div className="empty" style={{ padding: 16 }}>
                Nothing at this agency was surfaced as a lead.
              </div>
            ) : (
              <div className="table-wrap">
                <table className="plan-table">
                  <thead>
                    <tr>
                      <th>Work</th><th>Description</th><th>Band</th>
                      <th style={{ textAlign: "right" }}>Exposure</th>
                      <th>Why</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.top_leads.map((row) => (
                      <tr key={row.work_ref}>
                        <td>
                          <Link to={`/case/${row.work_ref}`} className="plan-ref">
                            {row.work_ref}
                          </Link>
                        </td>
                        <td className="plan-agency" title={row.description}>
                          {row.description}
                        </td>
                        <td><Band value={row.band} /></td>
                        <td style={{ textAlign: "right" }}>
                          {rupees(row.exposure_rupees)}
                        </td>
                        <td className="plan-agency">{row.signals.join(" · ")}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </Reveal>

        {/* ------------------------------------------------------ same-trip pairs */}
        {data.internal_duplicates.length > 0 && (
          <Reveal delay={190}>
            <div className="section-title">Near-duplicate pairs one visit could settle</div>
            <div className="card">
              <p className="plan-cost-note" style={{ marginTop: 0 }}>
                Both works in each pair sit at this agency, so a single trip can establish
                whether they are genuinely separate. Repeated descriptions are common and
                legitimate in this scheme — this is a question to put to someone, not a
                finding.
              </p>
              <div className="table-wrap">
                <table className="plan-table">
                  <thead>
                    <tr><th>Work</th><th>Work</th><th>Similarity</th><th>Description</th></tr>
                  </thead>
                  <tbody>
                    {data.internal_duplicates.map((pair) => (
                      <tr key={`${pair.a}-${pair.b}`}>
                        <td><Link to={`/case/${pair.a}`} className="plan-ref">{pair.a}</Link></td>
                        <td><Link to={`/case/${pair.b}`} className="plan-ref">{pair.b}</Link></td>
                        <td>{(pair.similarity * 100).toFixed(1)}% · {pair.classification}</td>
                        <td className="plan-agency">{pair.description}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </Reveal>
        )}

        {/* ------------------------------------------------------- what they build */}
        <Reveal delay={240}>
          <div className="section-title">What this agency builds</div>
          <div className="card">
            <div className="dossier-chips">
              {p.categories.map((row) => (
                <span key={row.category} className="chip">
                  {row.category} <b>{num(row.works)}</b>
                </span>
              ))}
            </div>
            <p className="plan-cost-note">
              {num(p.completed)} completed, {num(p.open)} open
              {p.median_completed_days
                ? ` · completed works took a median of ${num(Math.round(p.median_completed_days))} days`
                : ""}
              . Constituencies: {data.constituencies.join(", ")}.
            </p>
          </div>
        </Reveal>
      </div>
    </>
  );
}
