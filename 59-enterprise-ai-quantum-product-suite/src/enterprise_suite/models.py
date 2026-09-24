from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field


class Module(StrEnum):
    CRYPTO = "crypto-readiness"
    OPTIMIZATION = "optimization-studio"
    QUANTUM = "quantum-workbench"
    GOVERNANCE = "shared-governance"


class DecisionOutcome(StrEnum):
    INVEST = "invest"
    HOLD = "hold"
    KILL = "kill"


class Principal(BaseModel):
    identity_id: str
    tenant_id: str
    role: str
    workspace_ids: tuple[str, ...] = ()
    service: bool = False


class ResourceRef(BaseModel):
    resource_id: str
    tenant_id: str
    workspace_id: str
    module: Module
    classification: Literal["public", "internal", "restricted"] = "internal"
    revision: int = Field(default=1, ge=1)


class Evidence(BaseModel):
    evidence_id: str
    tenant_id: str
    module: Module
    title: str
    source: str
    sha256: str
    confidence: float = Field(ge=0, le=1)
    correlation_id: str


class Recommendation(BaseModel):
    recommendation_id: str
    tenant_id: str
    module: Module
    summary: str
    evidence_ids: tuple[str, ...] = Field(min_length=1)
    uncertainty: str
    decision_owner: str
    revision: int = 1


class Approval(BaseModel):
    approval_id: str
    tenant_id: str
    requester_id: str
    resource_id: str
    resource_revision: int
    scope: str
    budget_limit: float = Field(ge=0)
    expires_at: datetime
    status: Literal["requested", "granted", "denied", "expired", "consumed"] = "requested"
    approver_id: str | None = None


class DecisionRequest(BaseModel):
    tenant_id: str
    owner_id: str
    outcome: DecisionOutcome
    assumptions: tuple[str, ...] = ()


class JobRequest(BaseModel):
    tenant_id: str
    capability_id: str
    approval_id: str
    idempotency_key: str
    input_reference: str


class BenchmarkRequest(BaseModel):
    tenant_id: str
    opportunity_id: str
    baseline: str = "deterministic"


class ReportRequest(BaseModel):
    tenant_id: str
    report_type: Literal["portfolio", "assurance", "usage"]


class AuditRecord(BaseModel):
    record_id: str
    tenant_id: str
    action: str
    result: str
    reason_code: str
    policy_version: str = "policy.v1"
    correlation_id: str
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    details: dict[str, Any] = Field(default_factory=dict)


class AssistantRequest(BaseModel):
    tenant_id: str
    question: str
    evidence_ids: tuple[str, ...]


class AssistantResponse(BaseModel):
    answer: str
    citations: tuple[str, ...]
    abstained: bool
    baseline: str = "deterministic-grounded-v1"
    model_candidate: str = "disabled-local-reference"
    requires_human_approval: bool = True
    side_effects: tuple[str, ...] = ()
