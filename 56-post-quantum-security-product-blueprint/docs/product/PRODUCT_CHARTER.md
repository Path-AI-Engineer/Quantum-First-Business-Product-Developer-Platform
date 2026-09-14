# Product charter — Day 1562 exploration

Status: candidate for human review, 2026-09-14. This document starts the
research track; it does not attest the student's timed cycles or approval of
Project 55's handoff.

## Decision to support

Organizations with long-lived data and incomplete cryptographic inventories
need to decide where to investigate and plan migration first. The
Cryptographic Migration Command Center will connect each recommendation to a
specific asset, observation, source, owner, uncertainty and acceptance
evidence. It will support a human program owner; it will not execute
cryptographic changes.

The initial use cases are regulated long-lived applications, software vendors
with crypto-agility obligations, and IT/OT estates with slow replacement
windows. This is an ICP hypothesis. It is not evidence of buyer interviews,
market demand or product-market fit.

## Users and jobs

| Role | Decision or job | Needed evidence |
| --- | --- | --- |
| Security program owner | Scope the readiness program and migration waves | Coverage, unresolved unknowns, owners and blockers |
| Cryptography architect | Verify mechanism and migration path | Algorithm, protocol, implementation, provenance and compatibility limits |
| Application owner | Plan change windows and acceptance | Service dependencies, data lifetime, vendor commitments and test plan |
| PKI/infrastructure owner | Locate certificates, keys and external dependencies | Metadata only, source freshness and replacement constraints |
| Risk/compliance reviewer | Challenge priority and exceptions | Factors, confidence, conflicting evidence and auditable decisions |
| Executive sponsor | Choose funding and sequencing | Aggregate exposure, progress, uncertainty and named responsibility |
| External assessor | Review an authorized scope | Read-only, redacted evidence and export provenance |

## Product boundary

The proposed prototype accepts offline CBOM/SBOM, TLS certificate inventory,
SARIF, cloud/KMS and vendor-questionnaire **fixtures**, plus manually entered
synthetic evidence. It normalizes observations, preserves contradictory or
missing evidence, produces findings, ranks migration actions by explicit
factors, and exports technical and executive views.

Its knowledge states are `verified`, `inferred`,
`declared_by_vendor`, `conflicting`, `unknown` and `stale`.
Unknown and conflicting are never synonyms for safe. Priority bands describe
decision order, not an invented probability that a quantum attack occurs.

Discovery, verification and planning are the prototype's actionable phases.
Laboratory testing, staging, migration, validation and monitoring are only
represented as proposed human workflow states. No endpoint in this project may
rotate a key, modify a certificate, alter a protocol or scan an external host.

## Testable product outcome

The final candidate should let an authorized reviewer ingest the three
synthetic organizations, trace every finding to evidence, distinguish
unknowns and conflicts, assign a migration owner/dependency/acceptance
artifact, compare posture between assessments and reproduce reports. The
declared corpus target is 125 assets, 220 observations, 35 dependencies, 28
owners and 30 gold findings. These are future fixture targets, **not current
counts**.

Business packaging and pricing remain hypotheses. The application does not
replace cryptographic engineering review, legal advice or compliance
assessment. A signed proceed/pivot/stop decision and the final
`pqc-product-blueprint-v1` require a real reviewer; this file cannot approve
them.

## Relationship to the prior project

Project 55 proposed a post-quantum readiness wedge but its handoff is still
`pending_human_review`. This exploration uses only the new public brief and
public references. It neither imports an unapproved bundle nor marks the
preceding thesis as approved. Source code and state from the Software
Engineer track remain untouched.
