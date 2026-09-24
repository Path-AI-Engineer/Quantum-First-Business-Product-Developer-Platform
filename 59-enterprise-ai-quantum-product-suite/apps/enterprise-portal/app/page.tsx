"use client";

import { useMemo, useState } from "react";

const surfaces = [
  ["Enterprise Portfolio", "Command view for exposure, opportunity, gates, and evidence."],
  ["Crypto Readiness", "Synthetic inventory, findings, and proposed migration waves."],
  ["Optimization Opportunities", "Baseline-first assessments with value hypotheses."],
  ["Quantum Workbench", "Approved local sandbox jobs and reproducible artifacts."],
  ["Evidence Graph", "Source-to-decision lineage with confidence and provenance."],
  ["Risks & Decisions", "Human-owned choices separated from recommendations."],
  ["Approvals & Policies", "Revision-bound, expiring, replay-resistant approvals."],
  ["Catalog & Capabilities", "Standalone modules, owners, standards, and lifecycle."],
  ["Usage, Cost & Quotas", "Transparent synthetic showback; no realized ROI claim."],
  ["Audit, Reports & Support", "Tenant-safe correlation, assurance, and runbooks."],
] as const;

const modules = [
  { name: "Crypto readiness", value: "18 open findings", tone: "cyan" },
  { name: "Optimization studio", value: "12 candidates", tone: "purple" },
  { name: "Quantum workbench", value: "9 local templates", tone: "magenta" },
  { name: "Shared governance", value: "240 auth checks", tone: "green" },
] as const;

export default function Home() {
  const [active, setActive] = useState(0);
  const [tenant, setTenant] = useState("Meridian Financial Group");
  const evidence = useMemo(() => 60 + active * 3, [active]);
  return (
    <main>
      <aside aria-label="Enterprise suite surfaces">
        <div className="brand"><span>EQ</span><div><strong>Intelligence Suite</strong><small>technical candidate</small></div></div>
        <nav>{surfaces.map(([name], index) => (
          <button key={name} aria-current={active === index ? "page" : undefined} onClick={() => setActive(index)}>
            <span>{String(index + 1).padStart(2, "0")}</span>{name}
          </button>
        ))}</nav>
        <div className="boundary"><strong>CONTROL BOUNDARY</strong><p>Local sandbox only. Human approval required. Synthetic tenants.</p></div>
      </aside>
      <section className="workspace">
        <header>
          <div><p className="eyebrow">ENTERPRISE QUANTUM INTELLIGENCE</p><h1>{surfaces[active][0]}</h1><p>{surfaces[active][1]}</p></div>
          <label>Tenant<select value={tenant} onChange={(event) => setTenant(event.target.value)}>
            <option>Meridian Financial Group</option><option>Atlas Health Network</option><option>Northport Manufacturing</option>
          </select></label>
        </header>
        <div className="notice" role="status"><span>TECHNICAL CANDIDATE</span> External contract approval and executive portfolio decisions remain pending.</div>
        <section className="metrics" aria-label="Portfolio metrics">
          <article><small>EVIDENCE</small><strong>{evidence}</strong><em>tenant-scoped records</em></article>
          <article><small>DECISION GATES</small><strong>12</strong><em>human owned</em></article>
          <article><small>AUTHORIZATION</small><strong>240/240</strong><em>synthetic checks</em></article>
          <article><small>REALIZED ROI</small><strong>—</strong><em>hypothesis only</em></article>
        </section>
        <section className="module-grid">
          {modules.map((module) => <article className={`module ${module.tone}`} key={module.name}>
            <div className="module-top"><span></span><small>STANDALONE PATH</small></div><h2>{module.name}</h2><strong>{module.value}</strong>
            <p>Evidence linked · owner assigned · policy enforced</p><button>Inspect evidence <span aria-hidden="true">↗</span></button>
          </article>)}
        </section>
        <section className="flow" aria-labelledby="flow-title"><div><p className="eyebrow">DECISION LINEAGE</p><h2 id="flow-title">Recommendation is not authorization</h2></div>
          <ol><li><span>01</span><strong>Evidence</strong><small>verified source</small></li><li><span>02</span><strong>Risk</strong><small>confidence stated</small></li><li><span>03</span><strong>Recommendation</strong><small>owner required</small></li><li><span>04</span><strong>Approval</strong><small>scope + expiry</small></li><li><span>05</span><strong>Decision</strong><small>human recorded</small></li></ol>
        </section>
        <footer><span>687 evaluation cases · 3 synthetic tenants · 0 external provider actions</span><a href="/docs">API contract</a></footer>
      </section>
    </main>
  );
}

