"""FastAPI surface for the executable reference design."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import Depends, FastAPI, Header, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from quantum_platform.control_plane import ControlPlane
from quantum_platform.models import Environment, JobRequest, ProblemDetails
from quantum_platform.security import new_api_secret

app = FastAPI(
    title="Quantum Developer Platform Reference Lab",
    version="1.0.0-alpha.1",
    openapi_version="3.1.0",
    description="Local sandbox reference design. No commercial SLA or live cloud submission.",
)
plane = ControlPlane()


class OrganizationCreate(BaseModel):
    name: str


class ProjectCreate(BaseModel):
    organization_id: str
    name: str
    environment: Environment = Environment.SANDBOX


class ApiKeyCreate(BaseModel):
    project_id: str
    scopes: tuple[str, ...] = ("jobs:write", "jobs:read")


class WebhookCreate(BaseModel):
    project_id: str
    url: str


def _problem(status: int, code: str, detail: str, request_id: str) -> HTTPException:
    body = ProblemDetails(
        title="Quantum platform request failed",
        status=status,
        code=code,
        detail=detail,
        correlation_id=request_id,
        remediation_hint="Check the API reference and retry only when the operation is documented as safe.",
    )
    return HTTPException(status_code=status, detail=body.model_dump(mode="json"))


def request_id(x_request_id: Annotated[str | None, Header()] = None) -> str:
    return x_request_id or "req_local_reference"


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Any, exc: HTTPException) -> JSONResponse:
    content = exc.detail if isinstance(exc.detail, dict) else {"detail": exc.detail}
    return JSONResponse(status_code=exc.status_code, content=content)


@app.middleware("http")
async def security_headers(request: Any, call_next: Any) -> Response:
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/health")
@app.get("/v1/health/live")
def live() -> dict[str, str]:
    return {"status": "ok", "service": "quantum-developer-platform-reference-lab"}


@app.get("/v1/health/ready")
def ready() -> dict[str, object]:
    return {"status": "ready", "providers": ["fake", "local"], "cloud_live": False}


@app.post("/v1/organizations", status_code=201)
def create_organization(payload: OrganizationCreate) -> dict[str, object]:
    return plane.create_organization(payload.name).model_dump(mode="json")


@app.post("/v1/projects", status_code=201)
def create_project(payload: ProjectCreate, req: Annotated[str, Depends(request_id)]) -> dict[str, object]:
    try:
        result = plane.create_project(payload.organization_id, payload.name, payload.environment)
    except KeyError as exc:
        raise _problem(404, "ORGANIZATION_NOT_FOUND", str(exc), req) from exc
    return result.model_dump(mode="json")


@app.post("/v1/api-keys", status_code=201)
def create_api_key(payload: ApiKeyCreate, req: Annotated[str, Depends(request_id)]) -> dict[str, object]:
    try:
        return plane.create_api_key(payload.project_id, payload.scopes).model_dump(mode="json")
    except KeyError as exc:
        raise _problem(404, "PROJECT_NOT_FOUND", str(exc), req) from exc


@app.post("/v1/api-keys/{key_id}/rotate", status_code=201)
def rotate_api_key(
    key_id: str, project_id: str, req: Annotated[str, Depends(request_id)]
) -> dict[str, object]:
    try:
        return plane.rotate_api_key(project_id, key_id).model_dump(mode="json")
    except (KeyError, PermissionError) as exc:
        raise _problem(404, "CREDENTIAL_NOT_FOUND", str(exc), req) from exc


@app.delete("/v1/api-keys/{key_id}")
def revoke_api_key(
    key_id: str, project_id: str, req: Annotated[str, Depends(request_id)]
) -> dict[str, object]:
    try:
        return plane.revoke_api_key(project_id, key_id).model_dump(mode="json")
    except (KeyError, PermissionError) as exc:
        raise _problem(404, "CREDENTIAL_NOT_FOUND", str(exc), req) from exc


@app.get("/v1/capabilities")
def capabilities() -> list[dict[str, object]]:
    return [item.model_dump(mode="json") for item in plane.capabilities()]


@app.post("/v1/jobs/estimate")
def estimate(
    project_id: str, payload: JobRequest, req: Annotated[str, Depends(request_id)]
) -> dict[str, object]:
    try:
        return plane.estimate(project_id, payload)
    except KeyError as exc:
        raise _problem(404, "PROJECT_NOT_FOUND", str(exc), req) from exc


@app.post("/v1/jobs", status_code=202)
def submit_job(
    project_id: str,
    payload: JobRequest,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    req: Annotated[str, Depends(request_id)] = "req_local_reference",
) -> dict[str, object]:
    try:
        return plane.submit_job(project_id, payload, idempotency_key or "").model_dump(mode="json")
    except KeyError as exc:
        raise _problem(404, "PROJECT_NOT_FOUND", str(exc), req) from exc
    except ValueError as exc:
        code = str(exc)
        status = 409 if code == "IDEMPOTENCY_CONFLICT" else 422
        raise _problem(status, code, "Job submission was rejected by the sandbox policy.", req) from exc


@app.get("/v1/jobs")
def list_jobs(project_id: str) -> list[dict[str, object]]:
    return [job.model_dump(mode="json") for job in plane.list_jobs(project_id)]


@app.get("/v1/jobs/{job_id}")
def get_job(job_id: str, project_id: str, req: Annotated[str, Depends(request_id)]) -> dict[str, object]:
    try:
        return plane.get_job(project_id, job_id).model_dump(mode="json")
    except (KeyError, PermissionError) as exc:
        raise _problem(404, "JOB_NOT_FOUND", str(exc), req) from exc


@app.post("/v1/jobs/{job_id}/cancel")
def cancel_job(job_id: str, project_id: str, req: Annotated[str, Depends(request_id)]) -> dict[str, object]:
    try:
        return plane.cancel(project_id, job_id).model_dump(mode="json")
    except (KeyError, PermissionError, ValueError) as exc:
        raise _problem(409, "JOB_NOT_CANCELLABLE", str(exc), req) from exc


@app.get("/v1/jobs/{job_id}/artifacts")
def list_artifacts(job_id: str, project_id: str) -> list[dict[str, object]]:
    return [
        item.model_dump(mode="json", exclude={"content"}) for item in plane.list_artifacts(project_id, job_id)
    ]


@app.get("/v1/artifacts/{artifact_id}/download")
def download_artifact(artifact_id: str, project_id: str) -> Response:
    artifact = plane.get_artifact(project_id, artifact_id)
    return Response(
        artifact.content,
        media_type=artifact.media_type,
        headers={"Digest": f"sha-256={artifact.sha256}", "Content-Disposition": "attachment"},
    )


@app.post("/v1/webhook-endpoints", status_code=201)
def create_webhook(payload: WebhookCreate) -> dict[str, object]:
    endpoint, secret = plane.create_webhook(payload.project_id, payload.url)
    return {**endpoint.model_dump(mode="json"), "secret": secret}


@app.post("/v1/webhook-endpoints/{endpoint_id}/rotate-secret")
def rotate_webhook_secret(endpoint_id: str) -> dict[str, str]:
    endpoint, _old = plane.endpoints[endpoint_id]
    fresh = new_api_secret("whsec")
    plane.endpoints[endpoint_id] = (
        endpoint.model_copy(update={"secret_hash": __import__("hashlib").sha256(fresh.encode()).hexdigest()}),
        fresh,
    )
    return {"endpoint_id": endpoint_id, "secret": fresh}


@app.get("/v1/webhook-deliveries")
def deliveries(project_id: str) -> list[dict[str, object]]:
    endpoint_ids = {item.id for item, _ in plane.endpoints.values() if item.project_id == project_id}
    return [
        item.model_dump(mode="json") for item in plane.deliveries.values() if item.endpoint_id in endpoint_ids
    ]


@app.post("/v1/webhook-deliveries/{delivery_id}/replay")
def replay(delivery_id: str, project_id: str) -> dict[str, object]:
    return plane.replay_delivery(project_id, delivery_id).model_dump(mode="json")


@app.get("/v1/usage")
def usage(project_id: str) -> list[dict[str, object]]:
    return [record.model_dump(mode="json") for record in plane.usage_for(project_id)]


@app.get("/v1/quotas")
def quotas(project_id: str) -> dict[str, object]:
    return plane.quota_decision(project_id).model_dump(mode="json")


@app.get("/v1/audit")
def audit(project_id: str) -> list[dict[str, object]]:
    return [event.model_dump(mode="json") for event in plane.audit_for(project_id)]
