import { useEffect, useState } from "react";
import { api, num } from "../api.js";
import { Band, Loading, Topbar } from "../components/Bits.jsx";
import { Reveal } from "../components/Reveal.jsx";

/**
 * Has the model been right? The one screen this system is allowed to lose on.
 *
 * Everything else explains why a work was surfaced. This asks the only question that ever
 * settles it: when an officer actually went, what did they find — and did the works we
 * called HIGH turn out worse than the ones we called MEDIUM?
 *
 * Three things this page refuses to do, each of which costs it a number it would look
 * better with. It will not print a percentage off a handful of visits. It will not let a
 * bar chart imply a ranking that the intervals do not support. And it will not report
 * precision without saying that officers go where this model sends them, so the sample was
 * chosen by the thing being measured.
 */

function Bar({ row, widest }) {
  const width = row.reportable ? (row.rate / (widest || 1)) * 100 : 0;
  return (
    <div className="rota-bar-row">
      <div className="rota-bar-label"><Band value={row.band} /></div>
      <div className="rota-bar-track">
        {row.reportable ? (
          <>
            <span className="rota-bar-fill" style={{ width: `${Math.max(width, 1.5)}%` }} />
            {/* The interval, drawn over the bar. A point estimate on its own is the thing
                this page exists to avoid showing. */}
            <span
              className="score-interval"
              style={{
                left: `${(row.interval[0] / (widest || 1)) * 100}%`,
                width: `${((row.interval[1] - row.interval[0]) / (widest || 1)) * 100}%`,
              }}
            />
          </>
        ) : (
          <span className="score-nodata">not enough visits</span>
        )}
      </div>
      <div className="rota-bar-value">
        {row.reportable ? `${Math.round(row.rate * 100)}%` : "—"}
        <span className="plan-bar-share">
          {num(row.concerns_confirmed)} of {num(row.visits)}
        </span>
      </div>
    </div>
  );
}

export default function Scoreboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.calibration()
      .then(setData)
      .catch(() => setError("The verification store is not available."));
  }, []);

  if (error) {
    return (<><Topbar title="Field Scoreboard" /><div className="content">
      <div className="empty">{error}</div></div></>);
  }
  if (!data) {
    return (<><Topbar title="Field Scoreboard" /><div className="content"><Loading /></div></>);
  }

  const widest = Math.max(
    ...data.bands.filter((r) => r.reportable).map((r) => r.interval[1]), 0.1,
  );
  const readiness = data.label_readiness || {};

  return (
    <>
      <Topbar
        title="Field Scoreboard"
        sub="Has the model been right, on the works someone actually visited"
        right={<span className="pill">{num(data.visits)} visits</span>}
      />

      <div className="content">
        <div className="hitl">
          <span>◈</span>
          <span>
            <strong>The screen that can say no.</strong> {data.contract}
          </span>
        </div>

        <Reveal>
          <div className="section-title">
            How often a visit confirmed a concern, by the band we surfaced it with
          </div>
          <div className="card">
            <div className="rota-bars">
              {data.bands.map((row) => (
                <Bar key={row.band} row={row} widest={widest} />
              ))}
            </div>

            <div className="plan-notes">
              {data.bands.map((row) => (
                <div key={row.band} className="plan-note">
                  <b>{row.band}</b>{" "}
                  {row.reportable
                    ? `${num(row.concerns_confirmed)} of ${num(row.visits)} visits found `
                      + `something wrong; ${num(row.cleared)} cleared the work. The `
                      + `interval runs ${Math.round(row.interval[0] * 100)}–`
                      + `${Math.round(row.interval[1] * 100)}%.`
                    : row.note}
                </div>
              ))}
            </div>

            <p className="plan-cost-note">
              A rate is refused below {data.min_visits_for_a_rate} visits. Three visits and
              two confirmations is three visits, not sixty-seven percent — and the bar for a
              band with too few visits is left empty rather than drawn short, because a
              short bar reads as a low rate.
            </p>
          </div>
        </Reveal>

        <Reveal delay={80}>
          <div className="section-title">Does the ranking survive contact with the field?</div>
          <div className="card dossier-reading">{data.ordering.note}</div>
        </Reveal>

        <Reveal delay={140}>
          <div className="section-title">Why this is not precision on the portfolio</div>
          <div className="card">
            <p style={{ margin: 0 }}>{data.sampling_caveat}</p>
          </div>
        </Reveal>

        <Reveal delay={200}>
          <div className="section-title">What officers recorded</div>
          <div className="grid cols-4 plan-figures">
            <div className="card stat">
              <div className="label">Works visited</div>
              <div className="value accent">{num(data.works_visited)}</div>
              <div className="foot">newest record per work</div>
            </div>
            <div className="card stat">
              <div className="label">Superseded records</div>
              <div className="value">{num(data.superseded_records_excluded)}</div>
              <div className="foot">a correction is a new record, and votes once</div>
            </div>
            <div className="card stat">
              <div className="label">Demo records excluded</div>
              <div className="value">{num(data.demo_records_excluded)}</div>
              <div className="foot">seeded for the walkthrough, never counted</div>
            </div>
            <div className="card stat">
              <div className="label">Still needed to fit weights</div>
              <div className="value">
                {num(readiness.labels_needed_to_fit_weights ?? 0)}
              </div>
              <div className="foot">nothing is refitted until then</div>
            </div>
          </div>

          <div className="card" style={{ marginTop: 12 }}>
            <div className="dossier-chips">
              {data.outcomes.map((row) => (
                <span key={row.outcome} className="chip">
                  {row.outcome.replaceAll("_", " ").toLowerCase()} <b>{num(row.count)}</b>
                </span>
              ))}
            </div>
            <p className="plan-cost-note">{readiness.note}</p>
          </div>
        </Reveal>
      </div>
    </>
  );
}
