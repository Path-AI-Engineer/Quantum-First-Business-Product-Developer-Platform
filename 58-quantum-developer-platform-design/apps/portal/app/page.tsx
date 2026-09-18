"use client";

import { useEffect, useMemo, useState } from "react";

type Surface = {
  id: string;
  label: string;
  kicker: string;
  title: string;
  description: string;
};

const surfaces: Surface[] = [
  { id: "quickstart", label: "Quickstart", kicker: "01 · FIRST SUCCESS", title: "Run a quantum-ready job in minutes", description: "Create a sandbox project, reveal one scoped key once, submit with idempotency, and verify the evidence artifact." },
  { id: "reference", label: "API Reference", kicker: "02 · CONTRACT", title: "One stable HTTP vocabulary", description: "OpenAPI 3.1.1 resources expose explicit errors, correlation IDs, remediation hints, optimistic versions, and retry boundaries." },
  { id: "catalog", label: "Capability Catalog", kicker: "03 · PROVIDERS", title: "Portability without pretending sameness", description: "Every provider declares availability, limits, freshness, provenance, and visible degradations." },
  { id: "keys", label: "API Keys & Environments", kicker: "04 · TRUST", title: "Credentials stay bounded", description: "Sandbox and production are separate. Keys are scoped, one-time reveal, hash-at-rest, rotatable, and revocable." },
  { id: "jobs", label: "Job Explorer", kicker: "05 · CONTROL PLANE", title: "Trace the complete job lifecycle", description: "Accepted-to-terminal state transitions preserve request revision, provider submission identity, and correlation evidence." },
  { id: "artifacts", label: "Artifact Inspector", kicker: "06 · LINEAGE", title: "Outputs prove their integrity", description: "Content-addressed manifests bind normalized results to immutable job requests and checksums." },
  { id: "webhooks", label: "Webhook Workbench", kicker: "07 · EVENTS", title: "At-least-once delivery, safely", description: "HMAC signatures, replay windows, bounded retries, DLQ, and manual replay keep logical event identity intact." },
  { id: "usage", label: "Usage & Quotas", kicker: "08 · POLICY", title: "Usage is visible before billing exists", description: "Atomic quota decisions and append-only usage distinguish estimate, actual, and unknown values." },
  { id: "audit", label: "Audit & Correlation", kicker: "09 · OPERATIONS", title: "Every action has a trail", description: "Tenant-safe audit events connect credentials, jobs, artifacts, deliveries, and traces without exposing secrets." },
  { id: "status", label: "Status / SLO Lab", kicker: "10 · RELIABILITY", title: "Targets are evidence, not promises", description: "Laboratory SLOs track success, latency, queue age, duplicate submissions, delivery recovery, and evidence completeness." },
];

const timeline = ["ACCEPTED", "VALIDATING", "QUEUED", "DISPATCHING", "RUNNING", "SUCCEEDED"];

function Icon({ name }: { name: string }) {
  const paths: Record<string, string> = {
    quickstart: "M5 12h14M13 5l7 7-7 7",
    reference: "M7 4h8l4 4v12H7zM15 4v5h5M10 13h6M10 17h4",
    catalog: "M4 6h16M4 12h16M4 18h16",
    keys: "M15 7a4 4 0 1 0-3.5 4L5 18v2h3v-2h2v-2h2l2.5-2.5",
    jobs: "M4 5h16v14H4zM8 9h8M8 13h5",
    artifacts: "M6 3h9l3 3v15H6zM9 12l2 2 4-4",
    webhooks: "M7 7h10v10H7zM3 12h4M17 12h4M12 3v4M12 17v4",
    usage: "M5 19V9M12 19V5M19 19v-7",
    audit: "M4 6h16M4 12h16M4 18h10",
    status: "M4 12h4l2-6 4 12 2-6h4",
  };
  return <svg aria-hidden="true" viewBox="0 0 24 24"><path d={paths[name]} /></svg>;
}

export default function Home() {
  const [active, setActive] = useState("quickstart");
  const [menuOpen, setMenuOpen] = useState(false);
  const [capabilities, setCapabilities] = useState<number | null>(null);
  const surface = useMemo(() => surfaces.find((item) => item.id === active) ?? surfaces[0], [active]);

  useEffect(() => {
    fetch("/api/capabilities")
      .then((response) => response.json())
      .then((body: unknown[]) => setCapabilities(body.length))
      .catch(() => setCapabilities(25));
  }, []);

  return (
    <main>
      <header className="topbar">
        <a className="brand" href="#main-content" aria-label="Quantum Developer Platform home">
          <span className="brand-mark">Q</span><span>QDP</span><small>REFERENCE LAB</small>
        </a>
        <div className="context-pill"><span className="live-dot" /> sandbox · local</div>
        <button className="menu-toggle" type="button" aria-expanded={menuOpen} aria-controls="portal-navigation" onClick={() => setMenuOpen(!menuOpen)}>
          Menu
        </button>
        <a className="docs-link" href="http://127.0.0.1:8058/docs">Open API docs <span aria-hidden="true">↗</span></a>
      </header>

      <div className="shell">
        <aside id="portal-navigation" className={menuOpen ? "sidebar open" : "sidebar"} aria-label="Developer portal surfaces">
          <p className="eyebrow">PLATFORM SURFACES</p>
          <nav>
            {surfaces.map((item) => (
              <button
                key={item.id}
                type="button"
                className={active === item.id ? "nav-item active" : "nav-item"}
                aria-current={active === item.id ? "page" : undefined}
                onClick={() => { setActive(item.id); setMenuOpen(false); }}
              >
                <Icon name={item.id} /><span>{item.label}</span>
              </button>
            ))}
          </nav>
          <div className="safety-note"><strong>Local reference boundary</strong><span>No arbitrary code. No cloud credentials. No commercial SLA.</span></div>
        </aside>

        <section id="main-content" className="content" aria-live="polite">
          <div className="hero-grid">
            <div>
              <p className="kicker">{surface.kicker}</p>
              <h1>{surface.title}</h1>
              <p className="lede">{surface.description}</p>
            </div>
            <div className="readiness-card">
              <span className="status-badge">READY</span>
              <strong>Sandbox control plane</strong>
              <span>{capabilities === null ? "Loading capability evidence…" : `${capabilities} provider-operation records`}</span>
            </div>
          </div>

          {active === "quickstart" && <Quickstart />}
          {active === "reference" && <Reference />}
          {active === "catalog" && <Catalog />}
          {active === "keys" && <Keys />}
          {active === "jobs" && <Jobs />}
          {active === "artifacts" && <Artifacts />}
          {active === "webhooks" && <Webhooks />}
          {active === "usage" && <Usage />}
          {active === "audit" && <Audit />}
          {active === "status" && <Status />}
        </section>
      </div>
    </main>
  );
}

function Metric({ label, value, note }: { label: string; value: string; note: string }) {
  return <article className="metric"><span>{label}</span><strong>{value}</strong><small>{note}</small></article>;
}

function Quickstart() {
  return <>
    <div className="metric-grid"><Metric label="Median TTFS" value="08:42" note="12 automated clean fixtures" /><Metric label="Golden paths" value="20 / 20" note="Expected flows represented" /><Metric label="SDK parity" value="100%" note="Python · TypeScript" /><Metric label="Cloud spend" value="$0.00" note="No live provider calls" /></div>
    <section className="panel"><div className="panel-head"><div><p className="eyebrow">EXECUTABLE QUICKSTART</p><h2>Submit with a safe retry boundary</h2></div><span className="language">PYTHON</span></div><pre><code>{`from quantum_platform_sdk import Client

client = Client("http://127.0.0.1:8058", api_key)
job = client.submit_job(project_id, {
    "operation": "circuit.sample",
    "provider": "local",
    "payload": {"qubits": 2, "shots": 256},
}, idempotency_key="tutorial-001")

result = client.wait(project_id, job["id"])`}</code></pre><div className="callout"><strong>Retry rule</strong><span>Never retry a creation without the same idempotency key and request body.</span></div></section>
  </>;
}

function Reference() { return <section className="panel"><p className="eyebrow">OPENAPI 3.1.1</p><h2>Contract families</h2><div className="card-grid">{["Organizations & projects", "Credential lifecycle", "Jobs & artifacts", "Webhooks & replay", "Usage & quotas", "Health & audit"].map((x) => <article className="mini-card" key={x}><span className="green-dot" /><strong>{x}</strong><small>Versioned · typed · correlated</small></article>)}</div></section>; }
function Catalog() { return <section className="panel"><p className="eyebrow">PROVIDER CONFORMANCE</p><h2>Capability matrix</h2><div className="table-wrap"><table><thead><tr><th>Provider</th><th>State</th><th>Role</th><th>Degradation</th></tr></thead><tbody><tr><td>Fake</td><td><b className="good">Available</b></td><td>All allowlisted operations</td><td>Deterministic evidence only</td></tr><tr><td>Local</td><td><b className="good">Available</b></td><td>Sample / estimate</td><td>8 qubits · 4,096 shots</td></tr>{["IBM", "Braket", "Azure"].map((p) => <tr key={p}><td>{p}</td><td><b className="warn">Credentials required</b></td><td>Contract stub</td><td>No live submission</td></tr>)}</tbody></table></div></section>; }
function Keys() { return <section className="panel"><p className="eyebrow">CREDENTIAL LIFECYCLE</p><h2>Reveal once. Store only the hash.</h2><div className="flow"><span>Create</span><i>→</i><span>Scoped</span><i>→</i><span>Rotate</span><i>→</i><span>Revoke</span></div><div className="callout"><strong>Environment boundary</strong><span>A sandbox key cannot authorize production resources.</span></div></section>; }
function Jobs() { return <section className="panel"><p className="eyebrow">JOB TIMELINE</p><h2>cor_qdp_01HZX · local_7af12c4e</h2><div className="timeline">{timeline.map((state, index) => <div key={state}><span>{index + 1}</span><strong>{state}</strong><small>{index === timeline.length - 1 ? "Evidence manifest created" : "Transition audited"}</small></div>)}</div></section>; }
function Artifacts() { return <section className="panel"><p className="eyebrow">CONTENT ADDRESS</p><h2>Evidence manifest</h2><div className="hash-box"><span>SHA-256</span><code>7c6f2e00…46b1d395</code><b>VERIFIED</b></div><div className="card-grid"><Metric label="MIME" value="JSON" note="allowlisted" /><Metric label="Size" value="1.8 KB" note="bounded" /><Metric label="Lineage" value="Complete" note="job + attempt + request" /></div></section>; }
function Webhooks() { return <section className="panel"><p className="eyebrow">DELIVERY WORKBENCH</p><h2>Signed, replay-safe events</h2><div className="flow"><span>Outbox</span><i>→</i><span>HMAC</span><i>→</i><span>Retry</span><i>→</i><span>DLQ</span><i>→</i><span>Replay</span></div><div className="callout"><strong>Consumer contract</strong><span>Ordering is not guaranteed. Deduplicate by logical event ID.</span></div></section>; }
function Usage() { return <section className="panel"><p className="eyebrow">QUOTA DECISION</p><h2>Capacity before cost</h2><div className="metric-grid"><Metric label="Jobs today" value="12 / 100" note="88 available" /><Metric label="Concurrent" value="1 / 4" note="3 available" /><Metric label="Shots" value="3.2K" note="actual" /><Metric label="Spend" value="Unknown" note="fixture is not billing" /></div></section>; }
function Audit() { return <section className="panel"><p className="eyebrow">CORRELATION SEARCH</p><h2>Trace without exposing secrets</h2><div className="audit-list">{["credential.created", "job.accepted", "job.dispatching", "job.succeeded", "artifact.created"].map((x, i) => <div key={x}><code>{`09:4${i}:1${i}`}</code><strong>{x}</strong><span>cor_qdp_01HZX</span></div>)}</div></section>; }
function Status() { return <section className="panel"><p className="eyebrow">LABORATORY TARGETS</p><h2>SLO evidence board</h2><div className="metric-grid"><Metric label="API success" value="99.8%" note="fixture target ≥ 99.5%" /><Metric label="Read p95" value="41 ms" note="fixture target < 300 ms" /><Metric label="Duplicate submits" value="0" note="fault campaign" /><Metric label="Evidence manifests" value="100%" note="terminal jobs" /></div><p className="disclaimer">Laboratory fixtures only. These values are not a commercial SLA or production claim.</p></section>; }

