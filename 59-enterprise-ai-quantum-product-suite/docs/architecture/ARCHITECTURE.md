# Architecture and context map

## Decision

ADR-001 chooses a contract-first modular monolith for the reference implementation. The deployment is deliberately simple; the domain boundaries are not. Each bounded context owns its language and future persistence boundary. Contexts exchange versioned APIs and CloudEvents. There is no shared database-table contract and no fictional distributed transaction.

## Layers

1. Experience: enterprise portal, developer surface, and executive portfolio.
2. Shared control plane: tenancy/IAM, catalog, explicit policy and approvals, evidence/audit, usage/quota, reports.
3. Domain contexts: crypto readiness, optimization studio, and quantum workbench.
4. Platform: gateway, Redis Streams event model, workflow adapters, PostgreSQL, S3-compatible artifacts, and OpenTelemetry.

## Shared kernel

Only organization, workspace, identity, role/permission, policy, approval, resource reference, evidence, event, audit, usage/quota, risk, decision, and report have common semantics. Domain IDs remain local. Global references are limited to organization, workspace, identity, and evidence.

## Context ownership and mappings

| Context | Owns | Consumes through anti-corruption mapping |
|---|---|---|
| Crypto readiness | findings, assets, proposed migration waves | shared evidence, approval, catalog refs |
| Optimization | opportunities, formulations, benchmarks | shared evidence, quota, decision refs |
| Quantum execution | capabilities, sandbox jobs, artifacts | approval, usage, experiment refs |
| Portfolio/governance | risks, decisions, reports | stable projections from all contexts |
| Developer platform | contract discovery, request lifecycle | catalog capability and policy decisions |

All projections are eventually consistent. Outbox/inbox semantics give deduplication and correlation. Delayed events never authorize an action; current policy and approval must still be evaluated at the action boundary.

## Storage and messaging ADRs

- ADR-002: PostgreSQL represents durable transactional state per context in the blueprint; the reference process uses in-memory repositories so tests remain deterministic.
- ADR-003: Redis Streams is the local event backbone because consumer groups and replay are sufficient for this bounded prototype. AsyncAPI is the public event contract.
- ADR-004: LocalStack S3 is the S3-compatible local artifact store; artifact references are tenant-scoped and checksummed.
- ADR-005: policy is explicit Python in the reference and deny-by-default. A future OPA adapter is possible but is not implied to exist.

The implementation imports no runtime code from Projects 56–58.
