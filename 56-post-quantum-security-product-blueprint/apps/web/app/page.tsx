"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

type Asset = {
  id: string; tenant_id: string; service: string; kind: string; owner_id: string;
  data_lifetime_years: number; business_criticality: number; external_exposure: boolean;
  vendor_dependency: boolean; migration_lead_months: number;
};
type Evidence = { id: string; asset_id: string; source_type: string; algorithm: string; knowledge: string; sha256: string; confidence: number };
type Finding = { id: string; asset_id: string; evidence_ids: string[]; band: string; knowledge: string; factors: string[]; uncertainty: string[]; recommendation: string; owner_id: string };
type Action = { id: string; finding_id: string; owner_id: string; phase: string; blocker: string | null; acceptance_evidence: string };
type Dependency = { from: string; to: string };
type Standard = { id?: string; title?: string; publication_status?: string; url?: string };
type Report = { id: string; type: string; asset_count: number; observation_count: number; finding_count: number; by_band: Record<string, number>; caveat: string; sha256: string; delta?: string | { added_observations: number; changed_priority: string[]; scope: string } };

const surfaces = [
  "Executive Posture", "Cryptographic Inventory", "Evidence & Conflicts", "Exposure Heatmap",
  "Data-Lifetime Explorer", "Dependency Graph", "Migration Portfolio", "Standard/Vendor Watch",
  "Exceptions & Decisions", "Reports & Evidence Export",
] as const;
type Surface = typeof surfaces[number];
const tenants = [
  { id: "northstar", label: "Northstar Bank" },
  { id: "aster", label: "Aster Health" },
  { id: "harbor", label: "Harbor Industrial" },
];

async function api<T>(path: string, identity: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, {
    ...init,
    headers: { "content-type": "application/json", "x-demo-identity": identity, ...(init?.headers ?? {}) },
    cache: "no-store",
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail ?? `Request failed: ${response.status}`);
  return data as T;
}

function Label({ children, tone = "neutral" }: { children: React.ReactNode; tone?: string }) {
  return <span className={`pill pill-${tone}`}>{children}</span>;
}

export default function Home() {
  const [tenant, setTenant] = useState("northstar");
  const [role, setRole] = useState("owner");
  const [surface, setSurface] = useState<Surface>("Executive Posture");
  const [assets, setAssets] = useState<Asset[]>([]);
  const [evidence, setEvidence] = useState<Evidence[]>([]);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [actions, setActions] = useState<Action[]>([]);
  const [dependencies, setDependencies] = useState<Dependency[]>([]);
  const [standards, setStandards] = useState<Standard[]>([]);
  const [selectedFinding, setSelectedFinding] = useState<string | null>(null);
  const [filter, setFilter] = useState("");
  const [report, setReport] = useState<Report | null>(null);
  const [reportType, setReportType] = useState("executive");
  const [decision, setDecision] = useState("needs_evidence");
  const [rationale, setRationale] = useState("Synthetic evidence needs owner review");
  const [waveOwner, setWaveOwner] = useState("");
  const [acceptance, setAcceptance] = useState("Owner-approved synthetic lab report");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(true);
  const identity = `demo-${tenant}-${role}`;

  const refresh = useCallback(async () => {
    setBusy(true);
    setNotice("");
    try {
      const [a, e, f, m, d, s] = await Promise.all([
        api<Asset[]>("/v1/assets", identity),
        api<Evidence[]>("/v1/observations", identity),
        api<Finding[]>("/v1/findings", identity),
        api<Action[]>("/v1/migration-actions", identity),
        api<Dependency[]>("/v1/dependencies", identity),
        api<{ standards?: Standard[]; sources?: Standard[] }>("/v1/standards", identity),
      ]);
      setAssets(a); setEvidence(e); setFindings(f); setActions(m);
      setDependencies(d);
      setWaveOwner(a[0]?.owner_id ?? "");
      setStandards(s.standards ?? s.sources ?? []);
      setSelectedFinding(null);
      setReport(null);
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "The local assessment API is unavailable.");
    } finally { setBusy(false); }
  }, [identity]);

  useEffect(() => {
    const timer = window.setTimeout(() => { void refresh(); }, 0);
    return () => window.clearTimeout(timer);
  }, [refresh]);

  const shownAssets = useMemo(() => assets.filter((a) =>
    `${a.id} ${a.service} ${a.kind} ${a.owner_id}`.toLowerCase().includes(filter.toLowerCase())), [assets, filter]);
  const selected = findings.find((f) => f.id === selectedFinding) ?? findings[0];
  const linkedEvidence = evidence.filter((item) => selected?.evidence_ids.includes(item.id));
  const counts = Object.fromEntries(["urgent", "high", "planned", "verify"].map((band) =>
    [band, findings.filter((f) => f.band === band).length]));

  async function makeReport() {
    try {
      const next = await api<Report>("/v1/reports", identity, { method: "POST", body: JSON.stringify({ type: reportType }) });
      setReport(next);
      setNotice(`${reportType} report generated from the current synthetic snapshot.`);
    } catch (error) { setNotice(error instanceof Error ? error.message : "Report failed."); }
  }

  function downloadReport() {
    if (!report) return;
    const object = URL.createObjectURL(new Blob([JSON.stringify(report, null, 2)], { type: "application/json" }));
    const link = document.createElement("a");
    link.href = object; link.download = `${report.id}.json`; link.click(); URL.revokeObjectURL(object);
  }

  async function proposeWave() {
    if (!actions[0]) return;
    try {
      const wave = await api<{ id: string }>("/v1/migration-waves", identity, {
        method: "POST", body: JSON.stringify({ name: "Synthetic lab review wave", action_ids: actions.slice(0, 3).map((a) => a.id),
          owner_id: waveOwner, acceptance_evidence: acceptance }),
      });
      setNotice(`${wave.id} proposed; no system change executed.`);
    } catch (error) { setNotice(error instanceof Error ? error.message : "Wave proposal failed."); }
  }

  async function importSynthetic() {
    const asset = assets[0];
    if (!asset) return;
    try {
      const assessment = await api<{ id: string }>("/v1/assessments", identity, { method: "POST" });
      const result = await api<{ accepted: number }>(`/v1/assessments/${assessment.id}/imports`, identity, {
        method: "POST", body: JSON.stringify({ source_type: "cbom", payload: { observations: [
          { asset_id: asset.id, algorithm: "ML-KEM", function: "key_exchange", knowledge: "inferred" },
        ] } }),
      });
      await refresh();
      setNotice(`${result.accepted} synthetic observation imported; conflicting sources require verification.`);
    } catch (error) { setNotice(error instanceof Error ? error.message : "Synthetic import failed."); }
  }

  async function saveDecision() {
    if (!selected) return;
    try {
      await api(`/v1/findings/${selected.id}/decisions`, identity, {
        method: "POST", body: JSON.stringify({ decision, rationale }),
      });
      setNotice(`Decision recorded for ${selected.id}; it does not change an asset or migration state.`);
    } catch (error) { setNotice(error instanceof Error ? error.message : "Decision failed."); }
  }

  return <div className="shell">
    <aside className="sidebar" aria-label="Command Center navigation">
      <div className="brand"><span className="brand-icon" aria-hidden="true">◇</span><span>CRYPTOGRAPHIC<br /><strong>MIGRATION</strong></span></div>
      <p className="sidebar-kicker">COMMAND CENTER / LOCAL LAB</p>
      <nav aria-label="Evidence surfaces">
        {surfaces.map((name, index) => <button key={name} type="button" aria-current={surface === name ? "page" : undefined}
          onClick={() => setSurface(name)}><span className="nav-index">{String(index + 1).padStart(2, "0")}</span>{name}</button>)}
      </nav>
      <div className="sidebar-bottom">SYNTHETIC DATA ONLY<br />No active scanning or migration</div>
    </aside>
    <main className="main">
      <header className="topbar">
        <div><span className="eyebrow">PLAN 10 / PROJECT 56</span><h1>{surface}</h1><p>Evidence-led post-quantum migration planning</p></div>
        <div className="selectors">
          <label>Organization<select value={tenant} onChange={(event) => setTenant(event.target.value)}>
            {tenants.map((item) => <option key={item.id} value={item.id}>{item.label}</option>)}
          </select></label>
          <label>Demo role<select value={role} onChange={(event) => setRole(event.target.value)}>
            <option value="owner">Program owner</option><option value="architect">Crypto architect</option>
            <option value="app_owner">Scoped app owner</option><option value="reviewer">Read-only reviewer</option>
          </select></label>
        </div>
      </header>
      <div className="disclaimer" role="note">Prototype • fictional organizations • unknown is never safe • recommendations require human review</div>
      {notice && <p className="notice" role="status">{notice}</p>}
      {busy ? <p role="status" className="loading">Loading synthetic evidence…</p> : <>
        {surface === "Executive Posture" && <>
          <section className="metrics" aria-label="Posture summary">
            <article><span>INVENTORIED ASSETS</span><strong>{assets.length}</strong><small>Scoped to selected tenant</small></article>
            <article><span>OBSERVATIONS</span><strong>{evidence.length}</strong><small>With source and digest</small></article>
            <article><span>OPEN FINDINGS</span><strong>{findings.length}</strong><small>Every finding has evidence</small></article>
            <article><span>REQUIRE VERIFICATION</span><strong>{counts.verify}</strong><small>Unknown or conflicting</small></article>
          </section>
          <section className="panel"><h2>Priority bands</h2><div className="band-grid">{Object.entries(counts).map(([band, count]) =>
            <div key={band} className="band"><Label tone={band}>{band}</Label><strong>{count}</strong></div>)}</div>
            <p className="muted">Priority is an explainable planning band, not a breach probability or certification.</p></section>
        </>}
        {surface === "Cryptographic Inventory" && <section className="panel"><div className="panel-head"><h2>Asset inventory</h2>
          <label className="search">Filter assets<input value={filter} onChange={(event) => setFilter(event.target.value)} placeholder="ID, service, owner…" /></label></div>
          <div className="table-wrap"><table><thead><tr><th>Asset</th><th>Type</th><th>Owner</th><th>Lifetime</th><th>Exposure</th></tr></thead><tbody>
            {shownAssets.map((a) => <tr key={a.id}><td><strong>{a.id}</strong><small>{a.service}</small></td><td>{a.kind}</td><td>{a.owner_id}</td><td>{a.data_lifetime_years} years</td><td>{a.external_exposure ? "External" : "Internal"}</td></tr>)}
          </tbody></table></div><p className="muted">{shownAssets.length} assets shown</p></section>}
        {surface === "Evidence & Conflicts" && <div className="two-col"><section className="panel"><div className="panel-head"><h2>Findings</h2>
          <button onClick={() => void importSynthetic()} disabled={role === "reviewer" || role === "app_owner"}>Import synthetic sample</button></div><div className="finding-list">
          {findings.map((f) => <button type="button" className={selected?.id === f.id ? "finding active" : "finding"} key={f.id}
            onClick={() => setSelectedFinding(f.id)}><span>{f.asset_id}</span><Label tone={f.band}>{f.band}</Label></button>)}
        </div></section><section className="panel" aria-label="Finding evidence">{selected ? <><h2>{selected.id}</h2>
          <p><Label tone={selected.knowledge}>{selected.knowledge}</Label> · Owner {selected.owner_id}</p><p>{selected.recommendation}</p>
          {selected.uncertainty.length > 0 && <p className="warning">{selected.uncertainty.join("; ")}</p>}
          <h3>Source path</h3>{linkedEvidence.map((item) => <div className="evidence-row" key={item.id}><strong>{item.source_type}</strong>
            <span>{item.algorithm} · {item.knowledge}</span><code title={item.sha256}>{item.sha256.slice(0, 20)}…</code></div>)}</>
          : <p>No findings in scope.</p>}</section></div>}
        {surface === "Exposure Heatmap" && <section className="panel"><h2>Exposure × criticality</h2><div className="heatmap">
          {assets.map((a) => <div key={a.id} className={`heat heat-${a.business_criticality}`} title={`${a.id}: ${a.external_exposure ? "external" : "internal"}, criticality ${a.business_criticality}`}>{a.external_exposure ? "E" : "I"}</div>)}
        </div><p className="muted">E = external; I = internal. Color denotes business criticality, not cryptographic safety.</p></section>}
        {surface === "Data-Lifetime Explorer" && <section className="panel"><h2>Protection lifetime</h2><div className="lifetime">
          {[1, 5, 10, 20].map((years) => <div key={years}><span>{years} years</span><div className="track"><i style={{ width: `${assets.length ? assets.filter((a) => a.data_lifetime_years === years).length / assets.length * 100 : 0}%` }} /></div><strong>{assets.filter((a) => a.data_lifetime_years === years).length}</strong></div>)}
        </div><p className="muted">Long-lived data requires contextual review; this view makes no attack-timing forecast.</p></section>}
        {surface === "Dependency Graph" && <section className="panel"><h2>Migration dependencies</h2><p>These {dependencies.length} tenant-scoped edges come from the synthetic corpus.</p>
          <div className="dependency-list">{dependencies.map((edge) => <div key={`${edge.from}-${edge.to}`}><span>{edge.from}</span><span aria-hidden="true">→</span><span>{edge.to}</span></div>)}</div>
          <p className="muted">Graph is a local preview; a production dependency resolver is required before sequencing changes.</p></section>}
        {surface === "Migration Portfolio" && <section className="panel"><div className="panel-head"><h2>Human-owned actions</h2><button className="primary" onClick={() => void proposeWave()} disabled={role === "reviewer" || role === "app_owner" || !actions.length}>Propose lab wave</button></div>
          <div className="wave-fields"><label>Wave owner<select value={waveOwner} onChange={(event) => setWaveOwner(event.target.value)}>
            {[...new Set(assets.map((a) => a.owner_id))].map((owner) => <option key={owner} value={owner}>{owner}</option>)}</select></label>
            <label>Acceptance evidence<input value={acceptance} onChange={(event) => setAcceptance(event.target.value)} /></label></div>
          <div className="table-wrap"><table><thead><tr><th>Action</th><th>Owner</th><th>Phase</th><th>Acceptance</th></tr></thead><tbody>{actions.map((a) =>
            <tr key={a.id}><td>{a.id}</td><td>{a.owner_id}</td><td>{a.phase}</td><td>{a.acceptance_evidence}</td></tr>)}</tbody></table></div></section>}
        {surface === "Standard/Vendor Watch" && <section className="panel"><h2>Dated standards snapshot</h2><p>Verify publication status at the source before any client-facing claim.</p>
          <div className="standard-list">{standards.map((s, i) => <a key={s.id ?? i} href={s.url} target="_blank" rel="noreferrer"><strong>{s.id ?? s.title ?? `Source ${i + 1}`}</strong><span>{s.publication_status ?? "source"} ↗</span></a>)}</div>
          <h3>Vendor-dependent assets</h3><p>{assets.filter((a) => a.vendor_dependency).length} assets require a vendor handoff or capability confirmation.</p></section>}
        {surface === "Exceptions & Decisions" && <section className="panel"><h2>Decision boundary</h2><p>Dismissals and exceptions require a named reviewer, rationale, scope and auditable evidence. This prototype does not authorize remediation.</p>
          <p><Label tone="verify">{counts.verify} verify-first findings</Label></p>
          {selected && <div className="decision-fields"><p>Selected: <strong>{selected.id}</strong></p>
            <label>Decision<select value={decision} onChange={(event) => setDecision(event.target.value)}>
              <option value="needs_evidence">Needs evidence</option><option value="confirm">Confirm</option><option value="dismiss">Dismiss</option>
            </select></label><label>Rationale<input value={rationale} onChange={(event) => setRationale(event.target.value)} /></label>
            <button className="primary" onClick={() => void saveDecision()} disabled={role === "reviewer" || role === "app_owner" || rationale.trim().length < 8}>Record synthetic decision</button>
          </div>}
          <p className="muted">Read-only reviewers cannot create a wave or change a finding decision.</p></section>}
        {surface === "Reports & Evidence Export" && <section className="panel"><div className="panel-head"><h2>Reconciled report</h2>
          <label>Report type<select value={reportType} onChange={(event) => setReportType(event.target.value)}>
            {["executive", "technical", "exposure", "migration", "conflicts", "vendor", "delta"].map((name) => <option key={name} value={name}>{name}</option>)}
          </select></label><button className="primary" onClick={() => void makeReport()}>Generate {reportType} report</button></div>
          {report ? <div className="report"><p><strong>{report.id}</strong></p><p>{report.asset_count} assets · {report.observation_count} observations · {report.finding_count} findings</p>
            {report.delta && <p>{typeof report.delta === "string" ? report.delta : `${report.delta.added_observations} added observations · ${report.delta.changed_priority.length} priority changes. ${report.delta.scope}`}</p>}
            <p className="muted">SHA-256: <code>{report.sha256}</code></p><p>{report.caveat}</p><button onClick={downloadReport}>Download JSON</button></div> : <p className="muted">Generate a report from the current authorized synthetic snapshot.</p>}</section>}
      </>}
      <footer>PROJECT 56 · v0.1 local prototype · No production authorization · No active scanning</footer>
    </main>
  </div>;
}
