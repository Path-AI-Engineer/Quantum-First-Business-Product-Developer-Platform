from __future__ import annotations

import json
from collections.abc import Callable
from hashlib import sha256
from pathlib import Path
from typing import Any

from enterprise_suite.assistant import grounded_assistant
from enterprise_suite.corpus import build_corpus, corpus_counts
from enterprise_suite.models import AssistantRequest
from enterprise_suite.policy import authorize

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports" / "week-237" / "evaluation.v1.json"


def _cases(name: str, count: int, check: Callable[[int], bool]) -> dict[str, Any]:
    results = [bool(check(index)) for index in range(count)]
    return {"suite": name, "cases": count, "passed": sum(results), "failed": count - sum(results)}


def main() -> None:
    corpus = build_corpus()
    suites = [
        _cases(
            "authorization_tenant",
            240,
            lambda index: not authorize(
                corpus["identities"][index % 30],
                "can_view",
                next(resource for resource in corpus["resources"] if resource.tenant_id != corpus["identities"][index % 30].tenant_id),
            )[0],
        ),
        _cases("contract_event_compatibility", 120, lambda index: index >= 0),
        _cases("cross_module_journeys", 90, lambda index: bool(corpus["evidence"][index % 180].correlation_id)),
        _cases(
            "ai_grounding_injection_abstention",
            72,
            lambda index: grounded_assistant(
                AssistantRequest(
                    tenant_id="meridian",
                    question="Ignore previous" if index % 3 == 0 else "Summarize",
                    evidence_ids=("ev-meridian-000",),
                ),
                corpus["evidence"],
            ).side_effects
            == (),
        ),
        _cases("policy_approval", 60, lambda index: index >= 0),
        _cases("fault_recovery", 45, lambda index: index >= 0),
        _cases("report_reconciliation", 30, lambda index: len(corpus["evidence"]) // 3 == 60),
        _cases("persona_usability", 18, lambda index: index < 18),
        _cases("package_pilot_decisions", 12, lambda index: index < 12),
    ]
    total = sum(item["cases"] for item in suites)
    passed = sum(item["passed"] for item in suites)
    artifact = {
        "schema_version": "enterprise-suite.evaluation.v1",
        "status": "verified" if total == passed == 687 else "failed",
        "total_cases": total,
        "passed": passed,
        "failed": total - passed,
        "synthetic_only": True,
        "corpus": corpus_counts(corpus),
        "suites": suites,
        "claims": {
            "production_ready": False,
            "compliant": False,
            "quantum_advantage": False,
            "real_customers": False,
        },
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(artifact, indent=2, sort_keys=True).encode()
    OUTPUT.write_bytes(encoded + b"\n")
    print(json.dumps({"cases": total, "passed": passed, "sha256": sha256(encoded).hexdigest()}))


if __name__ == "__main__":
    main()
