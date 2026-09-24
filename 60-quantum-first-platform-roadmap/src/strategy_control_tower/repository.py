"""Canonical synthetic strategy fixture with explicit provenance."""

from __future__ import annotations

from .models import (
    Capability,
    CostRange,
    Evidence,
    Gate,
    Horizon,
    Initiative,
    InitiativeState,
    Maturity,
    Scenario,
    Shock,
    StrategicClass,
    StrategyRepository,
)

CAPABILITY_NAMES = (
    "Product discovery",
    "PQC and crypto agility",
    "Optimization science",
    "Quantum software and algorithms",
    "Developer platform",
    "Enterprise IAM and security",
    "Data, evidence, and AI governance",
    "Cloud and platform engineering",
    "SRE and FinOps",
    "Sales, pilots, and customer success",
    "Legal, procurement, and partnerships",
    "Research and talent",
)

INITIATIVES = (
    (
        "pqc-readiness",
        "PQC Readiness Program",
        Horizon.YEAR_1,
        StrategicClass.REGULATORY,
        115,
        145,
        190,
        1.5,
        "Inventory 95% of cryptographic assets",
        None,
    ),
    (
        "optimization-assessment",
        "Optimization Assessment",
        Horizon.YEAR_1,
        StrategicClass.CORE,
        90,
        120,
        165,
        1.5,
        "Complete five evidence-backed assessments",
        "Best validated classical solver",
    ),
    (
        "developer-sandbox",
        "Developer Platform Sandbox",
        Horizon.YEAR_1,
        StrategicClass.ENABLER,
        105,
        140,
        185,
        2.0,
        "Three authorized workflows complete",
        None,
    ),
    (
        "evidence-plane",
        "Evidence and Governance Plane",
        Horizon.YEAR_1,
        StrategicClass.CORE,
        85,
        110,
        145,
        1.5,
        "Every material claim has provenance",
        None,
    ),
    (
        "enterprise-controls",
        "Enterprise IAM and Audit Controls",
        Horizon.YEAR_1,
        StrategicClass.REGULATORY,
        100,
        135,
        180,
        1.5,
        "Tenant and approval isolation verified",
        None,
    ),
    (
        "finops-observability",
        "FinOps and Observability Baseline",
        Horizon.YEAR_1,
        StrategicClass.ENABLER,
        70,
        95,
        130,
        1.0,
        "Showback reconciles to canonical cost",
        None,
    ),
    (
        "enterprise-suite",
        "Enterprise Product Suite",
        Horizon.YEAR_3,
        StrategicClass.GROWTH,
        160,
        225,
        320,
        3.0,
        "Retention and unit economics gates pass",
        None,
    ),
    (
        "partner-integrations",
        "Provider and Partner Integrations",
        Horizon.YEAR_3,
        StrategicClass.GROWTH,
        120,
        175,
        245,
        2.0,
        "Two exit-tested provider adapters",
        None,
    ),
    (
        "platform-extraction",
        "Conditional Platform Extraction",
        Horizon.YEAR_3,
        StrategicClass.OPTION,
        150,
        210,
        300,
        2.5,
        "Scale threshold justifies extraction",
        None,
    ),
    (
        "quantum-optimization",
        "Quantum Optimization Option",
        Horizon.YEAR_10,
        StrategicClass.OPTION,
        80,
        120,
        190,
        1.0,
        "Resource and economics gate beats baseline",
        "Best validated classical solver",
    ),
    (
        "quantum-ml",
        "Quantum ML Research Option",
        Horizon.YEAR_10,
        StrategicClass.WATCH,
        55,
        85,
        135,
        0.5,
        "Repeatable advantage signal survives review",
        "Best validated classical and AI model",
    ),
    (
        "sovereign-ecosystem",
        "Sovereign and Ecosystem Option",
        Horizon.YEAR_10,
        StrategicClass.OPTION,
        60,
        95,
        155,
        0.5,
        "Residency demand and economics justify exercise",
        None,
    ),
)


def _capabilities() -> tuple[Capability, ...]:
    return tuple(
        Capability(
            id=f"cap-{index + 1:02d}",
            name=name,
            current=Maturity.EMERGING if index < 8 else Maturity.ABSENT,
            target=Maturity.MANAGED if index < 8 else Maturity.REPEATABLE,
            prerequisites=() if index < 2 else (f"cap-{index:02d}",),
            owner=f"capability-owner-{index + 1:02d}",
            sourcing=("build" if index % 3 == 0 else "buy" if index % 3 == 1 else "partner"),
            evidence=f"evidence-{(index % 6) + 1:02d}",
            bottleneck_weight=round(0.35 + index * 0.04, 2),
        )
        for index, name in enumerate(CAPABILITY_NAMES)
    )


def _initiatives() -> tuple[Initiative, ...]:
    items: list[Initiative] = []
    for index, (identifier, name, horizon, category, minimum, expected, maximum, people, outcome, baseline) in enumerate(INITIATIVES):
        dependency = "foundation" if index < 3 else INITIATIVES[index - 3][0]
        items.append(
            Initiative(
                id=identifier,
                name=name,
                horizon=horizon,
                state=InitiativeState.COMMITTED if horizon is Horizon.YEAR_1 else InitiativeState.CANDIDATE,
                strategic_class=category,
                outcome=outcome,
                owner=f"initiative-owner-{index + 1:02d}",
                target_user="authorized enterprise decision maker",
                metrics=("evidence_coverage", "gate_pass_rate"),
                dependencies=(dependency,),
                capability_ids=(f"cap-{(index % 12) + 1:02d}",),
                cost=CostRange(minimum=minimum * 1000, expected=expected * 1000, maximum=maximum * 1000),
                headcount_min=people,
                headcount_max=people + 1.5,
                gate_ids=(f"gate-{(index % 6) + 1:02d}",),
                reversible=index not in {4, 6},
                classical_baseline=baseline,
                kill_condition="Kill or hold when the named outcome misses two consecutive reviews",
                exit_plan="Export evidence and contracts, revoke access, and retain provider-neutral records",
            )
        )
    return tuple(items)


def build_repository() -> StrategyRepository:
    gate_specs = (
        ("Evidence completeness", "evidence_coverage", 0.95, "strategy"),
        ("Security readiness", "control_coverage", 0.90, "security"),
        ("Adoption validity", "adoption_index", 0.60, "product"),
        ("Economic viability", "margin_index", 0.20, "finance"),
        ("Reliability", "slo_attainment", 0.99, "platform"),
        ("Quantum maturity", "advantage_confidence", 0.80, "research"),
    )
    gates = tuple(
        Gate(id=f"gate-{i:02d}", name=n, metric=m, threshold=t, owner=o, cadence="quarterly")
        for i, (n, m, t, o) in enumerate(gate_specs, 1)
    )
    scenarios = (
        Scenario(
            id="conservative",
            name="Conservative",
            budget=780_000,
            headcount=9,
            adoption_multiplier=0.55,
            compute_multiplier=1.45,
            confidence="medium",
        ),
        Scenario(
            id="base", name="Base", budget=1_080_000, headcount=13, adoption_multiplier=1.0, compute_multiplier=1.0, confidence="medium"
        ),
        Scenario(
            id="accelerated",
            name="Accelerated",
            budget=1_520_000,
            headcount=18,
            adoption_multiplier=1.55,
            compute_multiplier=0.82,
            confidence="low",
        ),
    )
    shock_specs = (
        ("hardware-delay", "Quantum hardware delayed 3–5 years", 1.0, 1.0, 0.8, "hold quantum options; invest in classical and PQC"),
        ("provider-exit", "Provider exit or lock-in", 0.95, 1.15, 0.9, "exercise exit plan and dual-source adapters"),
        ("compute-cost", "Compute cost doubles", 1.0, 2.0, 0.9, "enforce FinOps guardrails and reallocate"),
        ("security-deadline", "Breach or regulatory deadline", 1.1, 1.15, 0.9, "protect PQC and security obligations"),
        ("adoption-half", "Adoption reaches only 50%", 0.9, 1.0, 0.5, "hold growth bets and preserve learning"),
        ("partner-loss", "Top partner unavailable", 0.95, 1.1, 0.8, "activate secondary partner and reduce coupling"),
        ("classical-10x", "Classical solver improves 10x", 1.0, 0.9, 1.0, "kill quantum bet unless renewed evidence clears gate"),
        ("funding-cut", "Funding cut 35%", 0.65, 1.0, 0.85, "fund obligations, core, then learning options"),
        ("demand-surge", "Demand surges 3x", 1.2, 1.25, 3.0, "protect reliability before feature expansion"),
        ("breaking-standard", "Breaking standard or API", 0.9, 1.25, 0.85, "use adapters, version contracts, and pause rollout"),
    )
    shocks = tuple(
        Shock(id=i, name=n, budget_multiplier=b, cost_multiplier=c, adoption_multiplier=a, expected_action=x)
        for i, n, b, c, a, x in shock_specs
    )
    sources = (
        ("NIST PQC", "https://csrc.nist.gov/projects/post-quantum-cryptography", "PQC migration is current work, not a calendar promise"),
        (
            "CISA quantum readiness",
            "https://www.cisa.gov/resources-tools/resources/quantum-readiness-migration-post-quantum-cryptography",
            "Migration guidance; availability recheck required",
        ),
        ("NIST AI RMF", "https://www.nist.gov/itl/ai-risk-management-framework", "Voluntary framework; version 1.0 is under revision"),
        ("FinOps Framework", "https://www.finops.org/framework/", "Technology value and accountability model"),
        ("Kubernetes workloads", "https://kubernetes.io/docs/concepts/workloads/", "Kubernetes requires workload evidence"),
        ("OpenTelemetry", "https://opentelemetry.io/docs/", "Vendor-neutral telemetry contract"),
    )
    evidence = tuple(
        Evidence(id=f"evidence-{i:02d}", title=t, source_url=u, observed_on="2026-09-24", confidence="high", claim_boundary=b)
        for i, (t, u, b) in enumerate(sources, 1)
    )
    return StrategyRepository(
        schema_version="strategy-control-tower.v1",
        revision="quantum-first-roadmap-v1-candidate",
        as_of="2026-09-24",
        approval_status="technical_candidate_unapproved",
        scenarios=scenarios,
        shocks=shocks,
        gates=gates,
        capabilities=_capabilities(),
        initiatives=_initiatives(),
        cost_pools=("people", "cloud", "AI", "quantum", "security", "data", "support", "partnerships", "sales", "contingency"),
        providers=(
            {"id": "azure", "strategy": "buy", "exit": "OpenAPI and OCI images"},
            {"id": "aws", "strategy": "partner", "exit": "provider adapter contract"},
            {"id": "ibm", "strategy": "option", "exit": "portable circuit evidence"},
        ),
        evidence=evidence,
        board_questions=tuple(f"Board challenge {i:02d}: what evidence would reverse this decision?" for i in range(1, 21)),
    )
