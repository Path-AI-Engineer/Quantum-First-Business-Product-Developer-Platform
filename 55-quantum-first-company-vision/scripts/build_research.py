"""Materialize analyst-authored public-source notes; never simulate interviews.

Reviewed on 2026-09-12 using the linked official pages. Each sentence is a short
paraphrase, not a scraped article. Re-running does not pretend to re-access sources.
"""

from __future__ import annotations

from venture_evidence.models import Corpus, Protocol
from venture_evidence.repository import ROOT, write_json

DATE = "2026-09-12"
REVIEW = "2026-12-11"
SOURCES = [
    (
        "nist",
        "Post-Quantum Cryptography Project",
        "NIST",
        "https://csrc.nist.gov/projects/post-quantum-cryptography",
        "Global technical standards; US federal standards are not universal legal mandates.",
        [
            (
                "FIPS standards",
                "NIST published its first three principal postquantum cryptography standards in August 2024.",
                "supports",
            ),
            (
                "PQC Standards",
                "ML-KEM addresses key establishment; ML-DSA and SLH-DSA address digital signatures.",
                "supports",
            ),
            (
                "Migration to PQC",
                "NIST recommends identifying vulnerable cryptography and beginning migration planning.",
                "supports",
            ),
            (
                "Ongoing standardization",
                "Additional algorithms remain in standardization, so compatibility planning must accommodate change.",
                "context",
            ),
        ],
    ),
    (
        "cisa",
        "Quantum-Readiness: Migration to PQC",
        "CISA / NSA / NIST",
        "https://media.defense.gov/2023/Aug/21/2003284212/-1/-1/0/CSI-QUANTUM-READINESS.PDF",
        "US critical infrastructure guidance dated 2023-08-21; pre-final-standard wording is historical.",
        [
            (
                "p1 Why prepare now",
                "The joint guidance calls for roadmaps, inventories, risk assessment and vendor engagement.",
                "supports",
            ),
            (
                "p2 Prepare a cryptographic inventory",
                "Discovery may miss embedded cryptography; vendor documentation is also needed.",
                "contradicts",
            ),
            (
                "p3 Supply chain",
                "Migration planning should account for vendor upgrade paths and associated costs.",
                "supports",
            ),
            (
                "p1 Why prepare now",
                "Data with a long secrecy lifetime motivates preparation for harvest-now-decrypt-later risk.",
                "supports",
            ),
        ],
    ),
    (
        "finops",
        "FinOps Framework",
        "FinOps Foundation",
        "https://www.finops.org/framework/",
        "Technology spending governance; not a survey of willingness to pay.",
        [
            (
                "Definition",
                "FinOps connects engineering, finance and business around technology value "
                "and financial accountability.",
                "supports",
            ),
            (
                "Capabilities",
                "The framework includes cost allocation, forecasting and unit economics capabilities.",
                "context",
            ),
        ],
    ),
    (
        "ai-rmf",
        "AI Risk Management Framework",
        "NIST",
        "https://www.nist.gov/itl/ai-risk-management-framework",
        "Voluntary AI risk guidance; no certification or legal compliance claim.",
        [
            (
                "Overview",
                "The AI RMF is intended for voluntary use when managing trustworthiness across the AI lifecycle.",
                "context",
            ),
            ("Overview", "The framework covers design, development, use and evaluation of AI systems.", "context"),
        ],
    ),
    (
        "ortools",
        "OR-Tools",
        "Google",
        "https://developers.google.com/optimization",
        "Published software capabilities, not measured customer savings.",
        [
            (
                "About OR-Tools",
                "OR-Tools supplies open-source classical optimization for routing, flows and constrained scheduling.",
                "contradicts",
            ),
            (
                "About OR-Tools",
                "OR-Tools supports integration with several commercial and open-source solvers.",
                "contradicts",
            ),
        ],
    ),
    (
        "gurobi",
        "Gurobi Optimizer",
        "Gurobi",
        "https://www.gurobi.com/product",
        "Vendor describes capabilities; comparative performance and ROI not independently accepted.",
        [
            (
                "Problem types",
                "Gurobi offers mathematical optimization for linear, mixed-integer and quadratic problem classes.",
                "contradicts",
            ),
            (
                "Five ways optimization transforms decisions",
                "Gurobi documents sensitivity and infeasibility analysis for model inspection.",
                "contradicts",
            ),
        ],
    ),
    (
        "cplex",
        "ILOG CPLEX Optimization Studio",
        "IBM",
        "https://www.ibm.com/products/ilog-cplex-optimization-studio",
        "Vendor capabilities only; pricing and time-to-value remain unknown.",
        [
            (
                "Use cases",
                "CPLEX and CP Optimizer address mathematical programming and constraint-based scheduling.",
                "contradicts",
            ),
            (
                "Development environment",
                "CPLEX Studio documents a model development environment with debugging and visualization.",
                "context",
            ),
        ],
    ),
    (
        "braket",
        "What is Amazon Braket?",
        "AWS",
        "https://docs.aws.amazon.com/braket/latest/developerguide/what-is-braket.html",
        "Cloud quantum research offering, not evidence of advantage on our workloads.",
        [
            (
                "Build, Test, Run",
                "Braket offers a common service for simulators and different quantum hardware providers.",
                "contradicts",
            ),
            (
                "About quantum computing",
                "AWS describes hardware noise and hybrid algorithm limitations in its introductory guide.",
                "contradicts",
            ),
        ],
    ),
    (
        "azure",
        "What is Azure Quantum?",
        "Microsoft",
        "https://learn.microsoft.com/en-us/azure/quantum/overview-azure-quantum",
        "Quantum cloud service documentation; our laboratory runs locally.",
        [
            (
                "Overview",
                "Azure Quantum supports hardware execution, simulation and resource estimation.",
                "contradicts",
            ),
            (
                "Quantum Development Kit",
                "The QDK is open source and can be used without an Azure account.",
                "contradicts",
            ),
        ],
    ),
    (
        "qiskit",
        "Qiskit",
        "IBM",
        "https://www.ibm.com/quantum/qiskit",
        "Vendor-published tooling description; promotional benchmark numbers excluded.",
        [
            (
                "Quantum information science toolkit",
                "Qiskit provides tools for circuit construction, compilation and experiment execution.",
                "contradicts",
            ),
            (
                "Heterogeneous orchestration",
                "Qiskit documents plugins connecting classical and quantum execution resources.",
                "contradicts",
            ),
        ],
    ),
    (
        "oqs",
        "Open Quantum Safe",
        "Open Quantum Safe",
        "https://openquantumsafe.org/",
        "Open-source research tools; production suitability needs separate assessment.",
        [
            (
                "Project overview",
                "OQS provides liboqs and prototype integrations for postquantum cryptography research.",
                "contradicts",
            ),
            (
                "Project overview",
                "OQS includes integrations with protocols and applications such as OpenSSL.",
                "context",
            ),
        ],
    ),
    (
        "openssl",
        "EVP_KEM-ML-KEM",
        "OpenSSL",
        "https://docs.openssl.org/3.5/man7/EVP_KEM-ML-KEM/",
        "OpenSSL 3.5 documentation, not a certification of arbitrary deployed applications.",
        [
            (
                "Description",
                "OpenSSL 3.5 documents ML-KEM support through its key encapsulation interfaces.",
                "contradicts",
            ),
            ("Algorithms", "The ML-KEM interface documents parameter sets 512, 768 and 1024.", "context"),
        ],
    ),
    (
        "cloudflare",
        "Post-quantum cryptography",
        "Cloudflare",
        "https://developers.cloudflare.com/ssl/post-quantum-cryptography/",
        "Vendor-specific TLS capability, not complete customer cryptographic coverage.",
        [
            (
                "Hybrid key agreement",
                "Cloudflare documents hybrid X25519MLKEM768 key agreement support.",
                "contradicts",
            ),
            (
                "Visitor and origin connections",
                "Postquantum protection depends on support at the client or origin connection endpoint.",
                "supports",
            ),
        ],
    ),
    (
        "dwave",
        "D-Wave Documentation",
        "D-Wave",
        "https://docs.dwavequantum.com/en/latest/",
        "Vendor documentation; no generalized quantum advantage inferred.",
        [
            (
                "Industrial Optimization",
                "D-Wave documents quantum-classical hybrid solvers through its Leap service.",
                "contradicts",
            ),
            (
                "Quantum Research",
                "D-Wave separately documents direct QPU research access and hardware parameters.",
                "context",
            ),
        ],
    ),
]


def main() -> None:
    sources, evidence, claims, entities = [], [], [], []
    for sid, title, publisher, url, scope, notes in SOURCES:
        sources.append(
            dict(
                id=f"source-{sid}",
                title=title,
                publisher=publisher,
                url=url,
                accessed_on=DATE,
                published_on="2023-08-21" if sid == "cisa" else None,
                classification="primary",
                scope=scope,
                access_note="Official document reviewed; concise analyst paraphrases retained. "
                + (
                    "CISA landing returned 403; joint factsheet read from NSA official mirror." if sid == "cisa" else ""
                ),
            )
        )
        for i, (locator, note, stance) in enumerate(notes, 1):
            eid, cid = f"evidence-{sid}-{i}", f"claim-{sid}-{i}"
            evidence.append(
                dict(
                    id=eid,
                    source_id=f"source-{sid}",
                    paraphrase=note,
                    locator=locator,
                    stance=stance,
                    confidence="C3",
                    limitations=scope,
                )
            )
            claims.append(
                dict(
                    id=cid,
                    text=note,
                    kind="fact",
                    external=True,
                    confidence="C3",
                    source_ids=[f"source-{sid}"],
                    supporting_evidence=[eid],
                    opposing_evidence=[],
                    accessed_on=DATE,
                    scope=scope,
                    owner="research-maintainer",
                    review_on=REVIEW,
                    validity="True as a statement about the referenced document at access; not buyer validation.",
                )
            )

    def entity(eid, kind, title, description, refs, details=None, status="hypothesis", related=None):
        entities.append(
            dict(
                id=eid,
                entity_type=kind,
                title=title,
                description=description,
                status=status,
                claim_ids=refs,
                related_ids=related or [],
                details=details or {},
            )
        )

    assumptions = [
        (
            "market",
            "Reachable market is unknown",
            "Organization counts are illustrative planning inputs, not an observed TAM.",
        ),
        ("price", "Willingness to pay is unmeasured", "All price intervals need buyer and procurement validation."),
        ("delivery", "Delivery effort is unmeasured", "Hours and unit costs need a time-tracked assisted pilot."),
        ("access", "Buyer access is unknown", "Founder has not demonstrated access to a qualified buying committee."),
        (
            "moat",
            "Evidence workflow may differentiate",
            "Defensibility depends on repeat use and permissioned operational learning.",
        ),
    ]
    for key, title, desc in assumptions:
        entity(
            f"assumption-{key}",
            "assumption",
            title,
            desc,
            ["claim-cisa-1", "claim-finops-2"],
            {
                "confidence": "C0",
                "owner": "founder",
                "review_on": REVIEW,
                "validation": "Future interviews and measured pilot",
            },
        )

    verticals = [
        ("finance", "Financial services", "Long-lived financial records and service dependencies", "claim-cisa-4"),
        ("health", "Health / life sciences", "Sensitive records and research information lifecycle", "claim-cisa-4"),
        ("logistics", "Logistics / manufacturing", "Scheduling, routing and OT dependencies", "claim-ortools-1"),
        (
            "regulated-tech",
            "Technology / regulated public sector",
            "Software supply chain and accountable platform spending",
            "claim-finops-1",
        ),
    ]
    roles = [
        ("security", "CISO / cryptography lead", "Security architecture owner", "Audit / risk committee"),
        ("operations", "COO / operations lead", "Planner / operations analyst", "Service delivery teams"),
        ("engineering", "CTO / VP Engineering", "Platform engineer / innovation lead", "Developers / procurement"),
    ]
    for vertical, label, pain, ref in verticals:
        for role, buyer, user, beneficiary in roles:
            entity(
                f"icp-{vertical}-{role}",
                "customer_profile",
                f"{label} · {buyer}",
                f"Public-evidence-derived archetype. Proposed pain: {pain}. No named customer or interview.",
                [ref, "claim-cisa-1"],
                {
                    "vertical": label,
                    "buyer": buyer,
                    "user": user,
                    "beneficiary": beneficiary,
                    "budget": None,
                    "access": None,
                    "switching_barrier": "Existing vendor relationships and change approvals; hypothesis to test.",
                },
                status="inference",
            )
    jobs = [
        ("Identify cryptographic dependencies before planning a migration", "cisa-1", "finance-security"),
        ("Associate long-lived records with protection requirements", "cisa-4", "health-security"),
        ("Request embedded-cryptography inventories from suppliers", "cisa-2", "regulated-tech-security"),
        ("Prioritize system upgrades with owners and risk context", "nist-3", "finance-security"),
        ("Separate key establishment from signature migration", "nist-2", "regulated-tech-engineering"),
        ("Verify endpoint support before changing TLS policy", "cloudflare-2", "health-engineering"),
        ("Compare routes under real operational constraints", "ortools-1", "logistics-operations"),
        ("Test schedule feasibility before committing capacity", "cplex-1", "logistics-operations"),
        ("Inspect sensitivity when optimization assumptions change", "gurobi-2", "finance-operations"),
        ("Preserve a solver baseline before testing alternatives", "ortools-2", "health-operations"),
        ("Attribute experimental cloud spend to an owner", "finops-1", "regulated-tech-engineering"),
        ("Compare prototype cost against a business value unit", "finops-2", "finance-engineering"),
        ("Select simulator or device for a bounded experiment", "braket-1", "health-engineering"),
        ("Estimate resources before proposing a hardware dependency", "azure-1", "logistics-engineering"),
        ("Track circuit preparation and execution provenance", "qiskit-1", "regulated-tech-engineering"),
        ("Evaluate a hybrid solver against a classical workflow", "dwave-1", "logistics-operations"),
        ("Integrate trustworthy AI review in a product lifecycle", "ai-rmf-1", "regulated-tech-security"),
        ("Plan supplier contract changes for migration", "cisa-3", "finance-security"),
    ]
    for i, (job, ref, icp) in enumerate(jobs, 1):
        entity(
            f"job-{i:02}",
            "job_to_be_done",
            job,
            "Inferred job grounded in public guidance/capability; frequency and buyer priority remain unverified.",
            [f"claim-{ref}"],
            {"desired_outcome": job, "frequency": None, "validation": "Future discovery interview"},
            status="inference",
            related=[f"icp-{icp}"],
        )
    alternatives = [
        ("OR-Tools", "ortools", "Classical routing and constrained optimization"),
        ("Gurobi", "gurobi", "Classical commercial solver and modeling support"),
        ("CPLEX", "cplex", "Classical planning and scheduling tools"),
        ("Amazon Braket", "braket", "Managed quantum experimentation"),
        ("Azure Quantum", "azure", "Hardware, simulation and estimation service"),
        ("Qiskit", "qiskit", "Open tooling and orchestration ecosystem"),
        ("Open Quantum Safe", "oqs", "Open PQC research library and prototypes"),
        ("OpenSSL", "openssl", "Integrate documented PQC primitives in existing libraries"),
        ("Cloudflare", "cloudflare", "Adopt provider TLS migration capabilities"),
        ("D-Wave Leap", "dwave", "Evaluate vendor hybrid optimization service"),
    ]
    for i, (name, ref, desc) in enumerate(alternatives, 1):
        entity(
            f"alternative-{i:02}",
            "competitor",
            name,
            desc,
            [f"claim-{ref}-1"],
            {
                "price": None,
                "time_to_value": None,
                "control": "Published capability; deployment fit untested",
                "lock_in": "Contract/API/data portability review required",
                "comparison_kind": "vendor-documented capability",
            },
            status="documented",
        )
    for i, name in enumerate(
        [
            "Internal spreadsheet and asset inventory",
            "Existing security consultancy",
            "Internal operations research team",
            "Vendor-led upgrade program",
            "Defer purchase and accept risk",
        ],
        11,
    ):
        entity(
            f"alternative-{i:02}",
            "alternative",
            name,
            "Candidate substitute to test in discovery; not a claim that surveyed buyers use it.",
            ["claim-cisa-3", "claim-finops-1"],
            {
                "price": None,
                "time_to_value": None,
                "control": "Buyer-dependent",
                "lock_in": "Unknown",
                "gap": "Measure decision effort and accountability",
            },
        )
    patterns = [
        "Who owns the budget?",
        "Security review before data export",
        "Procurement requires bounded deliverables",
        "Vendor upgrade schedules constrain delivery",
        "Legal review of discovery data",
        "Buyer and operator differ",
        "A pilot needs acceptance criteria",
        "Renewal requires recurring value",
        "Incumbent bundling can erase price",
        "Operational change windows constrain migration",
    ]
    for i, title in enumerate(patterns, 1):
        entity(
            f"buying-{i:02}",
            "buying_pattern",
            title,
            "Buying/risk hypothesis for discovery, not an observed buyer pattern.",
            ["claim-cisa-3", "claim-finops-1"],
            {"test": "Ask for the last comparable purchase and its decision record."},
        )
    workflows = [
        (
            "pqc",
            "Migration readiness",
            ["Scope assets", "Inventory", "Ask vendors", "Prioritize", "Approve changes"],
            "cisa-1",
        ),
        (
            "optimization",
            "Operational optimization",
            ["Capture constraints", "Model baseline", "Validate feasibility", "Compare cost", "Pilot"],
            "ortools-1",
        ),
        (
            "platform",
            "Hybrid experimentation",
            ["Define question", "Choose baseline", "Budget", "Execute experiment", "Review evidence"],
            "braket-1",
        ),
    ]
    for key, title, steps, ref in workflows:
        entity(
            f"workflow-{key}",
            "workflow",
            title,
            "Proposed current-state map inferred from public guidance; confirm with operators.",
            [f"claim-{ref}"],
            {"steps": steps, "owner": "future workflow interview"},
            status="inference",
        )
        entity(
            f"pain-{key}",
            "pain",
            f"Decision friction: {title}",
            "Unclear dependencies, acceptance criteria or accountability may increase rework. Magnitude unknown.",
            [f"claim-{ref}"],
            {"trigger": steps[0], "frequency": None},
            related=[f"workflow-{key}"],
        )
        entity(
            f"inaction-{key}",
            "inaction",
            f"Cost of inaction: {title}",
            "Parametric map only. No observed cost, probability or loss estimate is available.",
            [f"claim-{ref}"],
            {
                "formula": "events_per_year * hours_per_event * hourly_cost + expected_rework",
                "events_per_year": None,
                "hours_per_event": None,
                "hourly_cost": None,
                "expected_rework": None,
                "nonmonetary_cost": "Unresolved dependencies and decisions",
            },
        )
    questions = [
        "Tell me about the last cryptographic change your team handled.",
        "What triggered that change?",
        "Who participated in deciding what to do?",
        "What information was missing at that point?",
        "How did you find where the cryptography was used?",
        "What could your existing tools not tell you?",
        "What happened after you asked suppliers for information?",
        "How did you decide which assets came first?",
        "What approvals did the work need?",
        "How long did each approval take?",
        "Which budget paid for the work, if any?",
        "What alternatives did you consider?",
        "Why did you choose that alternative?",
        "What did the team do manually?",
        "How did you know the work was complete?",
        "What was left unresolved?",
        "Tell me about a time a proposed security purchase was rejected.",
        "What caused that rejection?",
        "How do you compare a service proposal with doing the work internally?",
        "What can an external team access today?",
        "What evidence would your risk team need to approve a pilot?",
        "What would make you stop such a pilot?",
        "How do you evaluate recurring work after the first assessment?",
        "Who else sees this process differently?",
    ]
    for i, title in enumerate(questions, 1):
        entity(
            f"question-{i:02}",
            "discovery_question",
            title,
            "Open, non-leading future interview prompt.",
            [],
            status="planned",
        )
    entity(
        "interview-plan",
        "interview_plan",
        "15 real interviews, not yet conducted",
        "Recruit through opt-in professional introductions; no outreach has been sent.",
        [],
        {
            "target": 15,
            "completed": 0,
            "sampling": {"primary_security": 6, "secondary_tech": 3, "operators": 3, "procurement_risk_legal": 3},
            "consent": "Ask before recording; anonymize notes; permit withdrawal.",
            "analysis": "Code triggers, alternatives, budget owner and dissent; count disconfirming cases.",
            "recruitment": (
                "Seek recent migration or comparable security-change experience; no convenience-only validation."
            ),
        },
        status="planned",
    )
    caps = [
        (
            "pqc",
            "PQC inventory and migration planning",
            "available-now",
            "nist-3",
            "Classical inventory and vendor coordination",
            "Approved scope, tested compatibility, cryptographic expert review",
            "Pause if inventory cannot be obtained with consent",
        ),
        (
            "optimization",
            "Quantum-ready optimization assessment",
            "available-now",
            "ortools-1",
            "OR-Tools / commercial solver baseline",
            "Repeated feasible improvement after equal-budget comparison",
            "Do not sell quantum uplift when classical baseline wins",
        ),
        (
            "platform",
            "Hybrid execution abstraction",
            "experimental",
            "braket-1",
            "Classical jobs and provider-native tools",
            "Paid repeat workflow and portable contracts",
            "Stop if native tools cover the entire job at lower cost",
        ),
        (
            "advantage",
            "Broad fault-tolerant quantum advantage",
            "speculative",
            "braket-2",
            "Use best available classical implementation",
            "Independent reproducible advantage at total workload cost",
            "No roadmap date or revenue dependency before evidence",
        ),
    ]
    for key, title, maturity, ref, baseline, gate, kill in caps:
        entity(
            f"capability-{key}",
            "capability",
            title,
            "Capability classification is an analyst assessment.",
            [f"claim-{ref}"],
            {
                "maturity": maturity,
                "trl": None,
                "trl_note": "No formal TRL assessment performed",
                "classical_baseline": baseline,
                "maturity_gate": gate,
                "kill_gate": kill,
                "vendor_risk": "Recheck support and interoperability before any adoption",
            },
            status="inference",
        )
    dimensions = [
        ("severity", "Problem severity", 10, "benefit"),
        ("urgency", "Time urgency", 10, "benefit"),
        ("budget", "Accessible budget", 9, "benefit"),
        ("frequency", "Frequency", 5, "benefit"),
        ("inaction", "Cost of inaction", 7, "benefit"),
        ("access", "Buyer access", 9, "benefit"),
        ("classical-value", "Classical time-to-value", 10, "benefit"),
        ("differentiation", "Defensible differentiation", 7, "benefit"),
        ("accumulation", "Workflow / data accumulation", 6, "benefit"),
        ("regulation", "Regulatory compatibility", 6, "benefit"),
        ("optionality", "Quantum optionality", 3, "benefit"),
        ("dependency", "Technology dependence risk", 7, "cost"),
        ("complexity", "Delivery complexity", 6, "cost"),
        ("competition", "Competitive intensity", 5, "cost"),
    ]
    stress = [
        ("budget-freeze", "Budget becomes the constraint", {"budget": 3, "urgency": 0.5}),
        ("incumbent-bundle", "Incumbents bundle the service", {"competition": 3, "differentiation": 2}),
        ("buyer-access", "Buyer access dominates", {"access": 3, "severity": 0.5}),
        ("hardware-delay", "Quantum maturity is delayed", {"dependency": 3, "optionality": 0.2}),
        ("operations-pressure", "Operational frequency dominates", {"frequency": 3, "regulation": 0.5}),
        ("compliance-review", "Regulatory fit dominates", {"regulation": 3, "complexity": 2}),
        ("service-cost", "Human delivery becomes expensive", {"complexity": 3, "classical-value": 2}),
        ("quantum-progress", "Quantum optionality gets higher weight", {"optionality": 5, "dependency": 0.5}),
    ]
    protocol = dict(
        version="decision-protocol-v1",
        status="analyst_specification_not_buyer_validation",
        dimensions=[dict(id=i, label=name, weight=w, direction=d) for i, name, w, d in dimensions],
        scenarios={"conservative": 0, "base": 0.5, "aggressive": 1},
        stress_cases=[dict(id=i, title=t, multipliers=m) for i, t, m in stress],
        unknown_rule=(
            "Unknown stays null and contributes the full [0,5] interval; midpoint is an assumption, not evidence."
        ),
        tie_rule="Sort equal scenario estimates by stable ID; any overlapping intervals make selection provisional.",
    )
    scores = {
        "pqc": [
            (3.5, 5),
            (3, 5),
            None,
            (2, 4),
            (3, 5),
            None,
            (4, 5),
            (1, 3),
            (3, 4),
            (3, 4),
            (2, 3),
            (0, 1),
            (2, 4),
            (3, 5),
        ],
        "optimization": [
            (3, 4),
            (2, 4),
            None,
            (3, 5),
            (2, 4),
            None,
            (3, 5),
            (1, 3),
            (2, 4),
            (2, 4),
            (3, 5),
            (1, 3),
            (3, 5),
            (4, 5),
        ],
        "platform": [
            (1, 3),
            (1, 3),
            None,
            (1, 3),
            (1, 3),
            None,
            (2, 4),
            (1, 2),
            (2, 4),
            (2, 4),
            (3, 5),
            (2, 4),
            (3, 5),
            (4, 5),
        ],
    }
    names = {
        "pqc": "Postquantum readiness assessment",
        "optimization": "Quantum-ready optimization validation",
        "platform": "Hybrid development and operations platform",
    }
    opportunities = []
    dimension_context = {
        "severity": (
            "Long-lived cryptographic exposure motivates assessment, but impact is buyer-specific.",
            "Operational infeasibility can matter; no customer's loss has been measured.",
            "Fragmented experimentation is a proposed pain, not a validated critical incident.",
        ),
        "urgency": (
            "Readiness guidance supports preparation without a claimed local legal deadline.",
            "Urgency depends on a concrete planning bottleneck that has not been observed.",
            "A platform has no verified buying trigger in this corpus.",
        ),
        "frequency": (
            "Inventory and vendor changes may recur; cadence and paid frequency are unmeasured.",
            "Repeated planning is the proposed job; establish its actual cadence in discovery.",
            "Repeated hybrid jobs are an assumption and may remain occasional research.",
        ),
        "inaction": (
            "Delay may increase migration work and secrecy exposure; expected financial loss is unknown.",
            "Loss from an inadequate plan must be compared against the existing classical baseline.",
            "Cost of duplicated workflow effort is hypothetical until timed on a real team.",
        ),
        "classical-value": (
            "Inventory and roadmap artifacts can be delivered without quantum hardware.",
            "A classical solver benchmark provides value before any quantum comparison.",
            "Cost/provenance could be classical, but integration overhead delays the first outcome.",
        ),
        "differentiation": (
            "Primitives alone are not a moat; buyer value must come from a scoped evidence workflow.",
            "Established solvers constrain claims; differentiation needs domain evidence.",
            "Native cloud and SDK functionality limits a generic wrapper's differentiation.",
        ),
        "accumulation": (
            "Permissioned compatibility and migration history could accumulate; none is owned yet.",
            "Domain instances and benchmarks could accumulate only with explicit data rights.",
            "Workflow contracts may accumulate if teams adopt them; adoption is unvalidated.",
        ),
        "regulation": (
            "Auditability may fit risk review; no jurisdictional compliance conclusion is made.",
            "A reproducible decision trail may help review, subject to sector constraints.",
            "Cross-provider data governance adds review obligations rather than automatic compliance.",
        ),
        "optionality": (
            "PQC preparation preserves adaptability without selling quantum execution.",
            "Validated classical benchmarks leave an option for future workload-specific advantage.",
            "Adapters preserve provider options only if contracts remain portable.",
        ),
        "dependency": (
            "An assessment does not need a fault-tolerant quantum computer.",
            "Classical delivery reduces hardware reliance, but future quantum claims remain gated.",
            "Multiple external runtimes increase versioning and provider-change exposure.",
        ),
        "complexity": (
            "Service scoping and embedded discovery blind spots require human delivery.",
            "Constraint modeling and fair compute budgets require domain-specific work.",
            "Adapter lifecycle, cost semantics and support span several provider boundaries.",
        ),
        "competition": (
            "Internal teams, consultants and vendor PQC support are credible alternatives.",
            "Free and commercial classical solvers are established alternatives.",
            "Provider-native tooling and internal platforms already cover parts of the proposed job.",
        ),
    }
    for key in scores:
        cap = next(e for e in entities if e["id"] == f"capability-{key}")
        refs = {
            "pqc": ["claim-nist-3", "claim-cisa-1"],
            "optimization": ["claim-ortools-1", "claim-gurobi-1"],
            "platform": ["claim-finops-1", "claim-braket-1"],
        }[key]
        opposing = {
            "pqc": ["claim-cisa-2", "claim-cloudflare-1", "claim-openssl-1"],
            "optimization": ["claim-ortools-2", "claim-cplex-1"],
            "platform": ["claim-qiskit-2", "claim-azure-2"],
        }[key]
        opportunities.append(
            dict(
                id=f"opportunity-{key}",
                name=names[key],
                promise={
                    "pqc": (
                        "Hypothesis: within 4 weeks, deliver an owner-reviewed inventory for 2 agreed services, "
                        "with unknowns and a prioritized roadmap."
                    ),
                    "optimization": (
                        "Hypothesis: within 4 weeks, establish a reproducible feasible baseline "
                        "and equal-budget comparison for one workflow."
                    ),
                    "platform": (
                        "Hypothesis: within 4 weeks, reproduce one bounded workflow "
                        "with cost and provenance across two adapters."
                    ),
                }[key],
                classical_alternative=cap["details"]["classical_baseline"],
                maturity_condition=cap["details"]["maturity_gate"],
                kill_gate=cap["details"]["kill_gate"],
                primary_icp="icp-finance-security" if key == "pqc" else "icp-logistics-operations",
                secondary_icp="icp-regulated-tech-security" if key == "pqc" else "icp-regulated-tech-engineering",
                claim_ids=refs,
                opposing_claim_ids=opposing,
                dimensions={
                    d[0]: None if v is None else dict(low=v[0], high=v[1])
                    for d, v in zip(dimensions, scores[key], strict=True)
                },
                rationale={
                    d[0]: (
                        "Unknown: no direct buyer evidence (assumption-access / assumption-price)."
                        if v is None
                        else (
                            f"Analyst interval: {dimension_context[d[0]][list(scores).index(key)]} "
                            f"Context: {', '.join(refs)}; "
                            f"challenge with {', '.join(opposing)}."
                        )
                    )
                    for d, v in zip(dimensions, scores[key], strict=True)
                },
            )
        )
    offers = [
        (
            "assessment",
            "Fixed-price assessment",
            [6000, 18000],
            [40, 120],
            "Scoped service inventory and roadmap",
            "Existing consultant or internal team",
        ),
        (
            "pilot",
            "Pilot fee with acceptance criteria",
            [12000, 30000],
            [80, 240],
            "Two services with reviewed acceptance evidence",
            "Existing integrator",
        ),
        (
            "subscription",
            "Organization subscription / year",
            [6000, 24000],
            [20, 80],
            "Recurring change and inventory review",
            "Asset management workflow",
        ),
        (
            "managed",
            "Managed service / year",
            [24000, 72000],
            [200, 600],
            "Owned review cadence with agreed service levels",
            "Security managed service provider",
        ),
        (
            "consumption",
            "Platform consumption / reviewed job",
            [50, 500],
            [0.5, 5],
            "Metered, bounded evidence job",
            "Provider-native metering",
        ),
        (
            "enterprise",
            "Enterprise license / year",
            [30000, 120000],
            [100, 400],
            "Contracted deployment and support",
            "Internal platform / incumbent bundle",
        ),
    ]
    for key, title, price, hours, unit, alternative in offers:
        entity(
            f"pricing-{key}",
            "pricing",
            title,
            "Illustrative USD hypothesis, not a quote, revenue or validated willingness to pay.",
            ["claim-finops-2"],
            {
                "price_range_usd": price,
                "delivery_hours_range": hours,
                "hourly_cost_range_usd": [40, 100],
                "tooling_cost_range_usd": [100, 1000],
                "margin_target_range": [0.4, 0.65],
                "formula": "margin = (price - hours * hourly_cost - tooling) / price",
                "volume_sensitivity": "Delivery hours and capacity must be remeasured before volume discounts",
                "buyer": "CISO with procurement approval",
                "value_unit": unit,
                "anchor": alternative,
                "human_dependency": "Expert scoping, validation and change approval remain necessary",
                "validation": "Obtain opt-in pilot procurement feedback and time-track delivery",
            },
            related=["assumption-price", "assumption-delivery"],
        )
    experiments = [
        (
            "discovery",
            "Interview buying committees",
            "15 opt-in interviews; at least 5 identify a recent concrete trigger",
            "Pivot if no recurring trigger after 15 qualified interviews",
        ),
        (
            "access",
            "Test buyer access",
            "10 tailored opt-in introduction requests; at least 3 qualified conversations",
            "Change ICP/channel if no access after two channels",
        ),
        (
            "price",
            "Test paid assessment proposal",
            "3 qualified proposals reviewed by budget owners",
            "Pause after 3 explicit no-budget decisions; do not count polite interest",
        ),
        (
            "delivery",
            "Measure assisted delivery",
            "One consented pilot; at most 120 delivery hours for 2 scoped services",
            "Rescope if effort exceeds 120h or data access is denied",
        ),
        (
            "incumbent",
            "Compare incumbent outcome",
            "Blind compare evidence completeness and operator time on same scope",
            "Kill differentiation claim if incumbent meets the job at lower total cost",
        ),
        (
            "repeat",
            "Test recurring need",
            "Two subsequent review cycles with explicit customer continuation decision",
            "Do not launch subscription without recurring paid use",
        ),
    ]
    for i, (key, title, criterion, kill) in enumerate(experiments, 1):
        entity(
            f"experiment-{key}",
            "experiment",
            title,
            "Planned future validation; acceptance thresholds are analyst hypotheses.",
            ["claim-cisa-1", "claim-finops-1"],
            {
                "acceptance": criterion,
                "kill_gate": kill,
                "results": None,
                "owner": "founder",
                "review_on": REVIEW,
                "order": i,
            },
            status="planned",
        )
        entity(
            f"risk-{key}",
            "risk",
            f"Risk: {title.lower()}",
            "Unresolved risk; no evidence of mitigation completion.",
            ["claim-cisa-2", "claim-cloudflare-1"],
            {
                "kill_gate": kill,
                "trigger": criterion,
                "response": "Pivot scope, pause spend or stop thesis; record dissent",
                "owner": "founder",
            },
            related=[f"experiment-{key}"],
        )
    for months, title, gate, build, buy in [
        (
            [0, 6],
            "Assisted evidence service",
            "Consented paid pilot and measured scope",
            "Templates and validation",
            "Existing inventory tooling",
        ),
        (
            [6, 18],
            "Repeatable readiness product",
            "Repeated paid delivery with sustainable margins",
            "Change tracking and evidence workflow",
            "Maintained crypto libraries",
        ),
        (
            [18, 36],
            "Shared platform and suite",
            "Multiple repeatable workflows, portability and support economics",
            "Contract adapters and permissioned benchmark corpus",
            "Cloud execution only when budgeted",
        ),
    ]:
        entity(
            f"stage-{months[0]}",
            "product_stage",
            title,
            "Conditional sequence, not a promised release date.",
            ["claim-finops-1", "claim-braket-2"],
            {
                "months": months,
                "gate": gate,
                "build": build,
                "buy_partner": buy,
                "quantum_gate": (
                    "Independent reproducible workload advantage and affordable total cost; classical fallback remains"
                ),
            },
            status="planned",
        )
    moats = [
        "Permissioned migration compatibility data",
        "Domain models and transparent benchmarks",
        "Integration with critical review workflows",
        "Portable provider contracts and developer experience",
        "Audit trail with decision provenance",
        "Trusted partner distribution",
        "Maintained regulatory mapping",
        "Legitimate switching costs from useful workflow history",
    ]
    for i, title in enumerate(moats, 1):
        entity(
            f"moat-{i:02}",
            "moat",
            title,
            "Candidate accumulating asset; none is claimed defensible today.",
            ["claim-cisa-3", "claim-qiskit-2"],
            {
                "commoditization_test": "Can an incumbent reproduce the outcome within a quarter?",
                "data_rights": "Only permissioned or public evidence; no client reuse without contract",
                "exit": "Open formats and export; no artificial lock-in",
            },
        )
    hostile = [
        "Why would a buyer pay when libraries already ship PQC?",
        "Which specific buyer owns this problem?",
        "Where is the verified budget?",
        "What proves access to that buyer?",
        "Why start in finance?",
        "Are NIST recommendations local legal mandates?",
        "How will scope exclude undiscoverable embedded crypto?",
        "What if the incumbent bundles the assessment?",
        "What if there is no recurring need?",
        "Why is this not ordinary security consulting?",
        "What data rights permit a future moat?",
        "What if a quantum computer useful for attacks takes decades?",
        "What if classical optimization always wins?",
        "What is the cost of an incorrect inventory?",
        "Who approves cryptographic changes?",
        "Does a high score demonstrate willingness to pay?",
        "Are unknown values treated as zero?",
        "Can weights be changed to force a preferred answer?",
        "Does the ranking survive interval uncertainty?",
        "What supports the TAM numbers?",
        "Are founder labor and acquisition included in margins?",
        "What evidence can make the team stop?",
        "Has anyone actually been interviewed?",
        "Can another reviewer reproduce this decision?",
    ]
    answers = [
        "Unproven; test workflow value beyond supplied primitives in experiment-incumbent.",
        "Primary candidate is icp-finance-security; not a validated customer.",
        "No verified budget exists; assumption-price remains open.",
        "No access evidence exists; experiment-access is planned.",
        "Long confidentiality lifetime is a plausible signal, not vertical demand evidence; compare secondary ICP.",
        "No. Jurisdiction-specific legal review is required; no local compliance promise.",
        "Report coverage limitations and require vendor inventories; claim-cisa-2 contradicts exhaustive scanning.",
        "Run experiment-incumbent and kill the standalone price claim if no measurable gap remains.",
        "Keep an assessment business or stop; experiment-repeat gates subscription.",
        "It initially is an assisted service; productization is conditional on repeated evidence.",
        "No client data rights exist yet; require explicit contractual permission and export rights.",
        "Value proposition is classical inventory and migration readiness, with no hardware date dependency.",
        "Deliver the classical result and reject quantum uplift claims.",
        "Unknown; scope and liability review required before any live engagement.",
        "The customer security/change authority; this laboratory cannot approve changes.",
        "No. Scores are analyst assumptions that prioritize future validation.",
        "No. Null expands to [0,5] and lowers known-weight coverage.",
        "Protocol digest pins the authored method; sensitivity exposes weight-driven flips.",
        "Overlapping intervals make the wedge provisional even if midpoint rank is stable.",
        "Only illustrative parameters; observed market count is unknown.",
        "Only modeled delivery labor; acquisition, taxes and other overhead are explicitly excluded.",
        "Each experiment links to an explicit risk and kill gate.",
        "Zero interviews conducted; all 15 are planned.",
        "CLI, source notes, protocol, schemas and checksummed bundle reconstruct the calculation.",
    ]
    for i, (question, answer) in enumerate(zip(hostile, answers, strict=True), 1):
        entity(
            f"challenge-{i:02}",
            "challenge",
            question,
            answer,
            ["claim-cisa-2", "claim-finops-2", "claim-braket-2"],
            {"review_kind": "analyst_self_review_not_independent_red_team", "result": "answered_with_explicit_limit"},
            status="documented",
        )
    for i, (title, answer) in enumerate(
        [
            (
                "No raw infrastructure data may leave our environment",
                "Local-only workflow; agree a redacted evidence contract before pilot.",
            ),
            (
                "How do we verify completeness?",
                "We cannot promise total discovery; specify covered services, blind spots and vendor confirmations.",
            ),
            (
                "Who is liable for changing cryptography?",
                "No live changes in the offer until separate legal and change approvals.",
            ),
            (
                "How can we exit the service?",
                "Versioned JSON/Markdown export with checksums and no proprietary data lock.",
            ),
            (
                "What proves the price is justified?",
                "Nothing yet; compare timed pilot effort and current alternative with budget owner.",
            ),
            (
                "Are you certifying compliance or quantum safety?",
                "No certification, universal security or quantum advantage claim is made.",
            ),
        ],
        1,
    ):
        entity(f"objection-{i:02}", "objection", title, answer, ["claim-cisa-2", "claim-ai-rmf-1"], status="documented")
    for i, ref in enumerate(["nist-3", "cisa-1", "cisa-2", "cloudflare-1", "ortools-1", "braket-1"], 1):
        entity(
            f"trace-{i:02}",
            "trace",
            f"Decision-to-source path {i}",
            "Automated gate verifies every reference along this path.",
            [f"claim-{ref}"],
            {"path": ["decision-wedge", f"claim-{ref}", f"evidence-{ref}", "source-" + ref.rsplit("-", 1)[0]]},
            status="documented",
        )
    entity(
        "decision-wedge",
        "decision",
        "Provisional wedge: postquantum readiness assessment",
        "Proceed only to buyer discovery. No company launch, paid validation, legal approval "
        "or next project authorized by this record.",
        ["claim-nist-3", "claim-cisa-1", "claim-cisa-2", "claim-cloudflare-1", "claim-ortools-1", "claim-braket-1"],
        {
            "recommendation": "proceed_to_discovery",
            "approval": "pending_human_review",
            "dissent": "Budget/access unknown; incumbents may cover the job.",
            "alternative_decision": (
                "Pivot to classical optimization if buyer evidence dominates; pause if access fails."
            ),
            "quantified_promise": opportunities[0]["promise"],
        },
        status="candidate",
    )
    entity(
        "handoff-company-vision",
        "handoff_contract",
        "company-vision-v1",
        "Versioned candidate artifact only. Separate repositories, databases, credentials and execution state.",
        [],
        {
            "approval": "pending_human_review",
            "receiver": "Software Engineer Project 10 Sprint 1, subject to its own map",
            "boundary": "No automatic import or implementation permission",
            "next_project": "56 per supplied map; existing folder numbering differs",
        },
        status="candidate",
    )
    corpus = Corpus.model_validate(
        dict(
            schema_version="venture.corpus.v1",
            research_date=DATE,
            scope="Public technical evidence; buyer archetypes and economics are unvalidated hypotheses.",
            buyer_interviews_completed=0,
            paying_customers_validated=0,
            approval="pending_human_review",
            sources=sources,
            evidence=evidence,
            claims=claims,
            entities=entities,
            opportunities=opportunities,
        )
    )
    write_json(ROOT / "data/opportunities/protocol.v1.json", Protocol.model_validate(protocol).model_dump(mode="json"))
    write_json(ROOT / "data/evidence/corpus.v1.json", corpus.model_dump(mode="json"))
    print({"sources": len(sources), "evidence": len(evidence), "entities": len(entities), "approval": corpus.approval})


if __name__ == "__main__":
    main()
