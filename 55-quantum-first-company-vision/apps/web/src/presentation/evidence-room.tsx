"use client";
import { useState } from "react";
import type { Entity, Room, Score } from "../domain/contracts";
import { useRoom } from "../application/use-room";

const surfaces = [
  "Thesis Overview",
  "Evidence Graph",
  "ICP & JTBD Atlas",
  "Opportunity Comparator",
  "Scenario & Sensitivity Lab",
  "Experiment Backlog",
  "Risk / Kill-Gate Register",
  "Product Sequence",
  "Decision Log",
  "Handoff Export",
];
const captions = [
  "A company thesis, open to challenge.",
  "Follow every decision back to its source.",
  "Know whose problem you are investigating.",
  "Three paths. Explicit trade-offs.",
  "What changes when your assumptions do?",
  "Turn uncertainty into a testable next step.",
  "Make the conditions for stopping visible.",
  "Earn the right to build the next product.",
  "A record of reasoning, including dissent.",
  "Portable evidence. A clear boundary.",
];
const money = (n: number) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(n);
const label = (s: string) => s.replaceAll("_", " ").replaceAll("-", " ");
function value(v: unknown): string {
  if (v === null) return "Unknown / not measured";
  if (Array.isArray(v)) return v.map(value).join(" · ");
  if (typeof v === "object")
    return Object.entries(v as Record<string, unknown>)
      .map(([k, x]) => `${label(k)}: ${value(x)}`)
      .join(" / ");
  return String(v);
}
function Mark({ small = false }: { small?: boolean }) {
  return (
    <svg
      className={small ? "mark small" : "mark"}
      viewBox="0 0 40 40"
      aria-hidden="true"
    >
      <path
        d="M8 10h23v23H8zM15 4h23v23M2 17h23v21"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
      />
      <circle cx="20" cy="21" r="3" fill="currentColor" />
    </svg>
  );
}
function Badge({
  children,
  tone = "",
}: {
  children: React.ReactNode;
  tone?: string;
}) {
  return <span className={`badge ${tone}`}>{children}</span>;
}
function Scores({ rows }: { rows: Score[] }) {
  return (
    <div className="score-list">
      {rows.map((s, i) => (
        <article className="score-row" key={s.id}>
          <span className="rank">0{i + 1}</span>
          <div className="score-main">
            <div className="score-heading">
              <h3>{s.name}</h3>
              <strong>
                {s.estimate.toFixed(1)}
                <small> / 100</small>
              </strong>
            </div>
            <div
              className="range-track"
              role="img"
              aria-label={`${s.name}: range ${s.low.toFixed(1)} to ${s.high.toFixed(1)}, estimate ${s.estimate.toFixed(1)}`}
            >
              <span
                style={{ left: `${s.low}%`, width: `${s.high - s.low}%` }}
              />
              <i style={{ left: `${s.estimate}%` }} />
            </div>
            <div className="range-caption">
              <span>
                Assumption interval {s.low.toFixed(1)}–{s.high.toFixed(1)}
              </span>
              <span>
                {Math.round(s.known_weight_fraction * 100)}% weighted coverage
              </span>
            </div>
          </div>
        </article>
      ))}
    </div>
  );
}
function EntityCards({
  items,
  room,
  onClaim,
}: {
  items: Entity[];
  room: Room;
  onClaim: (id: string) => void;
}) {
  return (
    <div className="entity-grid">
      {items.map((item) => (
        <article className="entity-card" key={item.id} id={item.id}>
          <div className="eyebrow">
            {label(item.entity_type)}{" "}
            <Badge tone={item.status === "hypothesis" ? "amber" : ""}>
              {item.status}
            </Badge>
          </div>
          <h3>{item.title}</h3>
          <p>{item.description}</p>
          {Object.keys(item.details).length > 0 && (
            <details>
              <summary>Inspect assumptions & conditions</summary>
              <dl>
                {Object.entries(item.details).map(([key, v]) => (
                  <div key={key}>
                    <dt>{label(key)}</dt>
                    <dd>{value(v)}</dd>
                  </div>
                ))}
              </dl>
            </details>
          )}
          {item.related_ids.length > 0 && (
            <p className="related">
              Related:{" "}
              {item.related_ids
                .map(
                  (id) =>
                    room.corpus.entities.find((e) => e.id === id)?.title ?? id,
                )
                .join(" · ")}
            </p>
          )}
          <div className="references">
            {item.claim_ids.map((id) => (
              <button
                onClick={() => onClaim(id)}
                key={id}
                title={room.corpus.claims.find((c) => c.id === id)?.text}
              >
                {id.replace("claim-", "↗ ")}
              </button>
            ))}
          </div>
        </article>
      ))}
    </div>
  );
}

export function EvidenceRoom() {
  const state = useRoom();
  const [surface, setSurface] = useState(0);
  const [menu, setMenu] = useState(false);
  const [search, setSearch] = useState("");
  const [stance, setStance] = useState("all");
  const [selectedClaim, setSelectedClaim] = useState("claim-cisa-1");
  const [scenario, setScenario] = useState("base");
  const [dimension, setDimension] = useState("competition");
  const [multiplier, setMultiplier] = useState(1);
  const [price, setPrice] = useState(12000);
  const [vertical, setVertical] = useState("all");
  const navigate = (index: number) => {
    setSurface(index);
    setMenu(false);
  };
  const inspect = (id: string) => {
    setSelectedClaim(id);
    navigate(1);
  };
  const { room } = state;
  const entities = (...kinds: string[]) =>
    room?.corpus.entities.filter((e) => kinds.includes(e.entity_type)) ?? [];
  const claim = room?.corpus.claims.find((c) => c.id === selectedClaim);
  const facts =
    room?.corpus.evidence.filter(
      (e) =>
        (stance === "all" || e.stance === stance) &&
        `${e.paraphrase} ${e.source_id}`
          .toLowerCase()
          .includes(search.toLowerCase()),
    ) ?? [];
  const economic = state.economics ?? room?.economics.base;

  return (
    <div className="shell">
      <a className="skip" href="#main">
        Skip to evidence
      </a>
      <button
        className="mobile-toggle"
        aria-expanded={menu}
        aria-controls="navigation"
        onClick={() => setMenu(!menu)}
      >
        ☰ Evidence Room
      </button>
      <aside
        id="navigation"
        className={`sidebar ${menu ? "open" : ""}`}
        aria-label="Evidence room navigation"
      >
        <div className="brand">
          <Mark />
          <div>
            QUANTUM-FIRST<span>Venture Evidence Room</span>
          </div>
        </div>
        <div className="workspace">
          <span className="workspace-icon">55</span>
          <div>
            Company vision<small>Plan 10 · Local workspace</small>
          </div>
          <span>⌄</span>
        </div>
        <p className="nav-label">RESEARCH WORKSPACE</p>
        <nav>
          {surfaces.map((name, i) => (
            <button
              key={name}
              aria-current={surface === i ? "page" : undefined}
              onClick={() => navigate(i)}
            >
              <span className="nav-number">
                {String(i + 1).padStart(2, "0")}
              </span>
              {name}
              {surface === i && <span className="nav-dot" />}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="live-dot" /> Local, read-only
          <div>
            Public evidence. Private decisions.
            <br />
            No customer data connected.
          </div>
        </div>
      </aside>
      <div className="workspace-main">
        <header className="topbar">
          <span>
            Plan 10 <b>/</b> Company vision <b>/</b> {surfaces[surface]}
          </span>
          <Badge>Research v1</Badge>
        </header>
        <main id="main" tabIndex={-1}>
          <div className="page-title">
            <div>
              <p className="eyebrow">VENTURE RESEARCH · WEEKS 222—223</p>
              <h1>{surfaces[surface]}</h1>
              <p>{captions[surface]}</p>
            </div>
            <a className="button secondary" href="/api/thesis" download>
              ↓ Thesis memo
            </a>
          </div>
          {state.error && (
            <div role="alert" className="error">
              <strong>Evidence could not be loaded.</strong>
              <p>{state.error}</p>
              <button onClick={state.retry}>Retry connection</button>
            </div>
          )}
          {!room && !state.error && (
            <div role="status" className="loading" aria-busy="true">
              Loading the local evidence register…
            </div>
          )}
          {room && (
            <>
              {surface === 0 && (
                <>
                  <div className="overview-grid">
                    <section className="thesis-panel">
                      <div className="eyebrow">
                        <span className="live-dot" /> WORKING THESIS{" "}
                        <Badge tone="dark">Provisional</Badge>
                      </div>
                      <h2>
                        Build on evidence.
                        <br />
                        <em>Keep the future open.</em>
                      </h2>
                      <p>
                        Start with postquantum readiness. Help security teams
                        understand their cryptographic dependencies before they
                        commit to migration.
                      </p>
                      <div className="thesis-actions">
                        <button onClick={() => navigate(3)}>
                          Explore the decision <span>↗</span>
                        </button>
                        <span>Value today. Optionality tomorrow.</span>
                      </div>
                      <div className="orbit" aria-hidden="true">
                        <span />
                        <span />
                        <span />
                      </div>
                    </section>
                    <section className="decision-panel">
                      <div className="eyebrow">
                        DECISION STATUS <span className="live-dot" />
                      </div>
                      <h2>
                        Proceed to
                        <br />
                        buyer discovery.
                      </h2>
                      <p>
                        A recommendation to test, with explicit conditions for
                        stopping.
                      </p>
                      <dl>
                        <div>
                          <dt>Primary archetype</dt>
                          <dd>Financial-services CISO</dd>
                        </div>
                        <div>
                          <dt>Initial offer</dt>
                          <dd>Scoped readiness assessment</dd>
                        </div>
                        <div>
                          <dt>Human approval</dt>
                          <dd>
                            <Badge tone="amber">Pending review</Badge>
                          </dd>
                        </div>
                      </dl>
                      <button
                        className="text-button"
                        onClick={() => navigate(8)}
                      >
                        Read the decision log ↗
                      </button>
                    </section>
                  </div>
                  <div className="metrics">
                    <article>
                      <span>PUBLIC EVIDENCE</span>
                      <strong>
                        {room.audit.evidence}
                        <small>records</small>
                      </strong>
                      <p>{room.audit.sources} primary source documents</p>
                    </article>
                    <article>
                      <span>CANDIDATE WEDGES</span>
                      <strong>
                        03<small>compared</small>
                      </strong>
                      <p>3 scenarios · 8 assumption stresses</p>
                    </article>
                    <article>
                      <span>BUYER VALIDATION</span>
                      <strong>
                        00<small>interviews</small>
                      </strong>
                      <p>15 interviews planned, none conducted</p>
                    </article>
                    <article>
                      <span>DECISION CONFIDENCE</span>
                      <strong className="word-metric">Provisional</strong>
                      <p>Budget and buyer access are unknown</p>
                    </article>
                  </div>
                  <div className="lower-grid">
                    <section className="panel">
                      <div className="section-heading">
                        <div>
                          <p className="eyebrow">OPPORTUNITY SIGNALS</p>
                          <h2>A comparison, with uncertainty.</h2>
                        </div>
                        <button
                          className="text-button"
                          onClick={() => navigate(4)}
                        >
                          Test assumptions ↗
                        </button>
                      </div>
                      <Scores rows={room.scores.base} />
                      <p className="footnote">
                        Ranges reflect analyst assumptions. Overlap prevents a
                        definitive market ranking.
                      </p>
                    </section>
                    <section className="panel question-panel">
                      <p className="eyebrow">THE COUNTERARGUMENT</p>
                      <h2>
                        What if buyers
                        <br />
                        already have enough?
                      </h2>
                      <p>
                        Existing libraries and cloud providers ship PQC
                        capabilities. Our proposed workflow must earn its place.
                      </p>
                      <button
                        className="quote-link"
                        onClick={() => inspect("claim-cloudflare-1")}
                      >
                        Cloudflare’s published capabilities <span>↗</span>
                      </button>
                      <button
                        className="quote-link"
                        onClick={() => inspect("claim-cisa-2")}
                      >
                        The limits of cryptographic discovery <span>↗</span>
                      </button>
                      <Badge tone="amber">
                        Contradictory evidence included
                      </Badge>
                    </section>
                  </div>
                </>
              )}
              {surface === 1 && (
                <>
                  <section className="panel lineage">
                    <p className="eyebrow">
                      LIVE TRACE · SELECT A RECORD BELOW
                    </p>
                    <div className="trace-line">
                      <span>
                        {room.decision.claim_ids.includes(selectedClaim)
                          ? "Decision"
                          : "Research context"}
                        <br />
                        <strong>
                          {room.decision.claim_ids.includes(selectedClaim)
                            ? "Provisional wedge"
                            : "Corpus record"}
                        </strong>
                      </span>
                      <b>→</b>
                      <span>
                        Claim
                        <br />
                        <strong>{selectedClaim}</strong>
                      </span>
                      <b>→</b>
                      <span>
                        Evidence
                        <br />
                        <strong>{claim?.supporting_evidence.join(", ")}</strong>
                      </span>
                      <b>→</b>
                      <span>
                        Source
                        <br />
                        <strong>{claim?.source_ids.join(", ")}</strong>
                      </span>
                    </div>
                    <p>{claim?.text}</p>
                    <Badge>
                      {claim?.confidence} · {claim?.kind}
                    </Badge>{" "}
                    <span className="muted">Review by {claim?.review_on}</span>
                  </section>
                  <div className="toolbar">
                    <label>
                      Search evidence
                      <input
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        placeholder="Search statements or publishers…"
                      />
                    </label>
                    <label>
                      Evidence stance
                      <select
                        aria-label="Evidence stance"
                        value={stance}
                        onChange={(e) => setStance(e.target.value)}
                      >
                        <option value="all">All evidence</option>
                        <option value="contradicts">
                          Contradicts the thesis
                        </option>
                        <option value="supports">Supports the thesis</option>
                        <option value="context">Context</option>
                      </select>
                    </label>
                    <span role="status">{facts.length} records</span>
                  </div>
                  {facts.length === 0 ? (
                    <div className="empty" role="status">
                      No matching evidence. Clear the search or change the
                      stance.
                    </div>
                  ) : (
                    <div className="evidence-table">
                      {facts.map((e) => {
                        const source = room.corpus.sources.find(
                          (s) => s.id === e.source_id,
                        )!;
                        return (
                          <article key={e.id}>
                            <div>
                              <Badge
                                tone={e.stance === "contradicts" ? "amber" : ""}
                              >
                                {e.stance}
                              </Badge>
                              <span className="evidence-id">{e.id}</span>
                            </div>
                            <button
                              className="claim-link"
                              onClick={() =>
                                setSelectedClaim(
                                  e.id.replace("evidence-", "claim-"),
                                )
                              }
                            >
                              {e.paraphrase}
                            </button>
                            <p>{e.limitations}</p>
                            <div className="source-line">
                              <a
                                href={source.url}
                                target="_blank"
                                rel="noreferrer"
                              >
                                {source.publisher} ↗
                              </a>
                              <span>
                                {e.locator} · accessed {source.accessed_on} ·{" "}
                                {e.confidence}
                              </span>
                            </div>
                          </article>
                        );
                      })}
                    </div>
                  )}
                </>
              )}
              {surface === 2 && (
                <>
                  <div className="notice">
                    Archetypes inferred from public evidence. No named or
                    interviewed customers.
                  </div>
                  <div className="toolbar">
                    <label>
                      Vertical
                      <select
                        aria-label="Vertical"
                        value={vertical}
                        onChange={(e) => setVertical(e.target.value)}
                      >
                        <option value="all">All four verticals</option>
                        {[
                          ...new Set(
                            entities("customer_profile").map((e) =>
                              String(e.details.vertical),
                            ),
                          ),
                        ].map((v) => (
                          <option key={v}>{v}</option>
                        ))}
                      </select>
                    </label>
                  </div>
                  <EntityCards
                    items={entities("customer_profile").filter(
                      (e) =>
                        vertical === "all" || e.details.vertical === vertical,
                    )}
                    room={room}
                    onClaim={inspect}
                  />
                  <h2 className="subheading">Jobs to be done</h2>
                  <EntityCards
                    items={entities("job_to_be_done")}
                    room={room}
                    onClaim={inspect}
                  />
                  <h2 className="subheading">
                    Buying patterns & current workflow hypotheses
                  </h2>
                  <EntityCards
                    items={entities(
                      "buying_pattern",
                      "workflow",
                      "pain",
                      "inaction",
                    )}
                    room={room}
                    onClaim={inspect}
                  />
                </>
              )}
              {surface === 3 && (
                <>
                  <section className="panel">
                    <Scores rows={room.scores.base} />
                  </section>
                  <div className="entity-grid">
                    {room.corpus.opportunities.map((o) => (
                      <article className="entity-card" key={o.id}>
                        <Badge tone="amber">Offer hypothesis</Badge>
                        <h2>{o.name}</h2>
                        <p>{o.promise}</p>
                        <dl>
                          <div>
                            <dt>Classical alternative</dt>
                            <dd>{o.classical_alternative}</dd>
                          </div>
                          <div>
                            <dt>Maturity gate</dt>
                            <dd>{o.maturity_condition}</dd>
                          </div>
                          <div>
                            <dt>Kill gate</dt>
                            <dd>{o.kill_gate}</dd>
                          </div>
                        </dl>
                        <div className="references">
                          {[...o.claim_ids, ...o.opposing_claim_ids].map(
                            (id) => (
                              <button key={id} onClick={() => inspect(id)}>
                                {id}
                              </button>
                            ),
                          )}
                        </div>
                      </article>
                    ))}
                  </div>
                  <h2 className="subheading">
                    14 dimensions · versioned weights
                  </h2>
                  <div className="table-scroll">
                    <table>
                      <thead>
                        <tr>
                          <th>Dimension</th>
                          <th>Weight / direction</th>
                          {room.corpus.opportunities.map((o) => (
                            <th key={o.id}>{o.name}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {room.protocol.dimensions.map((d) => (
                          <tr key={d.id}>
                            <th>{d.label}</th>
                            <td>
                              {d.weight} / {d.direction}
                            </td>
                            {room.corpus.opportunities.map((o) => (
                              <td key={o.id}>
                                <details>
                                  <summary>
                                    {o.dimensions[d.id]
                                      ? `${o.dimensions[d.id]!.low}–${o.dimensions[d.id]!.high}`
                                      : "Unknown [0–5]"}
                                  </summary>
                                  <p>{o.rationale[d.id]}</p>
                                </details>
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <h2 className="subheading">Existing alternatives</h2>
                  <EntityCards
                    items={entities("competitor", "alternative")}
                    room={room}
                    onClaim={inspect}
                  />
                </>
              )}
              {surface === 4 && (
                <>
                  <div className="notice">
                    All economics are illustrative hypotheses. Organization
                    counts, prices and delivery effort are not market
                    measurements.
                  </div>
                  <form
                    className="panel scenario-form"
                    onSubmit={(e) => {
                      e.preventDefault();
                      void state.calculate(
                        scenario,
                        dimension,
                        multiplier,
                        price,
                      );
                    }}
                  >
                    <label>
                      Scenario
                      <select
                        aria-label="Scenario"
                        value={scenario}
                        onChange={(e) => setScenario(e.target.value)}
                      >
                        {["conservative", "base", "aggressive"].map((s) => (
                          <option key={s}>{s}</option>
                        ))}
                      </select>
                    </label>
                    <label>
                      Dimension
                      <select
                        aria-label="Dimension"
                        value={dimension}
                        onChange={(e) => setDimension(e.target.value)}
                      >
                        {room.protocol.dimensions.map((d) => (
                          <option value={d.id} key={d.id}>
                            {d.label}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label>
                      Weight multiplier · {multiplier.toFixed(1)}×
                      <input
                        type="range"
                        min="0.1"
                        max="5"
                        step="0.1"
                        value={multiplier}
                        onChange={(e) => setMultiplier(Number(e.target.value))}
                      />
                    </label>
                    <label>
                      Illustrative annual price (USD)
                      <input
                        type="number"
                        min="1"
                        max="1000000"
                        required
                        value={price}
                        onChange={(e) => setPrice(Number(e.target.value))}
                      />
                    </label>
                    <button className="button" disabled={state.busy}>
                      {state.busy ? "Recalculating…" : "Recalculate scenario"}
                    </button>
                  </form>
                  <section className="panel" aria-busy={state.busy}>
                    <Scores rows={state.scores ?? room.scores.base} />
                    <p role="status" className="footnote">
                      {state.scores
                        ? "Scenario recalculated by local API."
                        : "Showing baseline assumptions."}
                    </p>
                  </section>
                  <div className="metrics economics">
                    {economic &&
                      Object.entries({
                        "Illustrative TAM": economic.tam,
                        "Illustrative SAM": economic.sam,
                        "Capacity-capped SOM": economic.som,
                      }).map(([name, n]) => (
                        <article key={name}>
                          <span>{name}</span>
                          <strong>{money(n)}</strong>
                          <p>
                            Hypothetical annual scope · not observed market size
                          </p>
                        </article>
                      ))}
                  </div>
                  <section className="panel">
                    <h2>Inspect the arithmetic</h2>
                    <p>
                      Default assumptions: 250 organizations × 20% serviceable ×
                      10% obtainable; capacity at 6 customers. 80 delivery hours
                      × USD 60/hour + USD 500 tools.
                    </p>
                    <p>
                      Modeled gross margin:{" "}
                      {economic && (economic.gross_margin * 100).toFixed(1)}%.{" "}
                      {economic?.exclusions}.
                    </p>
                    <dl>
                      {economic &&
                        Object.entries(economic.formulas).map(([key, text]) => (
                          <div key={key}>
                            <dt>{key}</dt>
                            <dd>
                              <code>{text}</code>
                            </dd>
                          </div>
                        ))}
                    </dl>
                  </section>
                  <h2 className="subheading">
                    Conservative ↔ aggressive economics range
                  </h2>
                  <div className="entity-grid">
                    {Object.entries(room.economics).map(([key, e]) => (
                      <article className="entity-card" key={key}>
                        <Badge tone="amber">{key} hypothesis</Badge>
                        <h3>{money(e.som)} obtainable annual scope</h3>
                        <p>
                          Modeled margin {(e.gross_margin * 100).toFixed(1)}% ·
                          delivery {money(e.delivery_cost_per_customer)} per
                          customer
                        </p>
                      </article>
                    ))}
                  </div>
                  <h2 className="subheading">Eight assumption stresses</h2>
                  <div className="entity-grid">
                    {room.sensitivity.stress_cases.map((c) => (
                      <article key={c.id} className="entity-card">
                        <h3>{c.title}</h3>
                        <p>Highest scenario estimate: {c.scores[0].name}</p>
                        <Badge tone="amber">Intervals may overlap</Badge>
                      </article>
                    ))}
                  </div>
                  <h2 className="subheading">Pricing hypotheses</h2>
                  <EntityCards
                    items={entities("pricing", "assumption")}
                    room={room}
                    onClaim={inspect}
                  />
                </>
              )}
              {surface === 5 && (
                <>
                  <div className="notice">
                    Planned experiments. No interview, outreach, purchase or
                    pilot has been executed.
                  </div>
                  <EntityCards
                    items={entities("experiment", "interview_plan")}
                    room={room}
                    onClaim={inspect}
                  />
                  <h2 className="subheading">
                    24 non-leading discovery questions
                  </h2>
                  <ol className="question-list">
                    {entities("discovery_question").map((e) => (
                      <li key={e.id}>{e.title}</li>
                    ))}
                  </ol>
                </>
              )}
              {surface === 6 && (
                <>
                  <EntityCards
                    items={entities("risk", "capability")}
                    room={room}
                    onClaim={inspect}
                  />
                  <h2 className="subheading">
                    Procurement, security & legal objections
                  </h2>
                  <EntityCards
                    items={entities("objection")}
                    room={room}
                    onClaim={inspect}
                  />
                </>
              )}
              {surface === 7 && (
                <>
                  <div className="notice">
                    Conditional sequence. Progress depends on evidence gates;
                    dates are planning horizons.
                  </div>
                  <div className="product-timeline">
                    {entities("product_stage").map((e, i) => (
                      <article key={e.id}>
                        <span className="timeline-step">0{i + 1}</span>
                        <p className="eyebrow">
                          {value(e.details.months)} MONTHS
                        </p>
                        <h2>{e.title}</h2>
                        <p>{String(e.details.gate)}</p>
                        <dl>
                          <div>
                            <dt>Build</dt>
                            <dd>{String(e.details.build)}</dd>
                          </div>
                          <div>
                            <dt>Buy / partner</dt>
                            <dd>{String(e.details.buy_partner)}</dd>
                          </div>
                        </dl>
                      </article>
                    ))}
                  </div>
                  <h2 className="subheading">Assets that could compound</h2>
                  <EntityCards
                    items={entities("moat")}
                    room={room}
                    onClaim={inspect}
                  />
                </>
              )}
              {surface === 8 && (
                <>
                  <div className="notice">
                    Analyst recommendation awaiting human review. Challenge
                    responses are self-review, not independent validation.
                  </div>
                  <EntityCards
                    items={entities("decision", "trace")}
                    room={room}
                    onClaim={inspect}
                  />
                  <h2 className="subheading">24 hostile questions</h2>
                  <div className="challenge-list">
                    {entities("challenge").map((e, i) => (
                      <details key={e.id}>
                        <summary>
                          <span>{String(i + 1).padStart(2, "0")}</span>
                          {e.title}
                        </summary>
                        <p>{e.description}</p>
                      </details>
                    ))}
                  </div>
                </>
              )}
              {surface === 9 && (
                <>
                  <section className="panel export-panel">
                    <Mark />
                    <p className="eyebrow">VERSIONED CONTRACT</p>
                    <h2>company-vision-v1</h2>
                    <p>
                      Thesis, decision, ICP/JTBD, product sequence, assumptions,
                      evidence, experiments, risks, glossary, schemas and
                      SHA-256 checksums.
                    </p>
                    <Badge tone="amber">
                      Candidate · human approval pending
                    </Badge>
                    <div className="export-actions">
                      <a className="button" href="/api/handoff" download>
                        ↓ Download candidate bundle
                      </a>
                      <a
                        className="button secondary"
                        href="/api/thesis"
                        download
                      >
                        ↓ Read thesis memo
                      </a>
                    </div>
                    <p className="footnote">
                      The recipient implements only what its own project map
                      authorizes. No shared code, databases, credentials or
                      execution state.
                    </p>
                  </section>
                  <EntityCards
                    items={entities("handoff_contract")}
                    room={room}
                    onClaim={inspect}
                  />
                </>
              )}
              <footer>
                <span>
                  <Mark small /> Quantum-First Venture Evidence Room
                </span>
                <span>
                  Public sources reviewed {room.corpus.research_date} · Local
                  decision support
                </span>
              </footer>
            </>
          )}
        </main>
      </div>
    </div>
  );
}
