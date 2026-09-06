import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, API_START_HINT, num, rupees } from "../api.js";
import { Loading, Topbar } from "../components/Bits.jsx";
import { Reveal } from "../components/Reveal.jsx";
import { sev } from "../severity.js";
import { useDebounced } from "../hooks.js";

/**
 * The audit plan with names against it.
 *
 * The plan screen answers "where should the days go". A supervising officer has to issue
 * something with people on it, and that is a second problem with one hard rule: an
 * implementing agency is never split between two auditors. The plan's entire saving is
 * that the second work at an agency is cheap *because* somebody is already standing there,
 * and sending two people pays for that journey twice.
 *
 * So the unit on this page is the trip, not the work — which is also why the honest
 * failure mode, more auditors than trips, is shown as idle names rather than papered over
 * by splitting an agency in half.
 */

const TEAM_PRESETS = [1, 2, 4, 6, 8, 12];

export default function FieldRota() {
  const [budget, setBudget] = useState(50);
  const [auditors, setAuditors] = useState(4);
  const [data, setData] = useState(null);
  const [busy, setBusy] = useState(false);
  const [open, setOpen] = useState(1);
  // A failed request and an empty plan are different problems. This page reported both as
  // "no plan available - run the pipeline first" and then had no way back, because the
  // only thing that re-runs the fetch is a dial that is not rendered in that branch.
  const [failed, setFailed] = useState("");
  const [attempt, setAttempt] = useState(0);

  // The number under the slider follows the thumb; only the request waits for it to
  // settle. Without this a drag from 5 to 250 days queued a request per step.
  const askedBudget = useDebounced(budget);
  const askedAuditors = useDebounced(auditors);

  useEffect(() => {
    let live = true;
    setBusy(true);
    setFailed("");
    api.auditAssignments(askedBudget, askedAuditors)
      .then((d) => { if (live) { setData(d); setFailed(""); } })
      .catch((err) => {
        console.error(err);
        if (live) setFailed(String(err.message || err));
      })
      .finally(() => { if (live) setBusy(false); });
    return () => { live = false; };
  }, [askedBudget, askedAuditors, attempt]);

  // The API is commonly still booting when the first page is opened. One automatic retry
  // covers that without the reader having to know it happened.
  useEffect(() => {
    if (!failed || attempt > 0) return undefined;
    const timer = setTimeout(() => setAttempt(1), 1200);
    return () => clearTimeout(timer);
  }, [failed, attempt]);

  if (!data && busy) {
    return (<><Topbar title="Field Rota" /><div className="content"><Loading /></div></>);
  }
  if (!data && failed) {
    return (
      <>
        <Topbar title="Field Rota" />
        <div className="content">
          <div className="empty">
            <p><b>Could not reach the API.</b> {failed}</p>
            <p className="muted">
              The rota is computed server-side. If the API is still starting, this clears
              on its own; otherwise start it with{" "}<code>{API_START_HINT}</code>.
            </p>
            <button className="btn" onClick={() => setAttempt((n) => n + 1)}>
              Try again
            </button>
          </div>
        </div>
      </>
    );
  }
  if (!data?.available) {
    return (
      <>
        <Topbar title="Field Rota" />
        <div className="content">
          <div className="empty">
            <p>{data?.note || "No plan available. Run the pipeline first."}</p>
            <button className="btn" onClick={() => setAttempt((n) => n + 1)}>
              Try again
            </button>
          </div>
        </div>
      </>
    );
  }

  const balance = data.balance;
  const people = data.people || [];

  return (
    <>
      <Topbar
        title="Field Rota"
        sub="Who goes where, and on which day"
        right={
          <span className="pill">
            {num(data.trips)} trips · {num(data.works)} works
          </span>
        }
      />

      <div className="content">
        <div className="hitl">
          <span>◈</span>
          <span><strong>A draft rota, not a posting order.</strong> {data.contract}</span>
        </div>

        {/* ------------------------------------------------------------- the dials */}
        <div className="card plan-budget">
          <div className="plan-budget-head">
            <div>
              <div className="section-label">Auditor-days available</div>
              <div className="plan-budget-value">{budget} days</div>
            </div>
            <div className="plan-budget-presets">
              {[10, 20, 50, 100, 250].map((preset) => (
                <button
                  key={preset}
                  className={"plan-preset" + (preset === budget ? " active" : "")}
                  onClick={() => setBudget(preset)}
                >
                  {preset}
                </button>
              ))}
            </div>
          </div>
          <input
            type="range" min={5} max={250} step={5} value={budget}
            onChange={(e) => setBudget(Number(e.target.value))}
            className="plan-slider"
            aria-label="Auditor-days available"
          />

          <div className="plan-budget-head" style={{ marginTop: 18 }}>
            <div>
              <div className="section-label">Auditors on the team</div>
              <div className="plan-budget-value">{auditors} auditors</div>
            </div>
            <div className="plan-budget-presets">
              {TEAM_PRESETS.map((preset) => (
                <button
                  key={preset}
                  className={"plan-preset" + (preset === auditors ? " active" : "")}
                  onClick={() => setAuditors(preset)}
                >
                  {preset}
                </button>
              ))}
            </div>
          </div>
          <p className="plan-cost-note">{data.constraint}</p>
        </div>

        {/* ------------------------------------------------------------ headline */}
        <Reveal>
          <div className="grid cols-4 plan-figures">
            <div className="card stat">
              <div className="label">Busiest round</div>
              <div className="value accent">{balance.busiest_days}</div>
              <div className="foot">auditor-days · quietest {balance.quietest_days}</div>
            </div>
            <div className="card stat">
              <div className="label">Spread across the team</div>
              <div className="value">{balance.spread_days}</div>
              <div className="foot">days between busiest and quietest</div>
            </div>
            <div className="card stat">
              <div className="label">Agency visits</div>
              <div className="value">{num(data.trips)}</div>
              <div className="foot">never split between two auditors</div>
            </div>
            <div className="card stat">
              <div className="label">Exposure covered</div>
              <div className="value" style={{ color: sev("LOW").ink }}>
                {rupees(data.exposure_rupees)}
              </div>
              <div className="foot">across {num(data.works)} works</div>
            </div>
          </div>
        </Reveal>

        {/* ------------------------------------------------------------- balance */}
        <Reveal delay={70}>
          <div className="section-title">How even the rota actually is</div>
          <div className="card">
            <div className="rota-bars">
              {people.map((person) => (
                <div key={person.auditor} className="rota-bar-row">
                  <div className="rota-bar-label">{person.label}</div>
                  <div className="rota-bar-track">
                    <span
                      className="rota-bar-fill"
                      style={{
                        width: `${Math.max(
                          (person.auditor_days / (balance.busiest_days || 1)) * 100, 1.5,
                        )}%`,
                      }}
                    />
                  </div>
                  <div className="rota-bar-value">
                    {person.auditor_days} d
                    <span className="plan-bar-share">{person.works} works</span>
                  </div>
                </div>
              ))}
            </div>
            <p className="plan-cost-note">{balance.note}</p>
            {data.idle?.length > 0 && (
              <p className="plan-cost-note">
                <b>{data.idle.join(", ")}</b> {data.idle.length === 1 ? "has" : "have"} no
                trips at this team size. That is reported rather than fixed by splitting an
                agency in two — a rota that looks complete and costs more than the plan
                allowed is worse than one with a gap in it.
              </p>
            )}
          </div>
        </Reveal>

        {/* --------------------------------------------------------- the rounds */}
        <Reveal delay={130}>
          <div className="section-title">Each auditor's round</div>
          <div className="grid cols-2 rota-grid">
            {people.map((person) => {
              const expanded = open === person.auditor;
              return (
                <div key={person.auditor} className="card rota-card">
                  <button
                    className="rota-card-head"
                    onClick={() => setOpen(expanded ? 0 : person.auditor)}
                    aria-expanded={expanded}
                  >
                    <div>
                      <div className="rota-card-name">{person.label}</div>
                      <div className="rota-card-meta">
                        {num(person.agency_visits)} visits · {num(person.works)} works ·{" "}
                        {person.auditor_days} auditor-days over {person.calendar_days}{" "}
                        calendar days
                      </div>
                      <div className="rota-card-meta">
                        {person.states.join(", ") || "—"}
                      </div>
                    </div>
                    <div className="rota-card-figure">
                      {rupees(person.exposure_rupees)}
                      <span>{expanded ? "hide" : "show"} the round</span>
                    </div>
                  </button>

                  {expanded && (
                    <div className="rota-schedule">
                      {person.schedule.length === 0 && (
                        <div className="empty" style={{ padding: 14 }}>
                          Nothing was allocated at this team size.
                        </div>
                      )}
                      {person.schedule.map((visit, index) => (
                        <div key={visit.implementing_agency} className="rota-visit">
                          <div className="rota-visit-head">
                            <span className="rota-day">
                              {visit.day_from === visit.day_to
                                ? `Day ${visit.day_from}`
                                : `Days ${visit.day_from}–${visit.day_to}`}
                            </span>
                            <span className="rota-visit-agency"
                              title={visit.implementing_agency}>
                              {index + 1}. {visit.implementing_agency}
                            </span>
                          </div>
                          <div className="rota-visit-meta">
                            {visit.state} · {visit.work_count} work
                            {visit.work_count === 1 ? "" : "s"} · {visit.cost_days}{" "}
                            auditor-days · {rupees(visit.exposure_rupees)}
                          </div>
                          <ul className="rota-works">
                            {visit.works.map((work) => (
                              <li key={work.work_ref}>
                                <Link to={`/case/${work.work_ref}`} className="plan-ref">
                                  {work.work_ref}
                                </Link>
                                <span className="rota-work-band">{work.band}</span>
                                <span className="rota-work-exposure">
                                  {rupees(work.exposure_rupees)}
                                </span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      ))}

                      <a
                        className="btn rota-pack"
                        href={api.dayPackUrl(person.auditor, askedBudget, askedAuditors)}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Field day pack (PDF)
                      </a>
                      <p className="plan-cost-note">
                        The itinerary as a document to carry, with a box to tick against
                        every work and the cost model printed on it — an officer who finds
                        the assumption wrong in the field is the fastest way it ever gets
                        corrected.
                      </p>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </Reveal>
      </div>
    </>
  );
}
