from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from optimization_lab.api import app
from optimization_lab.benchmark import robustness_report, run_benchmark
from optimization_lab.corpus import build_corpus, corpus_summary
from optimization_lab.models import Domain, ProblemInstance, Split

ROOT = Path(__file__).resolve().parents[1]


def write_json(path: Path, payload: Any) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    path.write_text(content, encoding="utf-8")
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def main() -> None:
    corpus = build_corpus()
    artifacts: dict[str, str] = {}
    for domain in Domain:
        selected = [item.model_dump(mode="json") for item in corpus if item.domain is domain]
        artifacts[f"data/{domain.value}/instances.v1.json"] = write_json(
            ROOT / "data" / domain.value / "instances.v1.json",
            {"schema_version": "optimization.instances.v1", "domain": domain.value, "instances": selected},
        )
    artifacts["data/splits/manifest.v1.json"] = write_json(
        ROOT / "data" / "splits" / "manifest.v1.json",
        {
            **corpus_summary(corpus),
            "development_ids": [item.instance_id for item in corpus if item.split is Split.DEVELOPMENT],
            "test_ids": [item.instance_id for item in corpus if item.split is Split.TEST],
        },
    )
    artifacts["contracts/schemas/problem-instance.v1alpha1.schema.json"] = write_json(
        ROOT / "contracts" / "schemas" / "problem-instance.v1alpha1.schema.json",
        ProblemInstance.model_json_schema(),
    )
    artifacts["contracts/openapi/openapi.v1alpha1.json"] = write_json(
        ROOT / "contracts" / "openapi" / "openapi.v1alpha1.json", app.openapi()
    )
    benchmark = run_benchmark(include_locked_test=True)
    artifacts["reports/week-229/final-benchmark.v1.json"] = write_json(
        ROOT / "reports" / "week-229" / "final-benchmark.v1.json", benchmark
    )
    artifacts["reports/week-229/robustness.v1.json"] = write_json(
        ROOT / "reports" / "week-229" / "robustness.v1.json", robustness_report()
    )
    print(json.dumps({"artifacts": len(artifacts), "runs": benchmark["run_count"], "sha256": artifacts}))


if __name__ == "__main__":
    main()
