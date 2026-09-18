from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
BUNDLE = ROOT / "reports/week-233/developer-platform-design-v1-candidate.json"
INCLUDED = ("src", "sdks", "cli", "contracts", "docs", "apps/portal/app", "tests", "scripts")


def source_hashes() -> dict[str, str]:
    values: dict[str, str] = {}
    for location in INCLUDED:
        path = ROOT / location
        for file in sorted(path.rglob("*")):
            if file.is_file() and not any(
                part in {"node_modules", ".next", "__pycache__"} for part in file.parts
            ):
                relative = file.relative_to(ROOT).as_posix()
                if relative.endswith("build_final_bundle.py"):
                    continue
                values[relative] = hashlib.sha256(file.read_bytes()).hexdigest()
    return values


def build() -> dict[str, object]:
    evaluation_path = ROOT / "reports/week-233/evaluation.v1.json"
    evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
    return {
        "schema_version": "qdp.release-candidate.v1",
        "release": "developer-platform-design-v1",
        "status": "technical_candidate_unapproved",
        "approval": None,
        "decision": None,
        "source_lineage": source_hashes(),
        "evidence": evaluation,
        "boundaries": {
            "live_cloud_jobs": 0,
            "arbitrary_code_execution": False,
            "commercial_billing": False,
            "enterprise_sla": False,
            "human_usability_study": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    current = build()
    if args.verify:
        stored = json.loads(BUNDLE.read_text(encoding="utf-8"))
        if stored != current:
            raise ValueError("frozen source snapshot is stale")
        print(json.dumps({"source_files": len(current["source_lineage"]), "status": "verified"}))
        return
    BUNDLE.parent.mkdir(parents=True, exist_ok=True)
    BUNDLE.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "file": str(BUNDLE.relative_to(ROOT)),
                "source_files": len(current["source_lineage"]),
                "status": current["status"],
            }
        )
    )


if __name__ == "__main__":
    main()
