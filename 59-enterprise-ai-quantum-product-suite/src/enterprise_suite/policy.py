from __future__ import annotations

from datetime import UTC, datetime

from enterprise_suite.models import Approval, Principal, ResourceRef

PERMISSIONS: dict[str, frozenset[str]] = {
    "executive-sponsor": frozenset({"can_view", "can_approve", "can_export"}),
    "crypto-lead": frozenset({"can_view", "can_request_assessment"}),
    "operations-lead": frozenset({"can_view", "can_request_assessment"}),
    "platform-lead": frozenset({"can_view", "can_approve", "can_submit_sandbox_job"}),
    "optimization-scientist": frozenset({"can_view", "can_request_assessment"}),
    "quantum-developer": frozenset({"can_view", "can_submit_sandbox_job"}),
    "risk-reviewer": frozenset({"can_view", "can_approve", "can_export"}),
    "procurement-finance": frozenset({"can_view", "can_export"}),
    "auditor": frozenset({"can_view", "can_export"}),
    "support-analyst": frozenset({"can_view"}),
}


def authorize(principal: Principal, action: str, resource: ResourceRef) -> tuple[bool, str]:
    if principal.tenant_id != resource.tenant_id:
        return False, "TENANT_MISMATCH"
    if resource.workspace_id not in principal.workspace_ids:
        return False, "WORKSPACE_DENIED"
    if principal.service and action not in {"can_view"}:
        return False, "SERVICE_IDENTITY_RESTRICTED"
    if action not in PERMISSIONS.get(principal.role, frozenset()):
        return False, "DENY_BY_DEFAULT"
    if resource.classification == "restricted" and principal.role not in {
        "executive-sponsor",
        "risk-reviewer",
        "auditor",
        "platform-lead",
    }:
        return False, "CLASSIFICATION_DENIED"
    return True, "ALLOW_POLICY_V1"


def approval_valid(
    approval: Approval,
    *,
    tenant_id: str,
    resource_id: str,
    revision: int,
    scope: str,
    budget: float,
    now: datetime | None = None,
) -> tuple[bool, str]:
    current = now or datetime.now(UTC)
    if approval.tenant_id != tenant_id:
        return False, "TENANT_MISMATCH"
    if approval.status != "granted":
        return False, "APPROVAL_NOT_GRANTED"
    if approval.expires_at <= current:
        return False, "APPROVAL_EXPIRED"
    if approval.resource_id != resource_id or approval.resource_revision != revision:
        return False, "APPROVAL_REVISION_MISMATCH"
    if approval.scope != scope:
        return False, "APPROVAL_SCOPE_MISMATCH"
    if budget > approval.budget_limit:
        return False, "APPROVAL_BUDGET_EXCEEDED"
    return True, "APPROVAL_VALID"
