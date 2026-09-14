# Architecture baseline — candidate v0.1

## Executable boundary

The prototype is a local-only, fixture-driven command center. FastAPI serves a
synthetic corpus, bounded offline imports, explainable findings, human-owned
actions, report exports and hash-chained audit events. Next.js presents the
same tenant-scoped API through a same-origin proxy. SQLAlchemy stores imported
metadata, decisions, waves, reports and audit rows in PostgreSQL through an
Alembic migration when `PQC_DATABASE_URL` is set. Without that variable,
state remains process-local for tests and quick demonstrations. The process
can also store generated synthetic reports in a content-addressed local object
directory; raw uploads are discarded. It has no scanner, key rotation, certificate update, migration executor or
production connector.

`import -> validate whole batch -> normalize -> evidence IDs and SHA-256 ->
resolve by tenant/asset -> conflicting/unknown states -> findings -> actions ->
reconciled reports`.

Trust boundaries: browser to local Next proxy; proxy to local API; API to
synthetic corpus and local metadata store. `X-Demo-Identity` is an overt
fixture selector, not authentication. Do not expose either process outside
loopback. Tenant IDs are applied before reads, writes and exports, but this
does not substitute for a production identity provider or row-level security.

## Production requirements, not prototype claims

- Harden PostgreSQL with row-level policies, constrained foreign keys,
  backup/restore tests and per-tenant key management. The prototype has
  tenant-keyed tables and transactional import, but no production hardening.
- Object storage for evidence metadata with immutable version IDs, access
  logging, retention, and verified deletion. Raw imports are not persisted by
  the prototype.
- Work queue with retry/idempotency and per-tenant quotas. Background import
  jobs are not yet implemented; bounded synchronous batches are the deliberate
  local choice.
- Real OIDC/OAuth identity, policy-as-code/RBAC, scoped application ownership,
  row-level security and security review before network exposure.
- Parser sandboxing, virus/content scanning, upload streaming limits, PII
  redaction, tamper-evident durable audit and export watermarking.
- A controlled standards update workflow; publisher pages remain source of
  truth and historical snapshots are append-only.

## Decisions

| ADR | Choice | Reason | Revisit trigger |
| --- | --- | --- | --- |
| 001 | Synthetic corpus generated deterministically in Python | Prevent real identifiers/secrets and keep exact counts reproducible | Approved pilot data contract |
| 002 | Optional local PostgreSQL metadata persistence | Prove restart behavior while discarding raw uploads | Pilot authorization and database threat review |
| 003 | Human-owned migration plans only | Prevent unreviewed production changes | Separate remediation product authorization |
| 004 | Priority bands, no probability | Avoid precision unsupported by evidence | Gold calibration and reviewer approval |
| 005 | Next.js and FastAPI on loopback | Accessible journeys without external connectivity | Production deployment decision |

## Domain and API contract

Domain records in `src/pqc_product/domain.py` carry `tenant_id`, synthetic IDs,
provenance, source hash, knowledge state and linked evidence. API route names
match the map under `/v1`. OpenAPI is generated at `/openapi.json`; its schema
must be reviewed before any external integration. This is a prototype
contract, not a promise of backward compatibility.
