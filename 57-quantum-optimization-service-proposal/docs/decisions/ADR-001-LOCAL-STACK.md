# ADR-001 — Local metadata and web stack

## Decision

Use DuckDB for local experiment metadata and Next.js with TypeScript for the Validation Lab.

## Rationale

DuckDB provides a zero-credential, file-backed local database suitable for reproducible experiment metadata without creating a cloud dependency. Next.js supports the ten evidence surfaces, keyboard navigation, API proxying, and responsive validation while keeping domain and solver logic in Python.

## Consequences

- This is not a production concurrency or identity architecture.
- `X-Demo-Identity` demonstrates role boundaries only and is forgeable.
- Production adoption requires managed identity, tenant authorization, backups, observability, and a reviewed database migration plan.
