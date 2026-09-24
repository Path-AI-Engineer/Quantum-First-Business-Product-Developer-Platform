# ADR-001 — Evidence-driven platform evolution

Status: accepted for the technical candidate.

## Decision

Year 1 uses a modular control plane, PostgreSQL, object storage, a queue/cache, OCI containers, OpenAPI 3.1, local provider fakes, isolated adapters, and OpenTelemetry. PostgreSQL is the production system of record; canonical JSON is the reproducible local review/export format.

Year 3 permits bounded-context extraction, durable asynchronous flows, stronger tenant isolation, DR/residency options, or a platform team only when adoption, reliability, isolation, economics, and operating-load thresholds justify them.

Kubernetes is evaluated against 12 dimensions: demand, latency, job duration, state, isolation, compliance, residency, skills, on-call burden, cost, portability, and exit. It is not a default.

Year 10 preserves provider-neutral interfaces and permits specialized quantum adapters, scheduling, ecosystem, or sovereign options only after resource, advantage, and TCO gates pass.

## Consequences

- No big-bang rewrite.
- Every provider choice includes an exit plan and evidence export.
- Complexity remains a gated cost, not a maturity badge.

