import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { api, rupees } from "../api.js";
import { useAuth } from "../AuthContext.jsx";

const OUTCOME_TONE = {
  VERIFIED_COMPLETE: "ok",
  VERIFIED_IN_PROGRESS: "ok",
  NOT_STARTED: "warn",
  NOT_FOUND: "bad",
  RECORD_MISMATCH: "bad",
  NO_ACCESS: "neutral",
};

/**
 * Record what an officer found on site — the only place in this product that creates
 * data. It captures the officer's own observation, attributed and immutable; it never
 * edits a government record.
 *
 * A photograph does three things when it arrives: it is read, it is matched to a work,
 * and it is checked against every photograph submitted before it. The third is the one a
 * human cannot do at scale, and the one this screen is loudest about.
 */
export default function FieldVerify({ workRef }) {
  const { user, token } = useAuth();
  const [history, setHistory] = useState([]);
  const [outcomes, setOutcomes] = useState({});
  const [outcome, setOutcome] = useState("");
  const [notes, setNotes] = useState("");
  const [photo, setPhoto] = useState(null);      // { name, preview }
  const [scan, setScan] = useState(null);        // OCR result
  const [scanning, setScanning] = useState(false);
  const [confirmed, setConfirmed] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const fileRef = useRef(null);

  const load = () =>
    api.verifications(workRef).then((d) => {
      setHistory(d.verifications || []);
      setOutcomes(d.outcomes || {});
    }).catch(() => {});

  useEffect(() => { load(); }, [workRef]);

  function reset() {
    setOutcome(""); setNotes(""); setPhoto(null); setScan(null); setConfirmed(false);
    if (fileRef.current) fileRef.current.value = "";
  }

  async function onPhoto(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setScanning(true);
    setScan(null);
    setConfirmed(false);
    setPhoto({ name: null, preview: URL.createObjectURL(file) });
    try {
      const res = await api.ocr(file, workRef);
      setPhoto((p) => ({ ...p, name: res.photo }));
      setScan(res);
    } catch {
      setScan({ error: "Could not read that image." });
    } finally {
      setScanning(false);
    }
  }

  async function submit(e) {
    e.preventDefault();
    if (!outcome || saving || blocked) return;
    setSaving(true);
    try {
      // What the camera found travels with the finding. The reference read off the board
      // is a separate claim from the work being verified, and the two disagreeing is the
      // most useful thing a photograph can report — so it is stored, not resolved away.
      await api.verify(workRef, {
        outcome,
        notes,
        photo: photo?.name || null,
        ocr_text: scan?.lines?.map((l) => l.text).join(" ") || null,
        board_ref: scan?.match?.work_ref || null,
        board_amount: scan?.fields?.amount?.value ?? null,
        ocr_confidence: scan?.fields?.work_ref?.confidence ?? null,
        needed_confirmation: Boolean(scan?.match?.needs_confirmation || reuse.length),
        photo_reuse_count: reuse.length,
        reused_from: reuse[0]?.work_ref || null,
      });
      setSaved(true);
      reset();
      await load();
      setTimeout(() => setSaved(false), 3500);
    } catch {
      setScan({ error: "Could not save. Your account may not cover this jurisdiction." });
    } finally {
      setSaving(false);
    }
  }

  const match = scan?.match;
  const readRef = match?.work_ref;
  const wrongWork = readRef && readRef !== workRef;
  const reuse = scan?.reuse?.reuse || [];
  // A photograph reads as evidence. If it was already submitted elsewhere, or the board
  // does not clearly say which work it is, the officer acknowledges that before saving.
  const needsAck = Boolean(reuse.length || wrongWork || match?.needs_confirmation);
  const blocked = needsAck && !confirmed;

  return (
    <div className="card verify">
      <h3>Field verification</h3>

      {history.length > 0 && (
        <div className="verify-history">
          {history.map((v) => (
            <div key={v.id} className={"verify-entry " + (OUTCOME_TONE[v.outcome] || "neutral")}>
              <div className="ve-head">
                <span className="ve-outcome">{v.outcome.replace(/_/g, " ")}</span>
                <span className="ve-when">
                  {v.demo ? <span className="ve-demo">sample</span> : null}
                  {new Date(v.created_at).toLocaleDateString()}
                </span>
              </div>
              {v.notes && <div className="ve-notes">{v.notes}</div>}
              <div className="ve-actor">
                {v.actor} · {v.role}
                {v.photo && (
                  <a className="ve-photo" href={`/api/photo/${v.photo}`} target="_blank" rel="noreferrer">
                    view photograph
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {!token ? (
        <p className="verify-locked">
          Sign in to record a site verification. Findings are attributed to the officer who
          made them, so an anonymous session cannot write one.{" "}
          <Link to="/login">Sign in →</Link>
        </p>
      ) : (
        <form onSubmit={submit} className="verify-form">
          <label className="verify-label">Photograph of the site or work board</label>
          <input ref={fileRef} type="file" accept="image/*" capture="environment"
            onChange={onPhoto} className="verify-file" />

          {scanning && <div className="verify-scanning">Reading the photograph…</div>}

          {photo?.preview && (
            <div className="verify-shot">
              <img src={photo.preview} alt="Site photograph" />

              {reuse.length > 0 && (
                <div className="verify-reuse">
                  <div className="vru-head">This photograph has been submitted before</div>
                  {reuse.map((r) => (
                    <div key={r.photo + r.work_ref} className="vru-row">
                      <Link to={`/case/${r.work_ref}`}>{r.work_ref}</Link>
                      <span className="vru-when">
                        {new Date(r.first_seen).toLocaleDateString()} · {r.actor}
                      </span>
                      <span className="vru-level">
                        {r.exact_file ? "the identical file" : r.note}
                        {" "}({Math.round(r.similarity * 100)}% match)
                      </span>
                    </div>
                  ))}
                  <p className="vru-note">
                    Matched on a perceptual hash, so a resized or re-compressed copy is
                    still recognised — the checksums differ. This is a question, not a
                    finding: two phases of one road legitimately look identical from the
                    roadside.
                  </p>
                </div>
              )}

              {scan && !scan.error && (
                <div className="verify-read">
                  <div className="vr-head">
                    Text read from the photograph
                    {match?.matched && !wrongWork && !match?.needs_confirmation && (
                      <span className="vr-ok">✓ matches this work</span>
                    )}
                    {wrongWork && <span className="vr-warn">reads {readRef}</span>}
                  </div>

                  {scan.fields?.work_ref && (
                    <div className="vr-field">
                      <b>Work reference</b> {scan.fields.work_ref.value}
                      <span className="vr-conf">
                        {Math.round(scan.fields.work_ref.confidence * 100)}% character
                        confidence
                      </span>
                    </div>
                  )}
                  {scan.fields?.amount && (
                    <div className="vr-field">
                      <b>Amount</b> {rupees(scan.fields.amount.value)}
                      {match?.corroboration && (
                        <span className={match.corroboration.agrees ? "vr-conf" : "vr-warn"}>
                          {match.corroboration.agrees
                            ? "agrees with the record"
                            : `record says ${rupees(match.corroboration.amount_on_record)}`}
                        </span>
                      )}
                    </div>
                  )}

                  {match?.reason && <p className="vr-reason">{match.reason}</p>}

                  {match?.alternatives?.length > 0 && (
                    <div className="vr-alts">
                      {match.alternatives.map((a) => (
                        <Link key={a} to={`/case/${a}`} className="vr-alt">{a}</Link>
                      ))}
                    </div>
                  )}

                  <div className="vr-lines">
                    {(scan.lines || []).map((l, i) => <span key={i}>{l.text}</span>)}
                  </div>
                  <p className="vr-note">{scan.note}</p>
                </div>
              )}
              {scan?.error && <div className="login-error">{scan.error}</div>}
            </div>
          )}

          {needsAck && (
            <label className="verify-ack">
              <input type="checkbox" checked={confirmed}
                onChange={(e) => setConfirmed(e.target.checked)} />
              <span>
                I have looked at what is flagged above and this photograph belongs to{" "}
                <b>{workRef}</b>.
              </span>
            </label>
          )}

          <label className="verify-label" htmlFor="outcome">What did you find?</label>
          <select id="outcome" className="select" value={outcome}
            onChange={(e) => setOutcome(e.target.value)}>
            <option value="">— select an outcome —</option>
            {Object.entries(outcomes).map(([key, meaning]) => (
              <option key={key} value={key}>{key.replace(/_/g, " ")} — {meaning}</option>
            ))}
          </select>

          <label className="verify-label" htmlFor="notes">Notes</label>
          <textarea id="notes" className="input verify-notes" rows={3} value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="What you observed, who you spoke to, anything the record does not capture." />

          <div className="verify-actions">
            <button className="btn btn-primary" type="submit" disabled={!outcome || saving || blocked}>
              {saving ? "Recording…" : "Record verification"}
            </button>
            {blocked && (
              <span className="verify-blocked">Confirm the photograph above first</span>
            )}
            {saved && <span className="verify-saved">✓ Recorded — this entry cannot be edited</span>}
          </div>
          <p className="verify-foot">
            Signed in as <b>{user?.name}</b>. Verification records are immutable and
            attributed; correcting one means adding a new record, never editing the old.
          </p>
        </form>
      )}
    </div>
  );
}
