import json
from dataclasses import asdict
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from pqc_product.corpus import build_corpus


def test_canonical_observation_schema_and_all_fixture_records() -> None:
    schema = json.loads(
        (Path(__file__).resolve().parents[1] / "contracts" / "canonical.v1alpha1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    corpus = build_corpus()
    for item in corpus.evidence:
        validator.validate(asdict(item))
