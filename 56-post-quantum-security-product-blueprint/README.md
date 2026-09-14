# Project 56 — Cryptographic Migration Command Center

Plan 10 · weeks 224–226 · global days 1562–1582. This repository is a local,
synthetic product laboratory, **not** a production PQC assurance service. It
does not connect to infrastructure, scan external systems or change keys,
certificates, libraries, protocols or configurations.

## What is implemented

- Reproducible fictional corpus: Northstar Bank (45 assets), Aster Health (38)
  and Harbor Industrial (42); 125 assets, 220 observations, 35 dependencies,
  28 owner IDs and 30 known positive finding assets.
- Bounded fixture-driven CBOM, CycloneDX, TLS CSV, SARIF, KMS JSON, vendor CSV
  and manual JSON import; whole-batch rejection and no raw import retention.
- Tenant-scoped FastAPI, evidence-linked findings, explainable priority bands,
  proposed human-owned migration waves, deterministic reports, and a
  hash-chained local audit log.
- Optional PostgreSQL metadata persistence with SQLAlchemy and Alembic; local
  Next.js Command Center with ten evidence surfaces, responsive layout and
  reduced-motion support. Docker Compose binds web/API only to loopback.
- Product charter, standards profile, canonical observation schema, security
  architecture, threat model, service blueprint, positioning, commercial
  hypotheses, pilot outline and evaluation preregistration.

## Run locally on Windows

```powershell
Set-Location "C:\JeanLoa\Path-AI-Engineer\Quantum-First-Business-Product-Developer-Platform\56-post-quantum-security-product-blueprint"
.\scripts\setup.ps1
.\scripts\quality-gate.ps1
```

The quality gate runs Python lint, formatting, strict types, tests, contract
syntax, web TypeScript/lint/build and 15 Playwright flows across desktop,
tablet and mobile. If Docker is available, `docker compose up --build -d`
starts PostgreSQL, API and web; stop with `docker compose stop` (volumes are
retained). Local app: `http://127.0.0.1:3056`. Local API documentation:
`http://127.0.0.1:8056/docs`.

`X-Demo-Identity` selects one of 12 fictional identities such as
`demo-northstar-owner`. It is **not authentication**. Neither the API nor web
app may be exposed publicly or used with real company data. The default
Compose password is a documented disposable local placeholder, not a secret
for production.

## Acceptance status

Technical checks are distinguished from human evidence. Automated 45-import,
72-authorization, 24-priority, 18-report and 12-browser cases are synthetic
regression checks. They are **not** an unopened blinded gold evaluation, human
usability study, real pilot, security certification or signed executive
decision. The preregistered final gold set, production security hardening,
customer validation, pricing validation and final proceed/pivot/stop approval
remain outside the current synthetic demonstration. See
[`docs/evaluation/PREREGISTRATION.md`](docs/evaluation/PREREGISTRATION.md) and
[`docs/security/THREAT_MODEL.md`](docs/security/THREAT_MODEL.md).

The root Plan 10 repository still has older differently numbered
`56-enterprise-ai-product-line` and `57-post-quantum-security-product-blueprint`
placeholders. This directory follows the updated map supplied for Project 56;
the legacy folders are intentionally untouched.
