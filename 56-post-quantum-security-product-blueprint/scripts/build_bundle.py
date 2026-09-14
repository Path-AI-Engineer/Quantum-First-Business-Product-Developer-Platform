"""Reproducible technical candidate; human approval is never synthesized."""

import argparse
import hashlib
import json
from pathlib import Path
from typing import cast

from pqc_product.corpus import build_corpus
from pqc_product.engine import evaluate, migration_actions
from pqc_product.reporting import build_report

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports" / "week-226" / "pqc-product-blueprint-v1-candidate.json"
INCLUDE = (
    "README.md",
    "pyproject.toml",
    "compose.yaml",
    "Dockerfile.api",
    ".dockerignore",
    ".gitignore",
    "alembic.ini",
    "apps/web/package.json",
    "apps/web/package-lock.json",
    "apps/web/tsconfig.json",
    "apps/web/next.config.ts",
    "apps/web/playwright.config.ts",
    "apps/web/Dockerfile",
    "apps/web/.dockerignore",
    "apps/web/next-env.d.ts",
    "apps/web/eslint.config.mjs",
)
DIRECTORIES = ("src", "contracts", "data/fixtures", "docs", "migrations", "scripts", "apps/web/app", "apps/web/tests")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def inputs() -> dict[str, str]:
    files = [ROOT / name for name in INCLUDE]
    for directory in DIRECTORIES:
        files.extend(path for path in (ROOT / directory).rglob("*") if path.is_file())
    return {
        path.relative_to(ROOT).as_posix(): sha256(path.read_bytes())
        for path in sorted(set(files))
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    }


def build() -> dict[str, object]:
    corpus = build_corpus()
    findings = evaluate(corpus.assets, corpus.evidence)
    actions = migration_actions(findings)
    if not set(corpus.gold_finding_asset_ids) <= {finding.asset_id for finding in findings}:
        raise ValueError("known development positives are missing")
    if any(not finding.evidence_ids for finding in findings):
        raise ValueError("untraceable finding")
    if any(f.band != "verify" for f in findings if f.knowledge in {"unknown", "conflicting"}):
        raise ValueError("unknown or conflicting evidence was treated as resolved")
    tenant_reports = {}
    for tenant in ("northstar", "aster", "harbor"):
        asset_set = tuple(asset for asset in corpus.assets if asset.tenant_id == tenant)
        evidence_set = tuple(item for item in corpus.evidence if item.tenant_id == tenant)
        finding_set = tuple(f for f in findings if f.tenant_id == tenant)
        action_set = tuple(a for a in actions if a.tenant_id == tenant)
        tenant_reports[tenant] = build_report(tenant, "executive", asset_set, evidence_set, finding_set, action_set)
    source_hashes = inputs()
    return {
        "bundle_id": "pqc-product-blueprint-v1",
        "status": "technical_candidate_unapproved",
        "synthetic": True,
        "approval": None,
        "source_snapshot_sha256": sha256(json.dumps(source_hashes, sort_keys=True).encode()),
        "source_files": source_hashes,
        "corpus": {
            "organizations": 3,
            "assets": len(corpus.assets),
            "observations": len(corpus.evidence),
            "dependencies": len(corpus.dependencies),
            "owners": len(corpus.owner_ids),
            "known_development_positives": len(corpus.gold_finding_asset_ids),
            "emitted_findings": len(findings),
        },
        "tenant_reports": tenant_reports,
        "limitations": [
            "no blinded gold evaluation",
            "no human usability study",
            "no customer pilot",
            "no production auth or security certification",
            "no executive proceed/pivot/stop decision",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    candidate = build()
    if args.verify:
        if not OUTPUT.is_file() or json.loads(OUTPUT.read_text(encoding="utf-8")) != candidate:
            raise SystemExit("Candidate bundle is missing or stale; run scripts/build_bundle.py after source changes")
        print(
            json.dumps(
                {"status": "verified_candidate", "source_files": len(cast(dict[str, str], candidate["source_files"]))}
            )
        )
        return
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": candidate["status"], "file": OUTPUT.relative_to(ROOT).as_posix()}))


if __name__ == "__main__":
    main()
