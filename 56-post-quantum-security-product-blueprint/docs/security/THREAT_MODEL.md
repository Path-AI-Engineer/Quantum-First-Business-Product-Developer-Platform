# Security and privacy threat model — candidate

Scope: local synthetic data only. No external connectors or production assets.

| STRIDE / abuse | Boundary | Prototype control | Residual production requirement |
| --- | --- | --- | --- |
| Spoofing demo identity | Browser/API | Explicit synthetic identities; default deny | OIDC, MFA and trusted token validation |
| Tamper with evidence | Import/API | Whole-batch validation, SHA-256, source IDs | Durable immutable object versions and signatures |
| Repudiate decision | Decision API | Actor/rationale and hash-chained process log | WORM/durable audit and independent verification |
| Information disclosure | Tenant reads/exports | Tenant filters, scoped app owner, no raw key material | DB row-level policies, field redaction and DLP |
| Denial of service | Parser | 64 KB and 250-record limit | Streaming ingress, quotas and sandbox workers |
| Privilege escalation / IDOR | Object URLs | Object lookup only after tenant filtering | External penetration test and policy review |

The demo header is forgeable by design. The prototype MUST NOT be deployed to
Azure or made reachable on a LAN. No customer information, PII, real
certificates, private keys or endpoint URLs are accepted. A report is a
planning artifact, not a compliance determination. Unknown/conflicting source
states cannot be converted to safe by a UI display rule.

Critical test evidence: `tests/test_product.py` covers deny-by-default,
cross-tenant API access, whole-batch rejection, evidence links and the absence
of mutation endpoints. The 72 HTTP authorization cases are synthetic
regressions; an independent security review is still required for a pilot.
