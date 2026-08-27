import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api.js";

/**
 * Where this work has got to as a piece of casework.
 *
 * The intelligence screens answer *why was this surfaced*. This answers *and what has
 * anyone done about it*, which is the question a reviewer opening the file six weeks later
 * actually has — and until now the two halves of the product could not see each other.
 *
 * A work that is not a case says so plainly rather than rendering an empty strip. "Nobody
 * has picked this up" is a real state and worth reading.
 */
export default function CaseworkStrip({ workRef }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    let live = true;
    api.casework(workRef)
      .then((d) => { if (live) setData(d); })
      .catch(() => {});
    return () => { live = false; };
  }, [workRef]);

  if (!data) return null;

  if (!data.in_salesforce) {
    return (
      <div className="casework casework-absent">
        <span className="casework-dot" aria-hidden="true">○</span>
        <span>
          <strong>Not yet a case.</strong> {data.note}
          {data.verifications > 0 && (
            <> {data.verifications} field verification(s) exist for it regardless.</>
          )}
        </span>
      </div>
    );
  }

  const { stages, stage_index: at } = data;

  return (
    <div className="casework">
      <div className="casework-head">
        <div>
          <div className="section-label">Casework in Salesforce</div>
          <div className="casework-stage">{data.stage}</div>
        </div>
        <div className="casework-meta">
          <span className="casework-chip">{data.escalation_tier}</span>
          <span className="casework-due">review by {data.target_review_date}</span>
        </div>
      </div>

      {/* The Path, mirrored from Salesforce so an officer sees the same shape in both. */}
      <ol className="casework-path" aria-label="Investigation stage">
        {stages.map((stage, i) => (
          <li
            key={stage}
            className={
              "casework-step"
              + (i < at ? " done" : "")
              + (i === at ? " current" : "")
            }
            style={{ "--i": i }}
          >
            <span className="casework-step-mark" aria-hidden="true">
              {i < at ? "✓" : i + 1}
            </span>
            <span className="casework-step-name">{stage}</span>
          </li>
        ))}
      </ol>

      <p className="casework-guidance">{data.guidance}</p>

      {data.findings?.length > 0 && (
        <div className="casework-findings">
          <div className="section-label">What officers found</div>
          {data.findings.map((f, i) => (
            <div key={i} className="casework-finding">
              <span className="casework-outcome">{f.outcome.replace(/_/g, " ")}</span>
              {f.notes && <span className="casework-notes">{f.notes}</span>}
              <span className="casework-by">{f.actor} · {f.when}</span>
            </div>
          ))}
          <p className="casework-label-note">
            Each of these is a label. There is no dataset saying which works were problems,
            so records like these are the only ground truth this system can obtain — and
            "nothing wrong" counts for exactly as much as a confirmed one.
          </p>
        </div>
      )}

      <Link to="/salesforce" className="casework-open">Open in the casework hub →</Link>
    </div>
  );
}
