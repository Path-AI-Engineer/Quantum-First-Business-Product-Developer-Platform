"use client";

import { useState } from "react";

export type Initiative = { id: string; name: string; horizon: string; state: string; strategic_class: string; outcome: string; owner: string; cost: { expected: number }; kill_condition: string };
export type RoadmapData = { revision: string; approval_status: string; as_of: string; initiatives: Initiative[]; capability_graph: { nodes: number; edges: number; critical_path: string[] } };

const views = [
  ["thesis", "Strategy Thesis"], ["roadmap", "1 / 3 / 10 Roadmap"], ["scenarios", "Scenario Comparator"],
  ["portfolio", "Initiative Portfolio"], ["capabilities", "Capability Graph"], ["architecture", "Architecture Evolution"],
  ["capital", "Capital & Unit Economics"], ["risks", "Risks, Signals & Gates"], ["providers", "Providers & Partners"],
  ["governance", "PQC / AI / Quantum Governance"], ["talent", "Organization & Talent"], ["evidence", "Decision and Evidence Log"],
] as const;

const copy: Record<string, { eyebrow: string; title: string; body: string }> = {
  thesis: { eyebrow: "Where to play", title: "Win with evidence before scale", body: "Lead with PQC readiness and classical-first optimization. Preserve quantum as a measured option, never a calendar promise." },
  roadmap: { eyebrow: "Conditional horizons", title: "Commit now. Gate Year 3. Option Year 10.", body: "The sequence protects regulatory obligations, validates product economics, and exercises long-range options only when observable triggers pass." },
  scenarios: { eyebrow: "Three futures", title: "Conservative, base, accelerated", body: "Ranges propagate funding, adoption, compute, provider, and maturity assumptions without pretending to forecast certainty." },
  portfolio: { eyebrow: "Capital discipline", title: "Obligations before bets", body: "Regulatory, core, and evidence capabilities receive minimum allocations before growth bets and carrying-cost options." },
  capabilities: { eyebrow: "12 connected domains", title: "Bottlenecks are visible", body: "Maturity, prerequisites, sourcing, ownership, evidence, criticality, and single points of failure share one graph." },
  architecture: { eyebrow: "No big-bang rewrite", title: "Architecture follows workload evidence", body: "Start modular and managed. Extract only after adoption, isolation, reliability, economics, and operating-burden gates pass." },
  capital: { eyebrow: "FinOps-aware", title: "Every material number has a formula", body: "Ten cost pools reconcile to the scenario allocation; showback and sensitivity remain scenario hypotheses until real evidence exists." },
  risks: { eyebrow: "10 mandatory shocks", title: "Signals change decisions", body: "Hardware delay, lock-in, cost, security, adoption, partner, classical, funding, demand, and standards shocks produce traceable actions." },
  providers: { eyebrow: "Build / buy / partner", title: "Exit is designed before entry", body: "Scorecards include contract, data, residency, egress, reliability, skill, TCO, maturity, portability, and dual-source considerations." },
  governance: { eyebrow: "Three governed tracks", title: "PQC now, AI controlled, quantum gated", body: "Inventory, risk classification, human oversight, incident rollback, no-advantage reporting, and research-to-product handoff are explicit." },
  talent: { eyebrow: "T-shaped first", title: "Hire only after the gate", body: "Ownership, RACI, bus factor, partner capacity, learning plans, and on-call thresholds constrain organization design." },
  evidence: { eyebrow: "Immutable reasoning", title: "Decisions can be reconstructed", body: "The ledger records source date, confidence, contradictions, formulas, dissent, approvals, checksums, and next review." },
};

export function ControlTower({ data }: { data: RoadmapData }) {
  const [active, setActive] = useState("thesis");
  const [scenario, setScenario] = useState("base");
  const current = copy[active];
  const year1 = data.initiatives.filter((item) => item.horizon === "year_1");
  return (
    <main>
      <a className="skip" href="#decision-surface">Skip to decision surface</a>
      <header className="topbar">
        <div className="brand"><span className="mark" aria-hidden="true">Q</span><span>DecodeLabs / Strategy OS</span></div>
        <div className="status"><span className="pulse" aria-hidden="true" /> Local evidence only</div>
      </header>
      <div className="shell">
        <aside aria-label="Strategy Control Tower views">
          <p className="nav-label">CONTROL TOWER</p>
          <nav>{views.map(([id, label], index) => <button key={id} aria-current={active === id ? "page" : undefined} onClick={() => setActive(id)}><span>{String(index + 1).padStart(2, "0")}</span>{label}</button>)}</nav>
          <div className="revision"><small>FROZEN REVISION</small><strong>{data.revision}</strong><span>{data.as_of}</span></div>
        </aside>
        <section id="decision-surface" className="content" tabIndex={-1}>
          <div className="utility">
            <label>Scenario<select value={scenario} onChange={(event) => setScenario(event.target.value)}><option value="conservative">Conservative</option><option value="base">Base</option><option value="accelerated">Accelerated</option></select></label>
            <span className="candidate">{data.approval_status.replaceAll("_", " ")}</span>
          </div>
          <section className="hero" aria-live="polite">
            <p>{current.eyebrow}</p><h1>{current.title}</h1><p className="lede">{current.body}</p>
            <div className="metrics"><article><strong>{data.initiatives.length || 12}</strong><span>initiatives</span></article><article><strong>{data.capability_graph.nodes}</strong><span>capabilities</span></article><article><strong>10</strong><span>stress shocks</span></article><article><strong>0</strong><span>external actions</span></article></div>
          </section>
          <div className="grid">
            <section className="panel roadmap-panel"><div className="panel-head"><div><p>1 / 3 / 10</p><h2>Conditional roadmap</h2></div><span>{scenario} case</span></div>
              <div className="horizons"><article><b>YEAR 1 · COMMIT</b><h3>PQC + evidence wedge</h3><p>Secure, measurable value available now.</p></article><article><b>YEAR 3 · GATE</b><h3>Product to platform</h3><p>Scale only validated demand and economics.</p></article><article><b>YEAR 10 · OPTION</b><h3>Quantum maturity</h3><p>Exercise on resources, advantage, and TCO.</p></article></div>
            </section>
            <section className="panel"><div className="panel-head"><div><p>PORTFOLIO</p><h2>Year-1 commitments</h2></div><span>{year1.length || 6} bounded</span></div>
              <ul className="initiative-list">{(year1.length ? year1 : [{id:"pqc",name:"PQC Readiness Program",state:"COMMITTED",outcome:"Inventory 95% of cryptographic assets"},{id:"evidence",name:"Evidence and Governance Plane",state:"COMMITTED",outcome:"Every material claim has provenance"}]).slice(0,4).map((item) => <li key={item.id}><span><strong>{item.name}</strong><small>{item.outcome}</small></span><b>{item.state}</b></li>)}</ul>
            </section>
            <section className="panel"><div className="panel-head"><div><p>CRITICAL PATH</p><h2>Capability topology</h2></div><span>{data.capability_graph.edges} edges</span></div>
              <div className="nodes">{data.capability_graph.critical_path.map((node, index) => <span key={node} style={{"--i": index} as React.CSSProperties}>{node}</span>)}</div><p className="note">Acyclic by invariant · ownership and sourcing attached</p>
            </section>
          </div>
          <footer><span>No cloud, staffing, product, or financial side effects.</span><span>Next review: quarterly gate</span></footer>
        </section>
      </div>
    </main>
  );
}

