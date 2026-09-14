"""Local fixture-driven assessment API. Never expose this demo on a public network."""

import hashlib
import json
import os
from dataclasses import asdict
from pathlib import Path
from threading import Lock
from typing import Annotated, Any, cast

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from pqc_product.corpus import Corpus, build_corpus
from pqc_product.domain import Asset, Evidence, Finding, MigrationAction
from pqc_product.engine import evaluate, migration_actions
from pqc_product.ingestion import ImportRejected, parse_import
from pqc_product.object_store import ObjectStore
from pqc_product.reporting import REPORT_TYPES, build_report
from pqc_product.security import IDENTITIES, Identity, allowed
from pqc_product.storage import DatabaseStore, decision_table, report_table, wave_table


class ImportBody(BaseModel):
    source_type: str
    payload: dict[str, Any] | list[Any] | str


class DecisionBody(BaseModel):
    decision: str = Field(pattern="^(confirm|dismiss|needs_evidence)$")
    rationale: str = Field(min_length=8, max_length=500)


class WaveBody(BaseModel):
    name: str = Field(min_length=3, max_length=80)
    action_ids: list[str] = Field(min_length=1, max_length=50)
    owner_id: str = Field(min_length=3, max_length=80)
    acceptance_evidence: str = Field(min_length=8, max_length=300)


class ReportBody(BaseModel):
    type: str


class State:
    def __init__(self, corpus: Corpus, db: DatabaseStore | None = None) -> None:
        self.corpus = corpus
        self.db = db
        self._audit_lock = Lock()
        self.imported: list[Evidence] = db.load_evidence() if db else []
        self.decisions: dict[str, dict[str, Any]] = db.load_documents(decision_table) if db else {}
        self.waves: dict[str, dict[str, Any]] = db.load_documents(wave_table) if db else {}
        self.reports: dict[str, dict[str, Any]] = db.load_documents(report_table) if db else {}
        self.audit: list[dict[str, Any]] = db.load_audit() if db else []

    def assets(self, identity: Identity) -> tuple[Asset, ...]:
        return tuple(a for a in self.corpus.assets if allowed(identity, a.tenant_id, "read", a.id))

    def evidence(self, identity: Identity) -> tuple[Evidence, ...]:
        visible = {a.id for a in self.assets(identity)}
        return tuple(e for e in (*self.corpus.evidence, *self.imported) if e.asset_id in visible)

    def findings(self, identity: Identity) -> tuple[Finding, ...]:
        return evaluate(self.assets(identity), self.evidence(identity))

    def actions(self, identity: Identity) -> tuple[MigrationAction, ...]:
        return migration_actions(self.findings(identity))

    def log(self, identity: Identity, operation: str, object_id: str) -> None:
        with self._audit_lock:
            previous = self.audit[-1]["hash"] if self.audit else "GENESIS"
            event = {
                "sequence": len(self.audit) + 1,
                "tenant_id": identity.tenant_id,
                "actor": identity.id,
                "operation": operation,
                "object_id": object_id,
                "previous_hash": previous,
            }
            event["hash"] = hashlib.sha256(json.dumps(event, sort_keys=True).encode()).hexdigest()
            if self.db:
                self.db.save_audit(event)
            self.audit.append(event)


def _identity(x_demo_identity: str | None = Header(default=None)) -> Identity:
    if x_demo_identity not in IDENTITIES:
        raise HTTPException(403, "Synthetic identity required; default deny")
    return IDENTITIES[x_demo_identity]


IdentityDep = Annotated[Identity, Depends(_identity)]


def _one(items: tuple[Any, ...], item_id: str) -> Any:
    for item in items:
        if item.id == item_id:
            return item
    raise HTTPException(404, "Not found")


def create_app(
    corpus: Corpus | None = None, db: DatabaseStore | None = None, objects: ObjectStore | None = None
) -> FastAPI:
    if db is None and os.getenv("PQC_DATABASE_URL"):
        db = DatabaseStore(os.environ["PQC_DATABASE_URL"])
    state = State(corpus or build_corpus(), db)
    if objects is None and os.getenv("PQC_OBJECT_ROOT"):
        objects = ObjectStore(Path(os.environ["PQC_OBJECT_ROOT"]))
    app = FastAPI(title="Cryptographic Migration Command Center — synthetic local prototype", version="0.1.0")
    app.state.lab = state

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "mode": "synthetic-offline"}

    @app.post("/v1/assessments")
    def create_assessment(identity: IdentityDep) -> dict[str, object]:
        if not allowed(identity, identity.tenant_id, "read"):
            raise HTTPException(403, "Denied")
        assessment_id = f"assessment-{identity.tenant_id}-synthetic-v1"
        state.log(identity, "assessment.created", assessment_id)
        return {"id": assessment_id, "tenant_id": identity.tenant_id, "synthetic": True}

    @app.post("/v1/assessments/{assessment_id}/imports")
    def import_evidence(assessment_id: str, body: ImportBody, identity: IdentityDep) -> dict[str, object]:
        if assessment_id != f"assessment-{identity.tenant_id}-synthetic-v1":
            raise HTTPException(404, "Not found")
        if not allowed(identity, identity.tenant_id, "import"):
            raise HTTPException(403, "Denied")
        payload = body.payload.encode() if isinstance(body.payload, str) else json.dumps(body.payload).encode()
        try:
            accepted = parse_import(
                identity.tenant_id, body.source_type, payload, frozenset(a.id for a in state.assets(identity))
            )
        except ImportRejected as exc:
            raise HTTPException(422, str(exc)) from exc
        if state.db:
            new = state.db.save_evidence(accepted)
        else:
            existing = {item.id for item in state.imported}
            new = tuple(item for item in accepted if item.id not in existing)
        state.imported.extend(new)
        state.log(identity, "evidence.imported", assessment_id)
        return {"accepted": len(new), "duplicates": len(accepted) - len(new), "tenant_id": identity.tenant_id}

    @app.get("/v1/assets")
    def list_assets(identity: IdentityDep) -> list[dict[str, Any]]:
        state.log(identity, "asset.list", identity.tenant_id)
        return [asdict(a) for a in state.assets(identity)]

    @app.get("/v1/assets/{asset_id}")
    def get_asset(asset_id: str, identity: IdentityDep) -> dict[str, Any]:
        asset = _one(state.assets(identity), asset_id)
        state.log(identity, "asset.read", asset_id)
        return asdict(asset)

    @app.get("/v1/dependencies")
    def list_dependencies(identity: IdentityDep) -> list[dict[str, str]]:
        visible = {asset.id for asset in state.assets(identity)}
        state.log(identity, "dependency.list", identity.tenant_id)
        return [
            {"from": source, "to": target}
            for source, target in state.corpus.dependencies
            if source in visible and target in visible
        ]

    @app.get("/v1/observations")
    def list_observations(identity: IdentityDep) -> list[dict[str, Any]]:
        state.log(identity, "evidence.list", identity.tenant_id)
        return [asdict(e) for e in state.evidence(identity)]

    @app.get("/v1/findings")
    def list_findings(identity: IdentityDep) -> list[dict[str, Any]]:
        state.log(identity, "finding.list", identity.tenant_id)
        return [asdict(f) for f in state.findings(identity)]

    @app.get("/v1/findings/{finding_id}")
    def get_finding(finding_id: str, identity: IdentityDep) -> dict[str, Any]:
        finding = _one(state.findings(identity), finding_id)
        state.log(identity, "finding.read", finding_id)
        return asdict(finding)

    @app.post("/v1/findings/{finding_id}/decisions")
    def decide(finding_id: str, body: DecisionBody, identity: IdentityDep) -> dict[str, Any]:
        finding = _one(state.findings(identity), finding_id)
        if not allowed(identity, finding.tenant_id, "decide", finding.asset_id):
            raise HTTPException(403, "Denied")
        decision = {
            "finding_id": finding_id,
            "tenant_id": identity.tenant_id,
            "actor": identity.id,
            "decision": body.decision,
            "rationale": body.rationale,
            "changes_asset": False,
        }
        if state.db:
            state.db.save_document(decision_table, finding_id, identity.tenant_id, decision)
        state.decisions[finding_id] = decision
        state.log(identity, "finding.decided", finding_id)
        return decision

    @app.get("/v1/migration-actions")
    def list_actions(identity: IdentityDep) -> list[dict[str, Any]]:
        state.log(identity, "action.list", identity.tenant_id)
        return [asdict(a) for a in state.actions(identity)]

    @app.post("/v1/migration-waves")
    def create_wave(body: WaveBody, identity: IdentityDep) -> dict[str, Any]:
        if not allowed(identity, identity.tenant_id, "wave"):
            raise HTTPException(403, "Denied")
        known = {a.id for a in state.actions(identity)}
        if not set(body.action_ids) <= known:
            raise HTTPException(422, "Unknown or cross-tenant action")
        if body.owner_id not in state.corpus.owner_ids or not body.owner_id.startswith(f"{identity.tenant_id}-"):
            raise HTTPException(422, "Unknown or cross-tenant owner")
        wave_id = f"wave-{identity.tenant_id}-{len(state.waves) + 1}"
        wave = {
            "id": wave_id,
            "tenant_id": identity.tenant_id,
            "name": body.name,
            "action_ids": body.action_ids,
            "owner_id": body.owner_id,
            "acceptance_evidence": body.acceptance_evidence,
            "status": "proposed",
            "executes_migration": False,
        }
        if state.db:
            state.db.save_document(wave_table, wave_id, identity.tenant_id, wave)
        state.waves[wave_id] = wave
        state.log(identity, "wave.proposed", wave_id)
        return wave

    @app.get("/v1/standards")
    def standards(identity: IdentityDep) -> dict[str, Any]:
        state.log(identity, "standards.read", identity.tenant_id)
        file = Path(__file__).resolve().parents[2] / "contracts" / "standards-profile.v1.json"
        return cast(dict[str, Any], json.loads(file.read_text(encoding="utf-8")))

    @app.post("/v1/reports")
    def create_report(body: ReportBody, identity: IdentityDep) -> dict[str, Any]:
        if body.type not in REPORT_TYPES:
            raise HTTPException(422, "Unsupported report type")
        visible_ids = {asset.id for asset in state.assets(identity)}
        baseline = tuple(item for item in state.corpus.evidence if item.asset_id in visible_ids)
        report = build_report(
            identity.tenant_id,
            body.type,
            state.assets(identity),
            state.evidence(identity),
            state.findings(identity),
            state.actions(identity),
            baseline_evidence=baseline if body.type == "delta" else None,
        )
        report_id = f"report-{identity.tenant_id}-{body.type}-{report['sha256'][:12]}"
        if objects:
            report["object_sha256"] = objects.put_report(report)
        if state.db:
            state.db.save_document(report_table, report_id, identity.tenant_id, report)
        state.reports[report_id] = report
        state.log(identity, "report.created", report_id)
        return {"id": report_id, **report}

    @app.get("/v1/reports/{report_id}")
    def get_report(report_id: str, identity: IdentityDep) -> dict[str, Any]:
        if not report_id.startswith(f"report-{identity.tenant_id}-") or report_id not in state.reports:
            raise HTTPException(404, "Not found")
        state.log(identity, "report.read", report_id)
        return {"id": report_id, **state.reports[report_id]}

    @app.get("/v1/audit")
    def audit(identity: IdentityDep) -> list[dict[str, Any]]:
        if identity.role not in {"owner", "architect", "reviewer"}:
            raise HTTPException(403, "Denied")
        return [event for event in state.audit if event["tenant_id"] == identity.tenant_id]

    return app


app = create_app()
