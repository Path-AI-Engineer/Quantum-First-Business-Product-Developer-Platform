# Threat model

| Threat | Control | Verification |
|---|---|---|
| Broken object authorization | Project-bound repository lookups and deny by default | Cross-tenant negative tests |
| Leaked or overprivileged API keys | One-time reveal, PBKDF2 hash-at-rest, scopes, revoke/rotate | Key lifecycle tests and sensitive scan |
| Idempotency poisoning/job replay | Request fingerprint bound to tenant, environment, endpoint key | Conflict and replay tests |
| Duplicate provider side effects | Pre/post submission identity ledger and reconciliation state | Fault-state tests |
| Webhook forgery/replay | HMAC-SHA256, timestamp window, delivery identity, constant-time compare | Forged, stale, altered-body tests |
| SSRF | HTTPS or loopback fixture allowlist | Denied metadata endpoint test |
| Artifact abuse | Content address, checksum, media boundary, tenant ownership | Integrity tamper tests |
| Quota bypass | Atomic policy decision boundary and append-only deduplicated usage | Limit/reconciliation tests |
| Secret/log leakage | Structured redaction policy and repository sensitive scan | Gate scan |

Residual risks: prototype in-memory persistence, no external identity provider, no penetration test, no production egress proxy, and no live provider certification.

