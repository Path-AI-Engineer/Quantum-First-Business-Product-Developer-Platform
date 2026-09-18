from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports" / "week-229" / "optimization-service-proposal-v1-candidate.json"
EVIDENCE = (
    "data/splits/manifest.v1.json",
    "reports/week-229/final-benchmark.v1.json",
    "reports/week-229/robustness.v1.json",
    "contracts/openapi/openapi.v1alpha1.json",
    "contracts/schemas/problem-instance.v1alpha1.schema.json",
    "docs/service/SERVICE_CHARTER.md",
    "docs/economics/COMMERCIAL_MODEL.md",
    "docs/pilot/PILOT_AND_SOW.md",
    "docs/decisions/EXECUTIVE_REVIEW.md",
)
SOURCE_ROOTS = ("src", "scripts", "tests", "apps/web/app", "apps/web/tests", "contracts")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_hashes() -> dict[str, str]:
    files: list[Path] = []
    for directory in SOURCE_ROOTS:
        base = ROOT / directory
        if base.exists():
            files.extend(path for path in base.rglob("*") if path.is_file())
    for name in ("pyproject.toml", "compose.yaml", "Dockerfile.api", "README.md", ".gitignore"):
        path = ROOT / name
        if path.is_file():
            files.append(path)
    return {path.relative_to(ROOT).as_posix(): digest(path) for path in sorted(set(files))}


def build() -> dict[str, Any]:
    missing = [name for name in EVIDENCE if not (ROOT / name).is_file()]
    if missing:
        raise ValueError(f"required evidence is missing: {missing}")
    benchmark = json.loads((ROOT / "reports/week-229/final-benchmark.v1.json").read_text(encoding="utf-8"))
    if benchmark["corpus"]["total"] != 90 or benchmark["corpus"]["splits"]["test"] != 24:
        raise ValueError("frozen benchmark does not contain the required 90/24 corpus")
    if benchmark["false_feasible_count"] or benchmark["exact_disagreement_count"]:
        raise ValueError("classical feasibility or small-oracle gate failed")
    return {
        "schema_version": "optimization-service-proposal.v1",
        "bundle_id": "optimization-service-proposal-v1",
        "status": "technical_candidate_unapproved",
        "approval": None,
        "decision": None,
        "classical_first": True,
        "qaoa_advantage_claim": False,
        "cloud_jobs_executed": False,
        "synthetic_data_only": True,
        "benchmark": {
            "instances": benchmark["corpus"]["total"],
            "locked_test": benchmark["corpus"]["splits"]["test"],
            "runs": benchmark["run_count"],
            "all_reported_solutions_feasible": benchmark["all_reported_solutions_feasible"],
            "small_exact_disagreements": benchmark["exact_disagreement_count"],
        },
        "evidence_sha256": {name: digest(ROOT / name) for name in EVIDENCE},
        "source_sha256": source_hashes(),
        "limitations": [
            "no client data or realized KPI",
            "no independent buyer or finance review",
            "no eight-week customer pilot",
            "no production authentication or authorization",
            "no paid cloud or quantum hardware execution",
            "no executive proceed, pivot, or stop decision",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    candidate = build()
    if args.verify:
        if not OUTPUT.is_file() or json.loads(OUTPUT.read_text(encoding="utf-8")) != candidate:
            raise SystemExit("candidate bundle is missing or stale; rebuild after source changes")
        print(json.dumps({"status": "verified_candidate", "sources": len(candidate["source_sha256"])}))
        return
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": candidate["status"], "file": OUTPUT.relative_to(ROOT).as_posix()}))


if __name__ == "__main__":
    main()
