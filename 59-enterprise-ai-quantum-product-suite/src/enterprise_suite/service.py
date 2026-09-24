from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any, cast
from uuid import uuid4

from enterprise_suite.assistant import grounded_assistant
from enterprise_suite.corpus import build_corpus, corpus_counts
from enterprise_suite.events import Outbox
from enterprise_suite.models import (
    Approval,
    AssistantRequest,
    AssistantResponse,
    AuditRecord,
    BenchmarkRequest,
    DecisionRequest,
    JobRequest,
    Module,
    ReportRequest,
)
from enterprise_suite.policy import approval_valid


class EnterpriseSuite:
    def __init__(self) -> None:
        self.corpus = build_corpus()
        self.outbox = Outbox()
        self.approvals: dict[str, Approval] = {}
        self.audit: list[AuditRecord] = []
        self.idempotency: dict[str, dict[str, Any]] = {}

    def _tenant_items(self, key: str, tenant_id: str) -> list[Any]:
        return [item for item in self.corpus[key] if self._tenant(item) == tenant_id]

    @staticmethod
    def _tenant(item: Any) -> str:
        return str(item.tenant_id if hasattr(item, "tenant_id") else item["tenant_id"])

    def portfolio(self, tenant_id: str) -> dict[str, Any]:
        return {
            "tenant_id": tenant_id,
            "modules": [module.value for module in Module],
            "evidence": len(self._tenant_items("evidence", tenant_id)),
            "opportunities": len(self._tenant_items("opportunities", tenant_id)),
            "experiments": len(self._tenant_items("experiments", tenant_id)),
            "recommendations": [item.model_dump() for item in self._tenant_items("recommendations", tenant_id)],
            "value_status": "hypothesis_not_realized",
        }

    def catalog(self) -> list[dict[str, Any]]:
        return [
            {
                "module": module.value,
                "lifecycle": "technical-candidate",
                "standalone": True,
                "owner": f"owner-{module.value}",
                "contract_revision": "v1alpha1",
            }
            for module in Module
        ]

    def evidence(self, evidence_id: str, tenant_id: str) -> dict[str, Any] | None:
        for item in self.corpus["evidence"]:
            if item.evidence_id == evidence_id and item.tenant_id == tenant_id:
                return cast(dict[str, Any], item.model_dump())
        return None

    def risks(self, tenant_id: str) -> list[dict[str, Any]]:
        return [
            {
                "risk_id": f"risk-{tenant_id}-{index}",
                "tenant_id": tenant_id,
                "severity": severity,
                "evidence_id": f"ev-{tenant_id}-{index:03d}",
                "status": "review-required",
            }
            for index, severity in enumerate(("high", "medium", "low"))
        ]

    def decide(self, recommendation_id: str, request: DecisionRequest) -> dict[str, Any]:
        matches = [item for item in self.corpus["recommendations"] if item.recommendation_id == recommendation_id and item.tenant_id == request.tenant_id]
        if not matches:
            raise LookupError("recommendation not found")
        record = {
            "decision_id": f"decision-{uuid4()}",
            "recommendation_id": recommendation_id,
            **request.model_dump(),
            "status": "recorded-human-decision",
        }
        self.outbox.publish("DecisionRecorded", request.tenant_id, recommendation_id, record["decision_id"])
        return record

    def request_approval(self, tenant_id: str, requester_id: str, resource_id: str, revision: int, scope: str) -> Approval:
        approval = Approval(
            approval_id=f"approval-{uuid4()}",
            tenant_id=tenant_id,
            requester_id=requester_id,
            resource_id=resource_id,
            resource_revision=revision,
            scope=scope,
            budget_limit=1000,
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        )
        self.approvals[approval.approval_id] = approval
        self.outbox.publish("ApprovalRequested", tenant_id, resource_id, approval.approval_id)
        return approval

    def grant_approval(self, approval_id: str, approver_id: str) -> Approval:
        approval = self.approvals[approval_id]
        updated = approval.model_copy(update={"status": "granted", "approver_id": approver_id})
        self.approvals[approval_id] = updated
        self.outbox.publish("ApprovalGranted", updated.tenant_id, updated.resource_id, approval_id)
        return updated

    def submit_job(self, request: JobRequest) -> dict[str, Any]:
        if request.idempotency_key in self.idempotency:
            return self.idempotency[request.idempotency_key]
        approval = self.approvals.get(request.approval_id)
        if approval is None:
            raise PermissionError("approval required")
        valid, reason = approval_valid(
            approval,
            tenant_id=request.tenant_id,
            resource_id=request.capability_id,
            revision=1,
            scope="sandbox-job",
            budget=100,
        )
        if not valid:
            raise PermissionError(reason)
        result: dict[str, Any] = {
            "job_id": f"job-{uuid4()}",
            "tenant_id": request.tenant_id,
            "status": "completed-local-sandbox",
            "provider_action": False,
            "input_reference": request.input_reference,
        }
        self.approvals[approval.approval_id] = approval.model_copy(update={"status": "consumed"})
        self.idempotency[request.idempotency_key] = result
        self.outbox.publish("QuantumJobCompleted", request.tenant_id, result["job_id"], result["job_id"])
        return result

    def benchmark(self, request: BenchmarkRequest) -> dict[str, Any]:
        candidates = self._tenant_items("opportunities", request.tenant_id)
        if request.opportunity_id not in {item["opportunity_id"] for item in candidates}:
            raise LookupError("opportunity not found")
        result: dict[str, Any] = {
            "benchmark_id": f"benchmark-{uuid4()}",
            "tenant_id": request.tenant_id,
            "baseline": request.baseline,
            "score": 0.71,
            "uncertainty": "Synthetic benchmark; no quantum advantage claim.",
        }
        self.outbox.publish("BenchmarkCompleted", request.tenant_id, request.opportunity_id, result["benchmark_id"])
        return result

    def usage(self, tenant_id: str) -> dict[str, Any]:
        return {
            "tenant_id": tenant_id,
            "units": {"evidence_records": 60, "sandbox_jobs": 0, "reports": 0},
            "estimated_cost": 0,
            "currency": "USD",
            "provenance": "synthetic-showback-v1",
        }

    def report(self, request: ReportRequest) -> dict[str, Any]:
        report: dict[str, Any] = {
            "report_id": f"report-{uuid4()}",
            "tenant_id": request.tenant_id,
            "type": request.report_type,
            "source_counts": {
                "evidence": len(self._tenant_items("evidence", request.tenant_id)),
                "opportunities": len(self._tenant_items("opportunities", request.tenant_id)),
            },
            "limitations": ["synthetic data", "technical candidate", "human approval pending"],
        }
        self.outbox.publish("ReportPublished", request.tenant_id, report["report_id"], report["report_id"])
        return report

    def assist(self, request: AssistantRequest) -> AssistantResponse:
        return grounded_assistant(request, self.corpus["evidence"])

    def health(self) -> dict[str, Any]:
        return {"status": "ok", "mode": "synthetic-local", "counts": corpus_counts(self.corpus)}
