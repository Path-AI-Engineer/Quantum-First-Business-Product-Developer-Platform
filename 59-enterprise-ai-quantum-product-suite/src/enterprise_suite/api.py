from __future__ import annotations

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

from enterprise_suite.models import (
    AssistantRequest,
    BenchmarkRequest,
    DecisionRequest,
    JobRequest,
    ReportRequest,
)
from enterprise_suite.service import EnterpriseSuite

app = FastAPI(
    title="Enterprise Quantum Intelligence Suite",
    version="1.0.0-alpha.1",
    description="Synthetic, local-only technical reference. No production or compliance claim.",
)
suite = EnterpriseSuite()


class ApprovalRequest(BaseModel):
    tenant_id: str
    requester_id: str
    resource_id: str
    resource_revision: int = 1
    scope: str


@app.get("/health")
def health() -> dict[str, object]:
    return suite.health()


@app.get("/v1/portfolio/summary")
def portfolio(x_tenant_id: str = Header()) -> dict[str, object]:
    return suite.portfolio(x_tenant_id)


@app.get("/v1/catalog")
def catalog() -> list[dict[str, object]]:
    return suite.catalog()


@app.get("/v1/evidence/{evidence_id}")
def evidence(evidence_id: str, x_tenant_id: str = Header()) -> dict[str, object]:
    result = suite.evidence(evidence_id, x_tenant_id)
    if result is None:
        raise HTTPException(404, "evidence not found")
    return result


@app.get("/v1/risks")
def risks(x_tenant_id: str = Header()) -> list[dict[str, object]]:
    return suite.risks(x_tenant_id)


@app.post("/v1/recommendations/{recommendation_id}/decisions")
def decision(recommendation_id: str, request: DecisionRequest) -> dict[str, object]:
    try:
        return suite.decide(recommendation_id, request)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc


@app.post("/v1/approvals")
def approval(request: ApprovalRequest) -> dict[str, object]:
    return suite.request_approval(
        request.tenant_id,
        request.requester_id,
        request.resource_id,
        request.resource_revision,
        request.scope,
    ).model_dump(mode="json")


@app.get("/v1/approvals")
def approvals(x_tenant_id: str = Header()) -> list[dict[str, object]]:
    return [approval.model_dump(mode="json") for approval in suite.approvals.values() if approval.tenant_id == x_tenant_id]


@app.get("/v1/crypto/findings")
def findings(x_tenant_id: str = Header()) -> list[dict[str, object]]:
    return suite.risks(x_tenant_id)


@app.get("/v1/crypto/migration-waves")
def migration_waves(x_tenant_id: str = Header()) -> list[dict[str, object]]:
    return [{"tenant_id": x_tenant_id, "wave": 1, "status": "proposed-not-authorized"}]


@app.get("/v1/optimization/opportunities")
def opportunities(x_tenant_id: str = Header()) -> list[dict[str, object]]:
    return suite._tenant_items("opportunities", x_tenant_id)


@app.post("/v1/optimization/benchmarks")
def benchmark(request: BenchmarkRequest) -> dict[str, object]:
    try:
        return suite.benchmark(request)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc


@app.get("/v1/quantum/capabilities")
def capabilities() -> list[dict[str, object]]:
    return [{"id": "local-simulator", "provider": "local", "external": False}]


@app.post("/v1/quantum/jobs")
def job(request: JobRequest) -> dict[str, object]:
    try:
        return suite.submit_job(request)
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc


@app.get("/v1/usage")
def usage(x_tenant_id: str = Header()) -> dict[str, object]:
    return suite.usage(x_tenant_id)


@app.get("/v1/audit")
def audit(x_tenant_id: str = Header()) -> list[dict[str, object]]:
    return [item.model_dump(mode="json") for item in suite.audit if item.tenant_id == x_tenant_id]


@app.post("/v1/reports")
def reports(request: ReportRequest) -> dict[str, object]:
    return suite.report(request)


@app.post("/v1/assistant/brief")
def assistant(request: AssistantRequest) -> dict[str, object]:
    return suite.assist(request).model_dump()
