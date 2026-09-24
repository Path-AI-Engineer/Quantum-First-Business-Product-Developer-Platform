# Operations, recovery, and support

## SLO hypotheses

These are prototype targets, not production SLO commitments: portfolio read 99% under 750 ms locally; approval decision 99% under 500 ms locally; evidence lineage 99% complete; reports reconcile exactly with the frozen domain fixture.

## Correlation and telemetry

Every cross-module event contains tenant ID, correlation ID, event ID, type, subject, and source. Logs and traces must never contain secrets, prompt bodies, or raw restricted artifacts. Tenant-safe support bundles include identifiers, timestamps, reason codes, hashes, and version metadata only.

## Failure runbooks

- Event delay/out of order: pause projections, replay the deduplicated inbox, and re-evaluate current policy before any action.
- API unavailable: preserve request idempotency key; do not infer success.
- Object store unavailable: retain the evidence reference as unavailable; do not issue a recommendation without citations.
- Report mismatch: mark report invalid, compare source counts, regenerate from immutable fixtures.
- Suspected tenant leak: engage the simulated kill switch, preserve sanitized audit evidence, and invalidate affected exports.
- AI degradation: disable model candidate, return deterministic baseline or abstain.

## Backup/restore fixture

The reproducible corpus generator is the backup fixture. Recovery rebuilds exactly 3 tenants, 30 identities, 15 units, 180 evidence records, 12 opportunities, 9 experiments, and 36 decision scenarios. Hashes in the final candidate bundle identify contract and report inputs.

## Migration/rollback

Compatible additions use a minor contract revision. Breaking changes require a new major route/schema, migration note, dual-read window, consumer evidence, and explicit rollback. No migration is auto-applied to a real system.

