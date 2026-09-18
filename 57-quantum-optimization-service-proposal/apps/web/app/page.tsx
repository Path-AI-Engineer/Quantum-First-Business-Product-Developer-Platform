"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

type JsonObject = Record<string, unknown>;

const views = [
  ["intake", "Opportunity Intake", "01"],
  ["eligibility", "Eligibility Scorecard", "02"],
  ["formulation", "Problem Formulation", "03"],
  ["constraints", "Constraint & Feasibility Inspector", "04"],
  ["benchmark", "Benchmark Arena", "05"],
  ["comparison", "Solution Comparison", "06"],
  ["value", "Value & Sensitivity Studio", "07"],
  ["quantum", "Quantum-Readiness Gate", "08"],
  ["pilot", "Pilot Builder", "09"],
  ["proposal", "Proposal & Evidence Export", "10"],
] as const;

const dimensions = [
  "decision_value", "outcome_controllability", "data_quality", "data_latency",
  "constraint_stability", "combinatorial_structure", "baseline_maturity",
  "integration_readiness", "error_tolerance", "human_validation",
  "current_solution_cost", "qubo_fit", "organizational_maturity",
];

async function api<T>(path: string, identity: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, {
    ...init,
    headers: { "content-type": "application/json", "x-demo-identity": identity, ...init?.headers },
  });
  const body = (await response.json()) as T & { detail?: string };
  if (!response.ok) throw new Error(body.detail ?? `Request failed: ${response.status}`);
  return body;
}

function Mark({ kind = "nodes" }: { kind?: "nodes" | "chart" | "shield" }) {
  if (kind === "chart") return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 19V9m5 10V5m5 14v-7m5 7V3" /></svg>;
  if (kind === "shield") return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 5 6v5c0 4.5 2.8 8.1 7 10 4.2-1.9 7-5.5 7-10V6l-7-3Z" /><path d="m9 12 2 2 4-5" /></svg>;
  return <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="5" cy="12" r="2" /><circle cx="19" cy="6" r="2" /><circle cx="19" cy="18" r="2" /><path d="m7 11 10-4M7 13l10 4" /></svg>;
}

const opportunityBody = {
  name: "Fictional workforce planning",
  domain: "workforce_scheduling",
  decision_frequency_per_year: 250,
  current_cost_per_decision: 120,
  dimensions: Object.fromEntries(dimensions.map((name) => [name, 0.72])),
};

export default function Home() {
  const [active, setActive] = useState<(typeof views)[number][0]>("intake");
  const [identity, setIdentity] = useState("operations-owner");
  const [snapshot, setSnapshot] = useState<JsonObject | null>(null);
  const [opportunityId, setOpportunityId] = useState("");
  const [assessment, setAssessment] = useState<JsonObject | null>(null);
  const [benchmark, setBenchmark] = useState<JsonObject | null>(null);
  const [value, setValue] = useState<JsonObject | null>(null);
  const [pilot, setPilot] = useState<JsonObject | null>(null);
  const [proposal, setProposal] = useState<JsonObject | null>(null);
  const [message, setMessage] = useState("Local evidence boundary ready");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api<JsonObject>("/v1/snapshot", identity).then(setSnapshot).catch((error: Error) => setMessage(error.message));
  }, [identity]);

  const current = useMemo(() => views.find(([id]) => id === active) ?? views[0], [active]);

  async function execute<T extends JsonObject>(label: string, operation: () => Promise<T>, setter: (value: T) => void) {
    setBusy(true);
    try {
      setter(await operation());
      setMessage(label);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unknown request failure");
    } finally {
      setBusy(false);
    }
  }

  function createOpportunity(event: FormEvent) {
    event.preventDefault();
    void execute("Opportunity recorded with synthetic inputs", () => api<JsonObject>("/v1/opportunities", identity, { method: "POST", body: JSON.stringify(opportunityBody) }), (result) => setOpportunityId(String(result.opportunity_id)));
  }

  function renderSurface() {
    if (active === "intake") return <section className="surface"><Header eyebrow="Decision definition" title="Opportunity Intake" copy="Start with the recurring business decision—not with a solver or quantum provider." /><form className="form-grid" onSubmit={createOpportunity}><label>Opportunity name<input defaultValue="Fictional workforce planning" /></label><label>Domain<select defaultValue="workforce_scheduling"><option value="workforce_scheduling">Workforce scheduling</option><option value="distribution_routing">Distribution routing</option><option value="portfolio_allocation">Portfolio allocation</option></select></label><label>Decisions / year<input type="number" defaultValue="250" /></label><label>Current cost / decision<input type="number" defaultValue="120" /></label><button className="primary" type="submit" disabled={busy}>Record synthetic opportunity</button></form><Boundary /></section>;
    if (active === "eligibility") return <section className="surface"><Header eyebrow="Falsifiable gate" title="Eligibility Scorecard" copy="Thirteen dimensions preserve unknowns, confidence, evidence gaps, and the next experiment." /><ScoreGrid /><button className="primary" disabled={!opportunityId || busy} onClick={() => void execute("Eligibility recommendation calculated", () => api<JsonObject>(`/v1/opportunities/${opportunityId}/assess`, identity, { method: "POST" }), setAssessment)}>Assess opportunity</button><Result data={assessment} empty="Record an opportunity first, then assess it." /></section>;
    if (active === "formulation") return <section className="surface"><Header eyebrow="Model before solver" title="Problem Formulation" copy="Every domain names variables, hard constraints, objective units, a native baseline, and a separate checker." /><div className="card-grid">{[["Workforce", "CP-SAT", "coverage · availability · load"], ["Distribution", "Routing solver", "capacity · visit exactly once"], ["Portfolio", "CP-SAT", "cardinality · exposure · return"]].map(([name, solver, rules]) => <article className="card" key={name}><span className="tag">{solver}</span><h3>{name}</h3><p>{rules}</p><a href="#constraints" onClick={() => setActive("constraints")}>Inspect guardrails <span aria-hidden="true">→</span></a></article>)}</div></section>;
    if (active === "constraints") return <section className="surface"><Header eyebrow="Independent verification" title="Constraint & Feasibility Inspector" copy="A decoded result is reportable only after the domain checker recomputes every hard constraint." /><div className="inspector"><div className="status-ring"><Mark kind="shield" /><strong>100%</strong><span>reported solutions checked</span></div><ol><li><b>Decode</b><span>Convert solver output to domain assignments.</span></li><li><b>Verify</b><span>Recompute coverage, capacity, exposure, and bounds.</span></li><li><b>Classify</b><span>Preserve infeasible and no-solution outcomes.</span></li></ol></div><Boundary /></section>;
    if (active === "benchmark") return <section className="surface"><Header eyebrow="Frozen development budget" title="Benchmark Arena" copy="Strong classical, heuristic, and exact-small runs share canonical inputs; locked test remains outside interactive tuning." /><div className="metric-row"><Metric value="66" label="development instances" /><Metric value="80 ms" label="strong run budget" /><Metric value="0" label="cloud jobs" /></div><button className="primary" disabled={busy || identity === "risk-reviewer"} onClick={() => void execute("Development benchmark completed locally", () => api<JsonObject>("/v1/benchmarks", identity, { method: "POST" }), setBenchmark)}>Run local development benchmark</button><Result data={benchmark} empty="No interactive benchmark run yet." /></section>;
    if (active === "comparison") return <section className="surface"><Header eyebrow="Feasibility before quality" title="Solution Comparison" copy="Compare normalized objective, status, runtime, bound, and variability without hiding failures." /><div className="comparison"><div className="axis"><span>Exact / strong</span><i style={{ width: "96%" }} /><b>reference</b></div><div className="axis"><span>Domain heuristic</span><i style={{ width: "72%" }} /><b>comparator</b></div><div className="axis"><span>QAOA diagnostic</span><i className="experimental" style={{ width: "51%" }} /><b>no advantage claim</b></div></div><p className="notice">Objective bars are illustrative UI structure; signed benchmark values live in the evidence bundle.</p></section>;
    if (active === "value") return <section className="surface"><Header eyebrow="Ranges, never promises" title="Value & Sensitivity Studio" copy="Expose adoption, improvement, cost, risk adjustment, horizon, break-even, and evidence needs." /><div className="tornado" aria-label="Sensitivity tornado illustration"><span style={{ width: "78%" }}>Adoption</span><span style={{ width: "62%" }}>Improvement</span><span style={{ width: "49%" }}>Integration cost</span><span style={{ width: "35%" }}>Risk adjustment</span></div><button className="primary" disabled={busy} onClick={() => void execute("Parametric value range calculated", () => api<JsonObject>("/v1/value-models", identity, { method: "POST", body: JSON.stringify({ baseline_cost_per_decision: 100, decisions_per_year: 500, improvement_low: 0.05, improvement_high: 0.15, adoption_low: 0.4, adoption_high: 0.8, integration_cost: 10000, annual_operating_cost: 2000, risk_adjustment: 0.7, horizon_years: 3 }) }), setValue)}>Calculate scenario</button><Result data={value} empty="Run a scenario to expose the value range." /></section>;
    if (active === "quantum") return <section className="surface"><Header eyebrow="Optionality, not marketing" title="Quantum-Readiness Gate" copy="A bounded QUBO experiment starts only after data, constraints, value, and a strong classical baseline are credible." /><div className="gate-list">{[["Classical baseline", "required", true], ["Independent checker", "required", true], ["Small QUBO mapping", "diagnostic", true], ["Provider workload", "not executed", false], ["Quantum advantage", "not claimed", false]].map(([name, note, state]) => <div key={String(name)}><span className={state ? "dot pass" : "dot neutral"} /><b>{name}</b><small>{note}</small></div>)}</div><Boundary /></section>;
    if (active === "pilot") return <section className="surface"><Header eyebrow="Eight weeks · shadow mode" title="Pilot Builder" copy="Acceptance, ownership, rollback, and termination are defined before any operational integration." /><div className="timeline">{["Data contract", "Formulation", "Shadow benchmark", "Decision review"].map((item, index) => <div key={item}><span>{index * 2 + 1}–{index * 2 + 2}</span><b>{item}</b></div>)}</div><button className="primary" disabled={!opportunityId || busy} onClick={() => void execute("Terminating shadow pilot drafted", () => api<JsonObject>("/v1/pilots", identity, { method: "POST", body: JSON.stringify({ opportunity_id: opportunityId, domain: "workforce_scheduling", owner: "Fictional operations owner", acceptance_metrics: ["feasibility_rate", "objective_improvement", "human_override_rate"], rollback_trigger: "Terminate after any agreed feasibility threshold breach" }) }), setPilot)}>Draft pilot</button><Result data={pilot} empty="Record an opportunity before drafting its pilot." /></section>;
    return <section className="surface"><Header eyebrow="Evidence-bound handoff" title="Proposal & Evidence Export" copy="Separate observed evidence, hypotheses, client duties, provider duties, and the missing executive decision." /><div className="export-card"><Mark kind="chart" /><div><span className="tag">optimization-service-proposal-v1</span><h3>Technical candidate</h3><p>Approval and proceed / pivot / stop remain intentionally unset.</p></div></div><button className="primary" disabled={!opportunityId || busy} onClick={() => void execute("Unapproved proposal candidate created", () => api<JsonObject>(`/v1/proposals?opportunity_id=${opportunityId}`, identity, { method: "POST" }), setProposal)}>Create candidate</button><Result data={proposal} empty="Record and assess an opportunity before exporting." /></section>;
  }

  return <main><header className="topbar"><a className="brand" href="#top" aria-label="Optimization Value Validation Lab home"><span><Mark /></span><b>OVVL</b><small>Decision evidence, before solver hype</small></a><label className="identity">Demo identity<select value={identity} onChange={(event) => setIdentity(event.target.value)}><option value="operations-owner">Operations owner</option><option value="optimization-scientist">Optimization scientist</option><option value="risk-reviewer">Risk reviewer · read-only</option></select></label></header><div className="shell"><aside aria-label="Validation lab surfaces"><p className="section-label">Validation workflow</p>{views.map(([id, name, number]) => <button key={id} className={active === id ? "active" : ""} aria-current={active === id ? "page" : undefined} onClick={() => setActive(id)}><span>{number}</span>{name}</button>)}<div className="aside-proof"><Mark kind="shield" /><b>Local-only boundary</b><small>90 synthetic instances<br />24 locked test cases</small></div></aside><div className="workspace" id="top"><section className="hero"><div><span className="eyebrow">Optimization opportunity assessment</span><h1>Prove the decision is worth optimizing.</h1><p>Diagnose readiness, benchmark strong classical methods, model conditional value, and design a pilot that can end honestly.</p></div><div className="hero-mark" aria-hidden="true"><span>90</span><small>synthetic decision fixtures</small></div></section><div className="context-bar"><div><span>Surface</span><b>{current[1]}</b></div><div><span>Corpus</span><b>{String(snapshot?.instance_count ?? 90)} fixtures</b></div><div><span>Status</span><b className="live">{message}</b></div></div>{renderSurface()}<footer><span>Classical-first · synthetic evidence · no auto-actuation</span><a href="http://127.0.0.1:8057/docs">API contract</a></footer></div></div></main>;
}

function Header({ eyebrow, title, copy }: { eyebrow: string; title: string; copy: string }) { return <div className="surface-head"><span className="eyebrow">{eyebrow}</span><h2>{title}</h2><p>{copy}</p></div>; }
function Metric({ value, label }: { value: string; label: string }) { return <div className="metric"><strong>{value}</strong><span>{label}</span></div>; }
function Boundary() { return <p className="notice"><b>Boundary:</b> synthetic, local decision support. Human review is required; no operational or financial advice.</p>; }
function ScoreGrid() { return <div className="score-grid">{["Business value", "Data readiness", "Constraint stability", "Classical baseline", "QUBO fit", "Human validation"].map((label, index) => <div key={label}><span>{label}</span><i><b style={{ width: `${58 + index * 5}%` }} /></i><strong>{58 + index * 5}</strong></div>)}</div>; }
function Result({ data, empty }: { data: JsonObject | null; empty: string }) { return <div className="result" aria-live="polite">{data ? <pre>{JSON.stringify(data, null, 2)}</pre> : <p>{empty}</p>}</div>; }
