# Project 58 — Quantum Developer Platform Reference Lab

An executable, local-first reference design for quantum-ready developer productization. It demonstrates stable contracts, tenant boundaries, one-time API credentials, asynchronous job semantics, safe idempotency, provider capability discovery, artifact integrity, signed webhooks, quotas, usage reconciliation, SDK parity, and an evidence-driven developer portal.

## Run the verified local closure

```powershell
Set-Location "C:\JeanLoa\Path-AI-Engineer\Quantum-First-Business-Product-Developer-Platform\58-quantum-developer-platform-design"
.\scripts\complete-project.ps1
```

Add `-IncludeContainers` only when Docker Desktop Linux is running. The standard gate always validates the Compose model; the explicit flag adds the full integration smoke.

## Product boundaries

- `fake` and `local` providers execute deterministically without cloud credentials.
- IBM Quantum, Amazon Braket, and Azure Quantum are explicit contract stubs. No live cloud job is part of the gate.
- The local sampler is bounded to allowlisted `circuit.sample` / `observable.estimate` workloads. Arbitrary Python, shells, user containers, and remote commands are rejected by design.
- Usage and pricing are laboratory fixtures, not invoicing. SLOs are test targets, not commercial SLAs.
- The final bundle status is `technical_candidate_unapproved`; named architecture, security, product, and commercial approvals are external decisions.

## Evidence surfaces

- HTTP: `contracts/openapi/openapi.v1alpha1.json`
- Events: `contracts/asyncapi/asyncapi.v1alpha1.json`
- Standards freeze: `contracts/standards-profile.v1.json`
- Threat model: `docs/security/THREAT_MODEL.md`
- TTFS protocol: `docs/dx/TTFS_PROTOCOL.md`
- Evaluation: `reports/week-233/evaluation.v1.json`
- Candidate: `reports/week-233/developer-platform-design-v1-candidate.json`

## Stack

FastAPI/Pydantic, Next.js/TypeScript, typed Python and TypeScript SDK layers, OpenAPI/AsyncAPI/JSON Schema, PostgreSQL, Redis Streams, MinIO, OpenTelemetry Collector, Docker Compose, pytest, mypy, Ruff, ESLint, and Playwright.

## Standards revalidated on 2026-09-18

- OpenAPI 3.1.1 and JSON Schema 2020-12
- AsyncAPI 3.0.0 and CloudEvents 1.0.x
- OpenTelemetry semantic conventions 1.44.0 and W3C Trace Context
- RFC 9457-compatible Problem Details envelope

