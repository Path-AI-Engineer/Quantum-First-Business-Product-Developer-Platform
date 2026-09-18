from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def test_materialized_instance_contract_validates_all_ninety_records() -> None:
    schema = json.loads(
        (ROOT / "contracts/schemas/problem-instance.v1alpha1.schema.json").read_text(encoding="utf-8")
    )
    validator = Draft202012Validator(schema)
    total = 0
    for path in sorted((ROOT / "data").glob("*/instances.v1.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        for instance in payload["instances"]:
            validator.validate(instance)
            total += 1
    assert total == 90


def test_openapi_contract_is_31_and_exposes_required_routes() -> None:
    payload = json.loads((ROOT / "contracts/openapi/openapi.v1alpha1.json").read_text(encoding="utf-8"))
    assert payload["openapi"].startswith("3.1")
    required = {
        "/v1/opportunities",
        "/v1/opportunities/{opportunity_id}",
        "/v1/opportunities/{opportunity_id}/assess",
        "/v1/instances",
        "/v1/formulations",
        "/v1/benchmarks",
        "/v1/benchmarks/{benchmark_id}",
        "/v1/benchmarks/{benchmark_id}/runs",
        "/v1/benchmarks/{benchmark_id}/comparison",
        "/v1/value-models",
        "/v1/pilots",
        "/v1/proposals",
        "/v1/evidence/{record_id}",
    }
    assert required <= set(payload["paths"])
