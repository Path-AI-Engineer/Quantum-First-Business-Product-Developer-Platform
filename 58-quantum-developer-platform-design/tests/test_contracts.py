import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).parents[1]


def test_versioned_contracts_parse_and_examples_validate() -> None:
    openapi = json.loads((ROOT / "contracts/openapi/openapi.v1alpha1.json").read_text())
    asyncapi = json.loads((ROOT / "contracts/asyncapi/asyncapi.v1alpha1.json").read_text())
    schema = json.loads((ROOT / "contracts/jsonschema/job-request.v1.schema.json").read_text())
    example = json.loads((ROOT / "contracts/examples/job-request.valid.json").read_text())
    assert openapi["openapi"] == "3.1.1"
    assert asyncapi["asyncapi"].startswith("3.")
    assert len(openapi["paths"]) >= 20
    jsonschema.validate(example, schema)


def test_standards_profile_is_frozen() -> None:
    profile = json.loads((ROOT / "contracts/standards-profile.v1.json").read_text())
    assert profile["freeze_state"] == "sealed"
    assert profile["cloud_live_smoke_required"] is False
    assert profile["profiles"]["json_schema"] == "2020-12"
