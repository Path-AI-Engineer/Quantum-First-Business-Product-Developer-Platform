# Threat model and AI boundaries

## Assets and trust boundaries

Tenant identities, policy decisions, approvals, evidence, artifacts, audit events, usage records, reports, and model prompts cross the portal, API, control plane, domain contexts, event transport, and storage boundaries. The reference uses only synthetic data and local adapters.

| Threat | Preventive control | Detection/recovery evidence |
|---|---|---|
| Cross-tenant/BOLA | tenant + workspace + object authorization | 240-case matrix; deny reason codes |
| Overprivileged service identity | separate service roles; action restriction | policy audit |
| Evidence poisoning | checksum, provenance, confidence, human review | broken-lineage checks |
| Prompt injection | marker/adversarial tests; scoped retrieval; abstention | 72 AI cases |
| Policy bypass | deny default; server-side evaluation | decision audit |
| Approval replay | bind tenant/resource/revision/scope/budget; consume | replay cases |
| Forged event | typed schema, event ID, dedupe, future signature adapter | inbox record |
| Artifact leakage | tenant-scoped refs and support bundle | secret scan |
| Quota abuse | append-only usage and explicit quota decision | showback reconciliation |
| Secret in telemetry | allowlisted attributes; scan | sanitized support bundle |
| Stale standards claim | dated standards profile and revalidation | contract migration note |
| Report inconsistency | source-count reconciliation | 30 report cases |

## AI control contract

The deterministic baseline retrieves only tenant-scoped evidence, returns structured citations, and abstains on incomplete or adversarial context. A model-assisted candidate is intentionally disabled in this local reference. Any future model/provider/version must be recorded with its data boundary and fallback. AI cannot grant approvals, change migration state, execute a solver/job, modify quota, transmit to providers, or make a final operating decision.

Kill switches disable AI candidates and external adapters independently. Deterministic workflows remain available.

