"""Deterministic reports and checksummed, review-pending contractual handoff."""

from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import pandas as pd
from jsonschema import Draft202012Validator
from pydantic import TypeAdapter

from venture_evidence.economics import EconomicsInput, economics
from venture_evidence.models import Contract, Corpus, Entity, Protocol
from venture_evidence.repository import ROOT, digest, load_corpus, load_protocol, write_json
from venture_evidence.scoring import Scenario, Score, SensitivityResult, compare, sensitivity
from venture_evidence.validation import validate


class WedgeExport(Contract):
    decision: Entity
    scores: dict[Scenario, list[Score]]
    sensitivity: SensitivityResult


def lineage(root: Path) -> dict[str, str]:
    paths = sorted((root / "src/venture_evidence").glob("*.py"))
    paths += [
        root / "data/evidence/corpus.v1.json",
        root / "data/opportunities/protocol.v1.json",
        root / "scripts/build_research.py",
        root / "pyproject.toml",
    ]
    return {path.relative_to(root).as_posix(): digest(path) for path in paths}


def overview(root: Path = ROOT) -> dict[str, Any]:
    corpus, protocol = load_corpus(root), load_protocol(root)
    audit = validate(corpus, protocol)
    scenarios = {
        scenario: [s.model_dump() for s in compare(corpus, protocol, scenario)]
        for scenario in ("conservative", "base", "aggressive")
    }
    stress = sensitivity(corpus, protocol)
    winner = scenarios["base"][0]["id"]
    decision = next(e for e in corpus.entities if e.id == "decision-wedge")
    if winner != "opportunity-pqc":
        raise ValueError("Computed winner changed; update the explicit decision record before exporting")
    return {
        "corpus": corpus.model_dump(mode="json"),
        "protocol": protocol.model_dump(mode="json"),
        "audit": audit,
        "scores": scenarios,
        "sensitivity": stress,
        "decision": decision.model_dump(mode="json"),
        "economics": {
            "conservative": economics(
                EconomicsInput(
                    organizations=100,
                    annual_price=6000,
                    hours_per_customer=120,
                    hourly_cost=100,
                    tooling_per_customer=1000,
                    customer_capacity=3,
                )
            ),
            "base": economics(EconomicsInput()),
            "aggressive": economics(
                EconomicsInput(
                    organizations=500,
                    annual_price=18000,
                    hours_per_customer=40,
                    hourly_cost=40,
                    tooling_per_customer=100,
                    customer_capacity=12,
                )
            ),
        },
    }


def thesis(room: dict[str, Any]) -> str:
    rows = room["scores"]["base"]
    sources = room["corpus"]["sources"]
    lines = [
        "# Company thesis · company-vision-v1",
        "",
        "Status: CANDIDATE — human approval pending.",
        "",
        "## Vision and mission",
        "",
        "Make technology decisions inspectable before customers commit capital or operational risk. "
        "Start with assisted cryptographic inventory and migration readiness for scoped financial-services workflows.",
        "",
        "## Decision",
        "",
        "Recommend proceeding to buyer discovery for a postquantum readiness assessment. "
        "Primary archetype: financial-services CISO. Secondary: regulated technology security lead. "
        "Neither archetype is a validated customer.",
        "",
        "Offer hypothesis: within four weeks, produce an owner-reviewed inventory for two agreed services, "
        "document blind spots and deliver a prioritized migration roadmap. "
        "No certification or cryptographic changes included.",
        "",
        "Initial revenue hypothesis: fixed-price assessment, illustrative USD 6,000–18,000. "
        "Price and effort ranges are assumptions. A recurring offer requires evidence of repeated paid use.",
        "",
        "## Comparison and uncertainty",
        "",
        "Formula: sum(normalized_weight * direction-adjusted_dimension / 5) * 100. "
        "Unknown values retain [0,5]; the base midpoint is illustrative. "
        "These intervals are not statistical confidence intervals.",
        "",
        "| Candidate | Base estimate | Assumption interval |",
        "|---|---:|---:|",
    ]
    lines.extend(f"| {r['name']} | {r['estimate']:.1f} | {r['low']:.1f}–{r['high']:.1f} |" for r in rows)
    lines += [
        "",
        "Intervals overlap: selection is fragile and provisional. Budget and buyer access remain unknown. "
        "Quantum-ready optimization is deferred because classical solvers already address many jobs; a hybrid platform "
        "is deferred because native cloud/SDK tooling already exists and paid workflow demand is unproved.",
        "",
        "## Dissent and kill gates",
        "",
        "Public guidance supports preparation, not demand for this particular offer. "
        "Libraries and incumbent providers can commoditize the technical portion. "
        "Discovery cannot guarantee visibility "
        "of embedded cryptography. Pause if qualified buyers cannot be reached; pivot if no buying trigger emerges in "
        "15 interviews; reject subscription without recurring paid use; stop standalone differentiation claims if an "
        "incumbent meets the same job at lower total cost.",
        "",
        "## Product sequence and quantum maturity",
        "",
        "0–6 months: assisted service, gated by a consented paid pilot. "
        "6–18 months: repeated product, gated by measured delivery and recurring use. 18–36 months: shared platform, "
        "gated by multiple repeatable workflows. Quantum execution requires independent "
        "workload evidence and acceptable "
        "total economics; retain the best classical alternative and promise no date of quantum advantage.",
        "",
        "## Evidence boundaries and reconstruction",
        "",
        "Zero interviews, zero validated paying customers, no observed "
        "revenue or market size. The market calculator is illustrative. "
        "NIST and CISA guidance is not a universal local "
        "legal mandate. Challenge responses are analyst self-review, not independent approval. "
        "Run `venture evidence validate`, `venture opportunity score --scenario base`, "
        "`venture opportunity sensitivity`, and `venture handoff verify` to reconstruct the decision.",
        "",
        "## Source register",
        "",
    ]
    lines.extend(f"- [{s['title']}]({s['url']}) — {s['publisher']}; accessed {s['accessed_on']}." for s in sources)
    return "\n".join(lines) + "\n"


def build_reports(root: Path = ROOT) -> dict[str, Any]:
    room = overview(root)
    reports = root / "reports/week-223"
    reports.mkdir(parents=True, exist_ok=True)
    write_json(reports / "room.v1.json", room)
    write_json(reports / "freshness.v1.json", room["audit"])
    write_json(reports / "sensitivity.v1.json", room["sensitivity"])
    frame = pd.DataFrame(
        [
            {key: r[key] for key in ("id", "scenario", "low", "high", "estimate")}
            for rows in room["scores"].values()
            for r in rows
        ]
    )
    frame.to_csv(reports / "opportunity-scenarios.csv", index=False, lineterminator="\n")
    text = thesis(room)
    (reports / "company-thesis.md").write_text(text, encoding="utf-8")
    (reports / "company-thesis.html").write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8"><title>Company thesis</title>'
        "<style>body{max-width:80ch;margin:3rem auto;padding:1rem;font:16px/1.6 system-ui;color:#243d35;"
        "background:#f7f8f3}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}</style>"
        f"<body><pre>{html.escape(text)}</pre></body></html>",
        encoding="utf-8",
    )
    return room


def export_handoff(version: str = "company-vision-v1", root: Path = ROOT) -> Path:
    if not re.fullmatch(r"company-vision-v[1-9][0-9]*", version):
        raise ValueError("Version must match company-vision-vN; path traversal forbidden")
    room = build_reports(root)
    target = root / "reports/handoff" / version
    target.mkdir(parents=True, exist_ok=True)
    entities = room["corpus"]["entities"]

    def select(*kinds: str) -> list[dict[str, Any]]:
        return [e for e in entities if e["entity_type"] in kinds]

    payloads: dict[str, Any] = {
        "wedge-decision.json": {
            "decision": room["decision"],
            "scores": room["scores"],
            "sensitivity": room["sensitivity"],
        },
        "icp-jtbd.json": select("customer_profile", "job_to_be_done"),
        "product-sequence.json": select("product_stage", "moat", "capability"),
        "assumptions-register.json": select("assumption", "pricing"),
        "evidence-index.json": room["corpus"],
        "experiment-backlog.json": select("experiment", "interview_plan", "discovery_question"),
        "risk-kill-gates.json": select("risk", "challenge", "objection"),
        "glossary.json": {
            "C0": "Unverified intuition",
            "C1": "Secondary signal",
            "C2": "Independent corroboration",
            "C3": "Primary source or reproducible measurement",
            "C4": "Direct buyer validation; absent here",
            "ICP": "Ideal customer profile archetype",
            "PQC": "Postquantum cryptography",
            "wedge": "Initial bounded offer",
            "kill_gate": "Condition to stop, pause or pivot",
        },
    }
    schemas: dict[str, Any] = {}
    list_schema = TypeAdapter(list[Entity]).json_schema()
    for name, payload in payloads.items():
        schema = (
            Corpus.model_json_schema()
            if name == "evidence-index.json"
            else WedgeExport.model_json_schema()
            if name == "wedge-decision.json"
            else list_schema
            if isinstance(payload, list)
            else {
                "type": "object",
                "required": list(payload),
                "additionalProperties": False,
                "properties": {
                    key: ({"type": "string", "minLength": 1} if isinstance(value, str) else {"type": "object"})
                    for key, value in payload.items()
                },
            }
        )
        schema = {"$schema": "https://json-schema.org/draft/2020-12/schema", **schema}
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(payload)
        schemas[name] = schema
        write_json(target / name, payload)
    (target / "company-thesis.md").write_text(thesis(room), encoding="utf-8")
    write_json(target / "schemas.json", schemas)
    filenames = sorted([*payloads, "company-thesis.md", "schemas.json"])
    for name in filenames:
        content = (target / name).read_text(encoding="utf-8")
        if re.search(r"-----BEGIN .*PRIVATE KEY-----|(?:sk|ghp)_[A-Za-z0-9]{20,}", content):
            raise ValueError("Possible secret in handoff")
    write_json(
        target / "manifest.json",
        {
            "schema_version": "venture.handoff.v1",
            "version": version,
            "approval": "pending_human_review",
            "files": {name: digest(target / name) for name in filenames},
            "source_lineage": lineage(root),
            "receiver_boundary": "Artifacts only; no code, database, credentials or execution state sharing.",
        },
    )
    with ZipFile(target.with_suffix(".zip"), "w", compression=ZIP_DEFLATED) as archive:
        for name in sorted([*filenames, "manifest.json"]):
            info = ZipInfo(name, date_time=(2026, 9, 12, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info, (target / name).read_bytes())
    return target


def verify_handoff(version: str = "company-vision-v1", root: Path = ROOT) -> dict[str, object]:
    if not re.fullmatch(r"company-vision-v[1-9][0-9]*", version):
        raise ValueError("Invalid version")
    target = root / "reports/handoff" / version
    manifest = json.loads((target / "manifest.json").read_text(encoding="utf-8"))
    if (
        manifest.get("schema_version") != "venture.handoff.v1"
        or manifest.get("version") != version
        or manifest.get("approval") != "pending_human_review"
    ):
        raise ValueError("Invalid handoff state or version; human approval cannot be fabricated")
    if manifest["source_lineage"] != lineage(root):
        raise ValueError("Handoff source lineage changed: rebuild the candidate with the reviewed source")
    required = {
        "company-thesis.md",
        "wedge-decision.json",
        "icp-jtbd.json",
        "product-sequence.json",
        "assumptions-register.json",
        "evidence-index.json",
        "experiment-backlog.json",
        "risk-kill-gates.json",
        "glossary.json",
        "schemas.json",
    }
    if set(manifest["files"]) != required:
        raise ValueError("Unexpected handoff members")
    for name, expected in manifest["files"].items():
        if digest(target / name) != expected:
            raise ValueError(f"Checksum mismatch: {name}")
    schemas = json.loads((target / "schemas.json").read_text(encoding="utf-8"))
    if set(schemas) != required - {"company-thesis.md", "schemas.json"}:
        raise ValueError("Missing payload schemas")
    for name, schema in schemas.items():
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(json.loads((target / name).read_text(encoding="utf-8")))
    if set(path.name for path in target.iterdir()) != required | {"manifest.json"}:
        raise ValueError("Unexpected files in handoff directory")
    with ZipFile(target.with_suffix(".zip")) as archive:
        if sorted(archive.namelist()) != sorted([*required, "manifest.json"]):
            raise ValueError("Unexpected archive members")
        for name in archive.namelist():
            if archive.read(name) != (target / name).read_bytes():
                raise ValueError(f"Archive content mismatch: {name}")
    validate(load_corpus(root), load_protocol(root))
    return {
        "status": "verified",
        "files": len(required),
        "approval": manifest["approval"],
        "zip_sha256": digest(target.with_suffix(".zip")),
        "manifest_sha256": hashlib.sha256((target / "manifest.json").read_bytes()).hexdigest(),
    }


def export_schemas(root: Path = ROOT) -> None:
    for name, model in (("corpus", Corpus), ("protocol", Protocol), ("entity", Entity)):
        schema = {"$schema": "https://json-schema.org/draft/2020-12/schema", **model.model_json_schema()}
        Draft202012Validator.check_schema(schema)
        write_json(root / f"contracts/schemas/{name}.v1.schema.json", schema)
