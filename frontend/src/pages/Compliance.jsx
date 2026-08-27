import { useEffect, useState } from "react";
import { api, num, rupees } from "../api.js";
import { Band, Loading, Topbar } from "../components/Bits.jsx";
import { Reveal } from "../components/Reveal.jsx";
import { authority, scoreFill, sev, sevFill } from "../severity.js";
import { useI18n } from "../I18nContext.jsx";

const LEVELS = ["CRITICAL", "HIGH", "MEDIUM", "LOW"];

export default function Compliance() {
  const [c, setC] = useState(null);
  const [w, setW] = useState(null);
  const [h, setH] = useState(null);
  const { t } = useI18n();

  useEffect(() => {
    api.compliance().then(setC).catch(console.error);
    api.earlyWarning().then(setW).catch(() => {});
    api.healthIndex().then(setH).catch(() => {});
  }, []);

  if (!c || !w || !h) return (<><Topbar title={t("compliance.title", "Compliance & Early Warning")} /><div className="content"><Loading /></div></>);

  return (
    <>
      <Topbar title={t("compliance.title", "Compliance & Early Warning")}
        sub={t("compliance.sub", "Lifecycle deviation checks and stalling risk")}
        right={<span className="pill">Health Index {h.score}/100</span>} />
      <div className="content">
        <div className="hitl">
          <span>⚖️</span>
          <span><strong>{t("compliance.authorityLead", "Authority matters.")}</strong> {c.authority_note}</span>
        </div>

        <div className="section-title">{t("compliance.healthIndex", "MPLADS Operational Health Index")} — {h.score}/100</div>
        <div className="card" style={{ marginBottom: 20 }}>
          {h.components.map((comp) => (
            <div key={comp.name} style={{ marginBottom: 14 }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13 }}>
                <span style={{ fontWeight: 600 }}>
                  {comp.name} <span className="muted">· {t("common.weight", "weight")} {(comp.weight * 100).toFixed(0)}%</span>
                </span>
                <span>{(comp.value * 100).toFixed(1)}%</span>
              </div>
              <div className="meter">
                <span style={{ width: `${comp.value * 100}%`, background: scoreFill(comp.value) }} />
              </div>
              <div className="muted" style={{ fontSize: 12, marginTop: 4 }}>{comp.explanation}</div>
            </div>
          ))}
          <div className="muted" style={{ fontSize: 12, borderTop: "1px solid var(--line-soft)", paddingTop: 10 }}>
            {h.note}
          </div>
        </div>

        <Reveal><div className="section-title">{t("compliance.earlyLevels", "Early-warning levels (open works)")}</div></Reveal>
        <div className="grid cols-4">
          {LEVELS.map((lvl) => (
            <div className="card stat sev-tile" key={lvl} style={{ "--sev": sevFill(lvl) }}>
              <div className="label">
                <i className="glyph" aria-hidden="true" style={{ color: sevFill(lvl) }}>{sev(lvl).glyph}</i>
                {lvl}
              </div>
              <div className="value" style={{ fontSize: 26, color: sev(lvl).ink }}>
                {num(w.levels[lvl] || 0)}
              </div>
              <div className="foot">{rupees(w.exposure_by_level?.[lvl] || 0)} {t("common.exposure", "exposure")}</div>
            </div>
          ))}
        </div>
        <p className="muted" style={{ fontSize: 12.5, marginTop: 10 }}>{w.method_note}</p>

        <Reveal><div className="section-title">{t("compliance.checks", "Lifecycle compliance checks")}</div></Reveal>
        <div className="table-wrap">
          <table>
            <thead><tr>
              <th>{t("compliance.check", "Check")}</th><th>{t("compliance.authority", "Authority")}</th><th>{t("compliance.severity", "Severity")}</th>
              <th className="num">{t("common.works", "Works")}</th><th>{t("compliance.meaning", "What it means")}</th>
            </tr></thead>
            <tbody>
              {c.checks.map((chk) => {
                const a = authority(chk.authority);
                return (
                  <tr key={chk.key}>
                    <td style={{ fontWeight: 600 }}>{chk.check}</td>
                    <td><span className="badge" style={{ color: a.ink, background: a.soft }}>{a.label}</span></td>
                    <td><Band value={chk.severity} /></td>
                    <td className="num">{num(chk.works_affected)}</td>
                    <td className="muted" style={{ fontSize: 12 }}>{chk.meaning}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
