# Project 60 — Quantum-First Strategy Control Tower

Auditable 1/3/10-year strategy system for a quantum-first company. It turns assumptions, evidence, capabilities, dependencies, costs, risks, signals, and gates into reproducible decisions. It does **not** execute cloud, financial, staffing, or product changes.

## Implemented

- Typed repository: 12 capability domains, 12 initiatives, 3 scenarios, 10 shocks, 10 cost pools, risks, gates, providers, and evidence.
- Deterministic scenario, critical-path, constrained allocation, cost reconciliation, and gate engines.
- Classical baselines and kill conditions for every quantum initiative; PQC is a Year-1 obligation.
- FastAPI/OpenAPI 3.1 API and keyboard-accessible Next.js Control Tower with all 12 views.
- Reconciled board, technical, and operating reports from one canonical revision.
- 437-case locked evaluation, quality gate, Playwright flows, and Docker Compose smoke test.

## Truth boundary

Economics, adoption, headcount, and long-horizon values are synthetic planning scenarios. The frozen artifact is `technical_candidate_unapproved`: no board approval, customer adoption, quantum advantage, financing event, or external decision is claimed.

## Local closure

```powershell
Set-Location "C:\JeanLoa\Path-AI-Engineer\Quantum-First-Business-Product-Developer-Platform\60-quantum-first-platform-roadmap"
.\scripts\complete-project.ps1
```

Individual commands: `setup.ps1`, `quality-gate.ps1`, and `container-smoke.ps1` under `scripts/`.

Control Tower: `http://127.0.0.1:8960`  
API docs: `http://127.0.0.1:8060/docs`

The long-range roadmap is conditional. Project 61 must not start until the approval field in the final bundle is signed by an authorized reviewer.

