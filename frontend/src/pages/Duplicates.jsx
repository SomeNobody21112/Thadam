import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, num, rupees } from "../api.js";
import { Band, Loading, Topbar } from "../components/Bits.jsx";
import { CountUp, Reveal } from "../components/Reveal.jsx";
import { DUPLICATE_LEVEL, prettify } from "../severity.js";
import { useI18n } from "../I18nContext.jsx";

const PAGE = 20;

export default function Duplicates() {
  const [d, setD] = useState(null);
  const [page, setPage] = useState(0);
  const { t } = useI18n();

  useEffect(() => {
    setD(null);
    api.duplicates({ limit: PAGE, offset: page * PAGE, concerning_only: true })
      .then(setD).catch(console.error);
  }, [page]);

  if (!d) return (<><Topbar title={t("duplicates.title", "Near-Duplicate Detection")} /><div className="content"><Loading /></div></>);

  const s = d.summary || {};
  const pages = Math.ceil(d.total / PAGE);

  return (
    <>
      <Topbar title={t("duplicates.title", "Near-Duplicate Detection")}
        sub={t("duplicates.sub", "Semantic similarity over 384-dimensional description embeddings")}
        right={<span className="pill">{num(d.total)} {t("duplicates.concerningPairs", "concerning pairs")}</span>} />
      <div className="content">
        <div className="hitl">
          <span>🔍</span>
          <span>
            <strong>Repeated descriptions are normal in this scheme</strong> — one MP
            recommending forty street lights writes the same sentence forty times. So we only
            treat a pair as concerning when it is near-identical, <strong>from the same
            implementing agency, for a near-identical amount</strong>. That is the shape a
            repeated claim would take. It is a question for a human, never proof.
          </span>
        </div>

        <Reveal><div className="grid cols-4">
          <div className="card stat">
            <div className="label">{t("duplicates.candidatesFound", "Candidate pairs found")}</div>
            <div className="value" style={{ fontSize: 26 }}>{num(s.total_pairs)}</div>
            <div className="foot">{t("duplicates.acrossBlocks", "across state x work-type blocks")}</div>
          </div>
          <div className="card stat">
            <div className="label">{t("duplicates.concerning", "Administratively concerning")}</div>
            <div className="value accent" style={{ fontSize: 26 }}>{num(s.concerning_pairs)}</div>
            <div className="foot">{t("duplicates.sameAgencyAmount", "same agency + near-identical amount")}</div>
          </div>
          <div className="card stat">
            <div className="label">{t("duplicates.identicalText", "Character-identical text")}</div>
            <div className="value" style={{ fontSize: 26 }}>{num(s.identical_text_pairs)}</div>
          </div>
          <div className="card stat">
            <div className="label">{t("duplicates.sameAgency", "Same implementing agency")}</div>
            <div className="value" style={{ fontSize: 26 }}>{num(s.same_agency_pairs)}</div>
          </div>
        </div>

        </Reveal>
        <Reveal><div className="section-title">{t("duplicates.candidatePairs", "Candidate pairs")}</div></Reveal>
        <div className="table-wrap">
          <table>
            <thead><tr>
              <th>{t("duplicates.workA", "Work A")}</th><th>{t("duplicates.workB", "Work B")}</th><th>{t("duplicates.similarity", "Similarity")}</th>
              <th className="num">{t("worklist.amount", "Amount")}</th><th>{t("worklist.state", "State")}</th>
            </tr></thead>
            <tbody>
              {d.items.map((p, i) => (
                <tr key={i}>
                  <td>
                    <Link to={`/case/${p.work_ref_a}`} className="link">
                      {p.work_ref_a}
                    </Link>
                    <div className="desc-cell muted" style={{ fontSize: 11 }}>{p.description_a}</div>
                  </td>
                  <td>
                    <Link to={`/case/${p.work_ref_b}`} className="link">
                      {p.work_ref_b}
                    </Link>
                    <div className="desc-cell muted" style={{ fontSize: 11 }}>{p.description_b}</div>
                  </td>
                  <td>
                    <Band
                      value={DUPLICATE_LEVEL[p.classification] || "NONE"}
                      label={`${(p.similarity * 100).toFixed(1)}%`}
                    />
                    <div className="muted" style={{ fontSize: 10, marginTop: 3 }}>
                      {prettify(p.classification)}
                    </div>
                  </td>
                  <td className="num">{rupees(p.amount_a)}</td>
                  <td className="muted">{p.state_name}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="pager">
          <span className="muted">Page {page + 1} of {num(pages)}</span>
          <div style={{ display: "flex", gap: 8 }}>
            <button className="btn" disabled={page === 0} onClick={() => setPage(page - 1)}>← Prev</button>
            <button className="btn" disabled={page + 1 >= pages} onClick={() => setPage(page + 1)}>Next →</button>
          </div>
        </div>
      </div>
    </>
  );
}
