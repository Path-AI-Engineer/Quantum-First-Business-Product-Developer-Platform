"""Public resources for the sandbox control plane."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> datetime:
    return datetime.now(UTC)


class Environment(StrEnum):
    SANDBOX = "sandbox"
    PRODUCTION = "production"


class JobState(StrEnum):
    ACCEPTED = "ACCEPTED"
    VALIDATING = "VALIDATING"
    REJECTED = "REJECTED"
    QUEUED = "QUEUED"
    DISPATCHING = "DISPATCHING"
    RUNNING = "RUNNING"
    CANCELLING = "CANCELLING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    UNKNOWN_RECONCILIATION_REQUIRED = "UNKNOWN_RECONCILIATION_REQUIRED"


TERMINAL_STATES = {
    JobState.REJECTED,
    JobState.SUCCEEDED,
    JobState.FAILED,
    JobState.CANCELLED,
    JobState.EXPIRED,
}


class Operation(StrEnum):
    CIRCUIT_SAMPLE = "circuit.sample"
    OBSERVABLE_ESTIMATE = "observable.estimate"
    OPTIMIZATION_SOLVE = "optimization.solve"
    RESOURCE_ESTIMATE = "resource.estimate"
    WORKFLOW_RUN = "workflow.run"


class Organization(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: str
    name: str = Field(min_length=2, max_length=80)
    created_at: datetime = Field(default_factory=utc_now)


class Project(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: str
    organization_id: str
    name: str = Field(min_length=2, max_length=80)
    environment: Environment


class ApiKeyResource(BaseModel):
    id: str
    project_id: str
    prefix: str
    scopes: tuple[str, ...]
    expires_at: datetime | None = None
    revoked_at: datetime | None = None
    last_used_at: datetime | None = None


class ApiKeyReveal(ApiKeyResource):
    secret: str


class Capability(BaseModel):
    operation: Operation
    provider: str
    backend: str
    availability: str
    limits: dict[str, int]
    source: str
    freshness: str
    degradations: tuple[str, ...] = ()
    schema_revision: str = "1.0.0"


class JobRequest(BaseModel):
    operation: Operation
    provider: str = "fake"
    payload: dict[str, Any] = Field(default_factory=dict)


class Job(BaseModel):
    id: str
    project_id: str
    environment: Environment
    request: JobRequest
    request_revision: int = 1
    state: JobState
    version: int = 1
    correlation_id: str
    provider_submission_id: str | None = None
    result: dict[str, Any] | None = None
    error_code: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class Artifact(BaseModel):
    id: str
    project_id: str
    job_id: str
    media_type: str
    bytes_count: int
    sha256: str
    content: str


class QuotaDecision(BaseModel):
    allowed: bool
    code: str
    limit: int
    current: int
    retry_after_seconds: int | None = None


class UsageRecord(BaseModel):
    id: str
    project_id: str
    environment: Environment
    operation: Operation
    quantity: float
    unit: str
    classification: str
    source: str
    deduplication_key: str
    reconciliation_status: str
    created_at: datetime = Field(default_factory=utc_now)


class AuditEvent(BaseModel):
    id: str
    project_id: str | None
    action: str
    subject_id: str
    correlation_id: str
    details: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)


class WebhookEndpoint(BaseModel):
    id: str
    project_id: str
    url: str
    secret_hash: str
    active: bool = True


class WebhookDelivery(BaseModel):
    id: str
    endpoint_id: str
    event_id: str
    event_type: str
    attempt: int
    status: str
    signature: str
    timestamp: int
    original_delivery_id: str | None = None


class ProblemDetails(BaseModel):
    type: str = "about:blank"
    title: str
    status: int
    code: str
    detail: str
    correlation_id: str
    remediation_hint: str
