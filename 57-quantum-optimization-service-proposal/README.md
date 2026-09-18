# 57 — Quantum Optimization Service Proposal

`Optimization Value Validation Lab` is a local, synthetic-data product lab for deciding whether an operational decision should use classical optimization, a bounded quantum-ready experiment, data/process remediation, or no pilot.

The project is classical-first. It does not claim quantum advantage, realized savings, investment advice, or production decision automation. Cloud execution and paid workloads are outside this repository's validation boundary.

## What is implemented

- 90 deterministic instances across workforce scheduling, distribution routing, and portfolio allocation;
- 66 development instances and 24 locked test instances;
- eligibility engine with 13 evidence dimensions, unknowns, confidence, explanations, and four outcomes;
- OR-Tools CP-SAT/routing baselines, domain heuristics, small exact oracles, and independent feasibility checkers;
- bounded four-variable p=1 local QAOA diagnostic with three fixed seeds and no advantage claim;
- 210-run final benchmark, robustness evidence, value ranges, pilot/SOW, and hypothetical packaging;
- FastAPI/OpenAPI 3.1 and JSON Schema 2020-12 contracts backed by local DuckDB metadata;
- Next.js Validation Lab with ten responsive, keyboard-accessible evidence surfaces;
- Docker Compose smoke path for API/web parity without credentials or paid services.

## Local workflow

```powershell
Set-Location "C:\JeanLoa\Path-AI-Engineer\Quantum-First-Business-Product-Developer-Platform\57-quantum-optimization-service-proposal"
.\scripts\setup.ps1
.\scripts\quality-gate.ps1 -RequireFinal
```

Full local closure:

```powershell
.\scripts\complete-project.ps1
```

Docker is optional in the project map. When Docker Desktop is running, add `-IncludeContainers` to validate image startup and proxy parity.

The local web/API ports are `3057` and `8057`. Swagger is available at `http://127.0.0.1:8057/docs` while the API is running.

## Evidence boundary

The generated `optimization-service-proposal-v1` bundle is a `technical_candidate_unapproved`. Approval remains `null` until a real buyer, finance/risk reviewers, and an executive decision owner assess client evidence and an eight-week shadow-mode pilot. Tests never manufacture that missing business evidence.
