# Project 56 evidence disposition — 2026-09-14

Status: **synthetic technical candidate**, not approved product closure.

| Gate | Evidence observed | Disposition |
| --- | --- | --- |
| Corpus cardinality | 3 organizations, 125 assets, 220 observations, 35 dependencies, 28 owner IDs, 30 development positives | Verified in tests |
| Import fail-closed | 45 distinct malformed/adversarial cases, whole-batch cross-tenant rejection, seven connector fixtures | Verified in synthetic tests |
| Tenant authorization | 72 API cases plus 72 policy cases over 12 fictional identities | Verified for demo header only; production auth not verified |
| Evidence trace | Every emitted finding has evidence IDs and tenant/asset scope | Verified in synthetic tests |
| Unknown/conflicting | Verify-first band; no safe label | Verified in synthetic tests |
| Risk ordering | 24 pairwise regression cases plus vendor/lead/stale regression | Verified in development set; not blinded gold |
| Report reconciliation | 18 source-to-report cases, deterministic digest | Verified in synthetic tests |
| Evidence delta | Before/after synthetic import, changed band explicitly not called migration success | Verified in synthetic API test |
| Object storage | Generated report content-addressing and digest readback | Verified in local test; no production retention policy |
| Audit concurrency | 24 simultaneous read requests retain a serial hash chain | Verified in process-local test; distributed writers not tested |
| Sensitive material | Pattern scan over bundle inputs finds no key PEM, common token or email pattern | Verified for those patterns only; not a complete DLP review |
| Browser journeys | 15 Playwright flows across desktop/tablet/mobile | Verified automation; human task success not measured |
| PostgreSQL | Compose build, Alembic upgrade, proxy/tenant smoke, report restore after API restart | Verified locally; no backup/restore drill |
| No active mutation | No network scanner, key, certificate or protocol mutation endpoint | Verified by route test and design review; independent security review pending |

`ruff`, `mypy`, `pytest` (252 passing tests), TypeScript, ESLint, production Next build and
Playwright are local quality gates. Warnings from upstream Starlette/httpx
test-client deprecations do not change test assertions. The candidate manifest
hashes source files and reconciled per-tenant reports; it is not a signature
of human approval.

Not verified: unopened gold accuracy/precision/recall, real-user usability,
real tenant identity, parser sandboxing, durable tamper-resistant audit,
customer/industry interviews, commercial willingness-to-pay, pilot security
acceptance and executive proceed/pivot/stop decision. No customer data,
deployment or external security claim is authorized by this evidence.
