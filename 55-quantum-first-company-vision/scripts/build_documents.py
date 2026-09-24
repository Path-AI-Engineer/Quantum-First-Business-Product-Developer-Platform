"""Materialize readable views from the canonical corpus, never invented study execution."""

import json

from venture_evidence.models import Claim
from venture_evidence.repository import ROOT, load_corpus, load_protocol, write_json
from venture_evidence.validation import validate

VIEWS = {
    "docs/discovery/problem-portfolio.md": ("pain", "workflow", "inaction", "buying_pattern"),
    "docs/discovery/icp-jtbd-atlas.md": ("customer_profile", "job_to_be_done"),
    "docs/discovery/alternatives.md": ("competitor", "alternative"),
    "docs/discovery/future-interviews.md": ("interview_plan", "discovery_question"),
    "docs/thesis/pricing-assumptions.md": ("pricing", "assumption"),
    "docs/product/capability-sequence-moat.md": ("capability", "product_stage", "moat"),
    "docs/decisions/wedge-and-challenge.md": ("decision", "challenge", "objection", "trace"),
    "experiments/validation-backlog.md": ("experiment", "risk"),
}


def main() -> None:
    corpus = load_corpus()
    validate(corpus, load_protocol())
    claims = {c.id: c for c in corpus.claims}
    sources = {s.id: s for s in corpus.sources}
    for filename, kinds in VIEWS.items():
        lines = [
            "# " + filename.rsplit("/", 1)[-1].replace(".md", "").replace("-", " ").title(),
            "",
            "Generated from data/evidence/corpus.v1.json. Human approval pending. "
            "Planned work is not completed validation. Regenerate with scripts/build_documents.py.",
            "",
        ]
        for entity in corpus.entities:
            if entity.entity_type not in kinds:
                continue
            lines += [f"## {entity.title}", "", f"ID: {entity.id} | State: {entity.status}", "", entity.description, ""]
            for key, value in entity.details.items():
                lines += [f"- {key.replace('_', ' ')}: {json.dumps(value, ensure_ascii=False)}"]
            lines.append("")
            for cid in entity.claim_ids:
                claim = claims[cid]
                urls = "; ".join(f"[{sources[sid].publisher}]({sources[sid].url})" for sid in claim.source_ids)
                lines += [f"- {cid} ({claim.confidence}, {claim.kind}): {claim.text} {urls}"]
            if entity.related_ids:
                lines += ["", "Related: " + ", ".join(entity.related_ids)]
            lines.append("")
        path = ROOT / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    views = {
        "data/sources/index.v1.json": [s.model_dump(mode="json") for s in corpus.sources],
        "data/assumptions/index.v1.json": [
            e.model_dump(mode="json") for e in corpus.entities if e.entity_type in ("assumption", "pricing")
        ],
        "data/customers/index.v1.json": [
            e.model_dump(mode="json")
            for e in corpus.entities
            if e.entity_type in ("customer_profile", "job_to_be_done")
        ],
        "data/competitors/index.v1.json": [
            e.model_dump(mode="json") for e in corpus.entities if e.entity_type in ("competitor", "alternative")
        ],
    }
    for filename, payload in views.items():
        write_json(ROOT / filename, payload)
    sample = corpus.claims[0].model_dump(mode="json")
    write_json(ROOT / "contracts/examples/claim.valid.json", sample)
    sample["source_ids"] = []
    write_json(ROOT / "contracts/examples/claim.invalid-missing-source.json", sample)
    write_json(
        ROOT / "contracts/schemas/claim.v1.schema.json",
        {"$schema": "https://json-schema.org/draft/2020-12/schema", **Claim.model_json_schema()},
    )
    print(json.dumps({"documents": len(VIEWS), "derived_data_views": len(views), "approval": corpus.approval}))


if __name__ == "__main__":
    main()
