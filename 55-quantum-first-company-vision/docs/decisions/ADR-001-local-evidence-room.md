# ADR-001 — Local Next.js + FastAPI evidence room

Status: implemented architectural decision, separate from business approval.

Choose Next.js/TypeScript over Streamlit because ten navigable evidence surfaces,
keyboard/mobile acceptance, browser downloads and scenario controls benefit from
explicit UI state. FastAPI remains a read-only loopback API. Python performs
scoring and economics; the browser never independently invents business results.
Pandas generates the scenario CSV; Pydantic and Draft 2020-12 schemas define
contracts. Typer offers the same operations without a browser.

The web module separates domain contracts, application state, infrastructure
fetches and presentation. Components call the application hook, not HTTP.
The Next proxy has a fixed loopback destination and allowlisted read endpoints.
There are no mutation endpoints, external URL proxy parameters, provider keys or
remote databases. Bind only 127.0.0.1; this is not a production authentication boundary.
Preview should not be exposed through a tunnel or public network.

Frontend dependencies are locked. Next 16.3.1 from older projects was not retained:
the maintainer's [Windows security advisory](https://github.com/vercel/next.js/security/advisories/GHSA-p293-qw3h-jr36)
lists it as affected. Project 55 uses 16.3.5 and audits the resolved tree.
Other projects were not modified. Production E2E uses a normal `next start`
build without `output: standalone`, avoiding the incompatible startup pattern.

## Execution and artifact isolation

Python 3.13, Node 22+ and local PowerShell are sufficient. Docker is optional in
the map and intentionally not required. Azure deployment is outside the local
biz-lab scope. No GPU, two-week training pipeline or cloud spend.

Checksummed lineage covers research/scoring source, canonical data and protocol,
not transient Next build paths. Browser compilation must not invalidate the
business evidence. A changed research source requires an explicit new candidate
export; the verifier never silently rewrites digests.

The ZIP has stable member order/timestamps and validated payloads. SHA-256
detects accidental change; it is not a signature or proof of author identity.
The receiving team must separately review/approve a version.
