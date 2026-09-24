from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports" / "week-237"
OUTPUT = REPORTS / "enterprise-suite-contracts-v1-candidate.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    inputs = [
        ROOT / "contracts" / "openapi" / "openapi.v1alpha1.json",
        ROOT / "contracts" / "asyncapi" / "asyncapi.v1alpha1.json",
        ROOT / "contracts" / "jsonschema" / "shared-kernel.v1.schema.json",
        REPORTS / "evaluation.v1.json",
        ROOT / "docs" / "product" / "PRODUCT_AND_PACKAGING.md",
        ROOT / "docs" / "security" / "THREAT_MODEL.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in inputs if not path.exists()]
    if missing:
        raise FileNotFoundError(f"bundle inputs missing: {missing}")
    evaluation = json.loads((REPORTS / "evaluation.v1.json").read_text())
    if evaluation["status"] != "verified" or evaluation["total_cases"] != 687:
        raise ValueError("evaluation is not frozen and verified")
    files: list[dict[str, Any]] = [{"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": digest(path)} for path in inputs]
    bundle = {
        "schema_version": "enterprise-suite-contracts-v1",
        "status": "technical_candidate_unapproved",
        "approval": None,
        "executive_portfolio_decision": None,
        "module_decisions": {
            "crypto-readiness": "pending-executive-review",
            "optimization-studio": "pending-executive-review",
            "quantum-workbench": "pending-executive-review",
            "shared-governance": "pending-executive-review",
        },
        "source_project": "59-enterprise-ai-quantum-product-suite",
        "runtime_dependencies_on_projects_56_57_58": [],
        "evaluation_cases": 687,
        "files": files,
        "limitations": [
            "Synthetic data only",
            "No production, compliance, customer, ROI, or quantum advantage claim",
            "External contract approval and executive invest/hold/kill decisions remain pending",
        ],
    }
    encoded = json.dumps(bundle, indent=2, sort_keys=True).encode()
    OUTPUT.write_bytes(encoded + b"\n")
    print(json.dumps({"file": str(OUTPUT.relative_to(ROOT)), "sha256": hashlib.sha256(encoded).hexdigest(), "status": bundle["status"]}))


if __name__ == "__main__":
    main()
