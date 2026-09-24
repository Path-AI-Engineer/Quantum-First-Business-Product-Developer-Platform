# Source policy — public evidence, bounded claims

The source register records URL, publisher, publication date when known, access
date, industrial/geographic scope, access caveat and primary/secondary class.
The research corpus was reviewed on 2026-09-12. Undated living documentation has
no fabricated publication date. No source substitutes for direct buyer evidence.

Each external claim needs sources, an access date, scope, validity, owner and
review date. Paraphrases are short and cite a section locator; no scraped full
articles or copied standards are shipped.

| Confidence | Interpretation | Permitted conclusion |
|---|---|---|
| C0 | Intuition / unmeasured hypothesis | Experiment proposal only |
| C1 | Secondary signal | Tentative inference |
| C2 | Multiple independent sources | Corroborated fact within scope |
| C3 | Primary document or reproducible measurement | Documented fact within scope |
| C4 | Direct validation with buyers | Not available in this project |

Repeated C0/C1 material cannot become a fact. C2 requires independent publishers;
C3 facts require primary supporting provenance. Pydantic validates semantic
conditions in addition to JSON Schema. Unknown budget/access remains null.

## Reading boundaries and dissent

- NIST standards document technical capability, not demand for our service.
- The 2023 CISA/NSA/NIST readiness guide is accessed through the official NSA
  hosted PDF because the CISA landing page returned HTTP 403. Historical
  pre-final-standard wording is not treated as today's standards status.
- US guidance is not a universal legal obligation in every jurisdiction.
- Vendor documentation supports that a feature is offered; it does not prove
  independent performance, market share, purchasing intent or competitiveness.
- FinOps framework concepts retain attribution to the FinOps Foundation
  (CC BY 4.0 where stated). This repository does not imply endorsement.
- No contacts, PII, interviews, revenue, paid pilots or measured TAM are included.

Evidence stance means support/contradiction/context relative to the venture
thesis, not whether the source's technical statement is true or false.
For example, available vendor PQC support is a documented fact and simultaneously
counterevidence to differentiation. Preserve that distinction in reviews.

## Maintenance

Edit `scripts/build_research.py`, deliberately regenerate the canonical corpus
and inspect the diff. Re-run all gates after material changes. Reports and
category indexes are derived views, not separate sources of truth.
`venture evidence lint` checks identifiers, coverage and lineage.
The freshness report flags overdue claims; it never extends their dates.
Before approving a stale candidate, revisit the actual source and record the new
review. Historical source hashes preserve a local snapshot, not remote-page authenticity.
