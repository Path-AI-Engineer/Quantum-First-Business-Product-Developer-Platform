# Evaluation preregistration — Day 1562

Recorded before creating the synthetic gold corpus or implementing the
assessment engine. Status: protocol candidate; no test outcome or human
approval is claimed. Freeze this protocol before opening the final gold cases;
record amendments and their rationale rather than editing historical results.

## Target corpus and isolation

Generate three expressly fictional organizations with 45, 38 and 42 assets,
respectively; 125 assets total, 220 crypto observations, 35 system
dependencies, 28 owners and 30 known findings. Include positive, negative,
conflicting, unknown and deliberately misleading observations. No real
corporate data, PII, certificates, private keys or production endpoints.

Keep implementation fixtures and gold evaluation cases separate. The
malformed-import, authorization, risk-ordering and report-reconciliation gold
sets receive immutable IDs and source hashes before execution. Do not tune
rules on their observed failures without versioning a new protocol and
reporting the original results.

## Acceptance questions and thresholds

| Question | Planned evidence | Pass condition |
| --- | --- | --- |
| Can an import fail closed? | 45 malformed/adversarial fixture imports | Every invalid type, schema or size is rejected with no accepted partial record |
| Is tenant isolation enforced? | 72 authorization cases across three tenants and 12 synthetic identities | Zero cross-tenant reads/writes; deny by default |
| Are findings traceable? | 30 gold findings, evidence ledger and exported reports | 100% of emitted findings have an evidence path, scope and knowledge state |
| Are unknown/conflicting states handled honestly? | Negative and contradictory observations | Neither state is rendered or scored as “safe” |
| Is priority ordering explainable? | 24 declared pairwise cases | All pairs match gold order or have a reviewed, documented exception; no opaque probability |
| Do reports reconcile? | 18 source-to-report cases | Totals and versions match the source snapshot; exports reproduce byte-for-byte given fixed inputs |
| Is the product usable? | 12 scripted tasks over authorized fixture data | Record completion, errors and accessibility findings; no success claim before execution |
| Does the app leave systems alone? | Endpoint and code-path review plus negative tests | No active scan, exploitation, key rotation, certificate or protocol mutation |

Coverage, precision/recall, unknown reduction and time-to-triage are measured
on the gold set and shown with denominator and missing-data notes. The brief
does not predeclare a precision threshold; a threshold must be approved before
opening the final set, not invented after inspecting scores. A human reviewer
also records the proceed/pivot/stop decision for the eventual blueprint.
