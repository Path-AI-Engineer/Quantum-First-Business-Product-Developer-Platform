# Standards profile — Day 1562

Checked against publisher pages on 2026-09-14. Machine-readable snapshot:
[`standards-profile.v1.json`](../../contracts/standards-profile.v1.json).
This is a source-status and product-scope record, not implementation
certification or legal applicability advice. Re-check official versions and
errata before a release or organization-specific recommendation.

| Source | Status checked | Role in the prototype |
| --- | --- | --- |
| [FIPS 203](https://csrc.nist.gov/pubs/fips/203/final) | Final, August 2024; publisher lists potential errata | ML-KEM reference for key-establishment observations, not proof an implementation is correct |
| [FIPS 204](https://csrc.nist.gov/pubs/fips/204/final) | Final, August 2024; potential errata noted July 2026 | ML-DSA reference for digital-signature observations |
| [FIPS 205](https://csrc.nist.gov/pubs/fips/205/final) | Final, August 2024 | SLH-DSA reference for digital-signature observations |
| [SP 800-227](https://csrc.nist.gov/pubs/sp/800/227/final) | Final, September 2025 | KEM implementation/use guidance; outside the assessment engine's ability to certify |
| [CSWP 39upd1](https://csrc.nist.gov/pubs/cswp/39/upd1/considerations-for-achieving-crypto-agility/final) | Final update, June 2026 | Crypto-agility design and operational trade-offs; supersedes the older CSWP 39 |
| [IR 8547](https://csrc.nist.gov/pubs/ir/8547/ipd) | Initial public draft, November 2024; no final publication confirmed | Watch-list input only. No draft timetable becomes an unconditional customer deadline |

The [NCCoE migration project](https://www.nccoe.nist.gov/applied-cryptography/migration-to-pqc)
separates cryptographic discovery/inventory from interoperability work. That
supports the proposed product split between evidence collection and a later
human-run lab. The [CISA/NSA/NIST quantum-readiness fact sheet
(2023)](https://www.cisa.gov/sites/default/files/2023-08/Quantum-Readiness%20-%20Migration%20to%20Post-Quantum%20Cryptography_508c.pdf)
supports early program ownership, inventory and supplier engagement; its date
is explicit and it is not treated as a 2026 standard.

The 2035 figure discussed on NIST's [PQC project
overview](https://csrc.nist.gov/projects/post-quantum-cryptography/) refers to
NIST's transition planning for quantum-vulnerable algorithms in its standards.
Because the detailed [IR 8547](https://csrc.nist.gov/pubs/ir/8547/ipd)
remains a draft on this check, the prototype must not apply that figure as a
universal or binding deadline to every customer.

## Revalidation rule

Store the publisher URL, document identifier, observed status and check date
with each standards entry. A changed publication, supersession, withdrawal or
erratum generates a new catalog version and an affected-finding review.
Historical assessment evidence is never silently rewritten. If the source
cannot be checked, mark it `status_unverified` and suppress dependent
normative claims until reviewed.
