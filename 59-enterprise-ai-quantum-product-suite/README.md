# Enterprise Quantum Intelligence Suite

Project 59 is a self-contained, contract-first technical reference that unifies four independently usable modules: Crypto Readiness, Optimization Studio, Quantum Workbench, and Shared Governance. It demonstrates how synthetic enterprises can move from evidence to a human-owned decision without confusing recommendation, authorization, or execution.

## Verified scope

- Three synthetic tenants, 30 identities, 15 business units, 180 evidence records, 12 optimization opportunities, 9 experiment templates, and 36 decision scenarios.
- Deny-by-default tenant and object authorization; revision/scope/budget-bound approvals with expiry and replay resistance.
- OpenAPI, JSON Schema, AsyncAPI, and CloudEvents contracts with deterministic local API behavior.
- Evidence-grounded deterministic assistant with citation, abstention, injection checks, and zero side effects.
- Ten-view responsive enterprise portal.
- A deterministic 687-case evaluation protocol and a checksummed handoff candidate.
- Docker Compose topology for PostgreSQL, Redis Streams, LocalStack S3-compatible storage, OpenTelemetry, API, and portal.

## Explicit boundaries

This is a `technical_candidate_unapproved`, not a production system. All organizations, people, records, usage, and outcomes are synthetic. It makes no compliance, customer, realized ROI, production-readiness, or quantum-advantage claim. No real provider, infrastructure, credential, migration, or operational action is executed. `enterprise-suite-contracts-v1` remains a candidate until an authorized external reviewer approves it; invest/hold/kill module decisions also remain pending.

## Run

```powershell
Set-Location "C:\JeanLoa\Path-AI-Engineer\Quantum-First-Business-Product-Developer-Platform\59-enterprise-ai-quantum-product-suite"
.\scripts\setup.ps1
.\scripts\quality-gate.ps1
```

Optional container runtime validation (requires Docker Desktop Linux engine):

```powershell
.\scripts\container-smoke.ps1
```

The API exposes Swagger at `http://127.0.0.1:8059/docs` when run locally. The portal uses `http://127.0.0.1:8959`.

## Evidence

- [Product and packaging](docs/product/PRODUCT_AND_PACKAGING.md)
- [Architecture and context map](docs/architecture/ARCHITECTURE.md)
- [Threat model](docs/security/THREAT_MODEL.md)
- [Operations and recovery](docs/operations/RUNBOOKS.md)
- [Evaluation protocol](docs/decisions/EVALUATION_PROTOCOL.md)
- [Validation status](docs/decisions/VALIDATION_STATUS.md)
