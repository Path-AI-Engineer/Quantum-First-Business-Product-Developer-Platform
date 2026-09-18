"""Tenant-aware in-memory reference control plane."""

from __future__ import annotations

import hashlib
import json
import secrets
import time
from dataclasses import dataclass
from datetime import UTC, datetime

from quantum_platform.models import (
    ApiKeyResource,
    ApiKeyReveal,
    Artifact,
    AuditEvent,
    Capability,
    Environment,
    Job,
    JobRequest,
    JobState,
    Operation,
    Organization,
    Project,
    QuotaDecision,
    UsageRecord,
    WebhookDelivery,
    WebhookEndpoint,
)
from quantum_platform.providers import (
    ContractStubProvider,
    DeterministicFakeProvider,
    LocalQuantumProvider,
    Provider,
)
from quantum_platform.security import StoredSecret, new_api_secret, sign_webhook, store_secret, verify_secret
from quantum_platform.state_machine import assert_transition


@dataclass(frozen=True)
class StoredKey:
    resource: ApiKeyResource
    secret: StoredSecret


def opaque(prefix: str) -> str:
    return f"{prefix}_{secrets.token_hex(8)}"


class ControlPlane:
    def __init__(self) -> None:
        self.organizations: dict[str, Organization] = {}
        self.projects: dict[str, Project] = {}
        self.keys: dict[str, StoredKey] = {}
        self.jobs: dict[str, Job] = {}
        self.idempotency: dict[tuple[str, Environment, str], tuple[str, str]] = {}
        self.submission_ledger: dict[str, str] = {}
        self.artifacts: dict[str, Artifact] = {}
        self.endpoints: dict[str, tuple[WebhookEndpoint, str]] = {}
        self.deliveries: dict[str, WebhookDelivery] = {}
        self.usage: dict[str, UsageRecord] = {}
        self.audit: list[AuditEvent] = []
        self.providers: dict[str, Provider] = {
            "fake": DeterministicFakeProvider(),
            "local": LocalQuantumProvider(),
            "ibm": ContractStubProvider("ibm"),
            "braket": ContractStubProvider("braket"),
            "azure": ContractStubProvider("azure"),
        }
        self.concurrent_limit = 4
        self.daily_job_limit = 100

    def _audit(self, project_id: str | None, action: str, subject_id: str, correlation_id: str) -> None:
        self.audit.append(
            AuditEvent(
                id=opaque("aud"),
                project_id=project_id,
                action=action,
                subject_id=subject_id,
                correlation_id=correlation_id,
            )
        )

    def create_organization(self, name: str) -> Organization:
        resource = Organization(id=opaque("org"), name=name)
        self.organizations[resource.id] = resource
        self._audit(None, "organization.created", resource.id, opaque("cor"))
        return resource

    def create_project(self, organization_id: str, name: str, environment: Environment) -> Project:
        if organization_id not in self.organizations:
            raise KeyError("organization not found")
        resource = Project(
            id=opaque("prj"), organization_id=organization_id, name=name, environment=environment
        )
        self.projects[resource.id] = resource
        self._audit(resource.id, "project.created", resource.id, opaque("cor"))
        return resource

    def create_api_key(self, project_id: str, scopes: tuple[str, ...]) -> ApiKeyReveal:
        self._project(project_id)
        key_id = opaque("key")
        prefix = f"qdp_{self.projects[project_id].environment.value}_{key_id[-6:]}"
        raw = new_api_secret(prefix)
        resource = ApiKeyResource(id=key_id, project_id=project_id, prefix=prefix, scopes=scopes)
        self.keys[key_id] = StoredKey(resource=resource, secret=store_secret(raw, prefix))
        self._audit(project_id, "credential.created", key_id, opaque("cor"))
        return ApiKeyReveal(**resource.model_dump(), secret=raw)

    def authenticate(self, raw: str, required_scope: str) -> ApiKeyResource:
        for key_id, stored in self.keys.items():
            if raw.startswith(stored.secret.prefix) and verify_secret(
                raw, stored.secret.salt, stored.secret.digest
            ):
                if stored.resource.revoked_at is not None:
                    raise PermissionError("CREDENTIAL_REVOKED")
                if required_scope not in stored.resource.scopes:
                    raise PermissionError("SCOPE_DENIED")
                resource = stored.resource.model_copy(update={"last_used_at": datetime.now(UTC)})
                self.keys[key_id] = StoredKey(resource=resource, secret=stored.secret)
                return resource
        raise PermissionError("CREDENTIAL_INVALID")

    def rotate_api_key(self, project_id: str, key_id: str) -> ApiKeyReveal:
        stored = self._key(project_id, key_id)
        self.keys[key_id] = StoredKey(
            resource=stored.resource.model_copy(update={"revoked_at": datetime.now(UTC)}),
            secret=stored.secret,
        )
        return self.create_api_key(project_id, stored.resource.scopes)

    def revoke_api_key(self, project_id: str, key_id: str) -> ApiKeyResource:
        stored = self._key(project_id, key_id)
        resource = stored.resource.model_copy(update={"revoked_at": datetime.now(UTC)})
        self.keys[key_id] = StoredKey(resource=resource, secret=stored.secret)
        self._audit(project_id, "credential.revoked", key_id, opaque("cor"))
        return resource

    def capabilities(self) -> list[Capability]:
        items: list[Capability] = []
        for provider in self.providers:
            available = "available" if provider in {"fake", "local"} else "credentials_required"
            for operation in Operation:
                local_supported = operation in {Operation.CIRCUIT_SAMPLE, Operation.OBSERVABLE_ESTIMATE}
                status = available
                degradations: tuple[str, ...] = ()
                if provider == "local" and not local_supported:
                    status = "unsupported"
                    degradations = ("No optimization/workflow executor in bounded local sampler",)
                if provider not in {"fake", "local"}:
                    degradations = ("Contract stub only; no live cloud submission",)
                items.append(
                    Capability(
                        operation=operation,
                        provider=provider,
                        backend=f"{provider}-sandbox",
                        availability=status,
                        limits={"max_shots": 4096, "max_qubits": 8},
                        source="versioned-local-fixture",
                        freshness="2026-09-18",
                        degradations=degradations,
                    )
                )
        return items

    def quota_decision(self, project_id: str) -> QuotaDecision:
        self._project(project_id)
        active = sum(
            1
            for job in self.jobs.values()
            if job.project_id == project_id
            and job.state not in {JobState.SUCCEEDED, JobState.FAILED, JobState.CANCELLED}
        )
        total = sum(1 for job in self.jobs.values() if job.project_id == project_id)
        if active >= self.concurrent_limit:
            return QuotaDecision(
                allowed=False,
                code="CONCURRENT_JOB_LIMIT",
                limit=self.concurrent_limit,
                current=active,
                retry_after_seconds=10,
            )
        if total >= self.daily_job_limit:
            return QuotaDecision(
                allowed=False,
                code="DAILY_JOB_LIMIT",
                limit=self.daily_job_limit,
                current=total,
                retry_after_seconds=3600,
            )
        return QuotaDecision(allowed=True, code="ALLOWED", limit=self.daily_job_limit, current=total)

    def estimate(self, project_id: str, request: JobRequest) -> dict[str, object]:
        self._project(project_id)
        quantity = float(request.payload.get("shots", 1))
        return {
            "classification": "estimate",
            "quantity": quantity,
            "unit": "shots" if "shots" in request.payload else "job",
            "currency": "USD",
            "amount": round(quantity * 0.00001, 6),
            "provenance": "sandbox pricing fixture; not billing",
        }

    def submit_job(self, project_id: str, request: JobRequest, idempotency_key: str) -> Job:
        project = self._project(project_id)
        if not idempotency_key or len(idempotency_key) > 128:
            raise ValueError("IDEMPOTENCY_KEY_REQUIRED")
        fingerprint = hashlib.sha256(request.model_dump_json().encode()).hexdigest()
        identity = (project_id, project.environment, idempotency_key)
        existing = self.idempotency.get(identity)
        if existing:
            prior_fingerprint, job_id = existing
            if prior_fingerprint != fingerprint:
                raise ValueError("IDEMPOTENCY_CONFLICT")
            return self.jobs[job_id]
        decision = self.quota_decision(project_id)
        if not decision.allowed:
            raise ValueError(decision.code)
        correlation_id = opaque("cor")
        job = Job(
            id=opaque("job"),
            project_id=project_id,
            environment=project.environment,
            request=request,
            state=JobState.ACCEPTED,
            correlation_id=correlation_id,
        )
        self.jobs[job.id] = job
        self.idempotency[identity] = (fingerprint, job.id)
        self._audit(project_id, "job.accepted", job.id, correlation_id)
        for target in (JobState.VALIDATING, JobState.QUEUED, JobState.DISPATCHING):
            job = self.transition(job.id, target, expected_version=job.version)
        try:
            provider = self.providers[request.provider]
        except KeyError:
            return self._fail(job, "PROVIDER_UNKNOWN")
        try:
            result = provider.submit(request, idempotency_key)
        except ValueError as exc:
            return self._fail(job, str(exc))
        if result.submission_id in self.submission_ledger:
            raise RuntimeError("DUPLICATE_PROVIDER_SUBMISSION")
        self.submission_ledger[result.submission_id] = job.id
        job = self.jobs[job.id].model_copy(
            update={"provider_submission_id": result.submission_id, "version": self.jobs[job.id].version + 1}
        )
        self.jobs[job.id] = job
        job = self.transition(job.id, JobState.RUNNING, expected_version=job.version)
        job = self.jobs[job.id].model_copy(update={"result": result.result, "version": job.version + 1})
        self.jobs[job.id] = job
        job = self.transition(job.id, JobState.SUCCEEDED, expected_version=job.version)
        self._record_usage(job, result.usage, result.usage_unit)
        self._create_manifest(job)
        return job

    def _fail(self, job: Job, code: str) -> Job:
        job = self.jobs[job.id].model_copy(update={"error_code": code, "version": job.version + 1})
        self.jobs[job.id] = job
        return self.transition(job.id, JobState.FAILED, expected_version=job.version)

    def transition(self, job_id: str, target: JobState, expected_version: int) -> Job:
        current = self.jobs[job_id]
        if current.version != expected_version:
            raise ValueError("OPTIMISTIC_CONCURRENCY_CONFLICT")
        assert_transition(current.state, target)
        updated = current.model_copy(
            update={"state": target, "version": current.version + 1, "updated_at": datetime.now(UTC)}
        )
        self.jobs[job_id] = updated
        self._audit(current.project_id, f"job.{target.value.lower()}", current.id, current.correlation_id)
        return updated

    def cancel(self, project_id: str, job_id: str) -> Job:
        job = self._job(project_id, job_id)
        if job.state == JobState.QUEUED:
            return self.transition(job.id, JobState.CANCELLED, job.version)
        if job.state == JobState.RUNNING:
            job = self.transition(job.id, JobState.CANCELLING, job.version)
            return self.transition(job.id, JobState.CANCELLED, job.version)
        raise ValueError("JOB_NOT_CANCELLABLE")

    def list_jobs(self, project_id: str) -> list[Job]:
        self._project(project_id)
        return [item for item in self.jobs.values() if item.project_id == project_id]

    def get_job(self, project_id: str, job_id: str) -> Job:
        return self._job(project_id, job_id)

    def list_artifacts(self, project_id: str, job_id: str) -> list[Artifact]:
        self._job(project_id, job_id)
        return [a for a in self.artifacts.values() if a.project_id == project_id and a.job_id == job_id]

    def get_artifact(self, project_id: str, artifact_id: str) -> Artifact:
        artifact = self.artifacts[artifact_id]
        if artifact.project_id != project_id:
            raise PermissionError("OBJECT_ACCESS_DENIED")
        if hashlib.sha256(artifact.content.encode()).hexdigest() != artifact.sha256:
            raise ValueError("ARTIFACT_INTEGRITY_FAILED")
        return artifact

    def create_webhook(self, project_id: str, url: str) -> tuple[WebhookEndpoint, str]:
        self._project(project_id)
        if not url.startswith("https://") and not url.startswith("http://127.0.0.1"):
            raise ValueError("WEBHOOK_TARGET_DENIED")
        raw = new_api_secret("whsec")
        endpoint = WebhookEndpoint(
            id=opaque("whe"),
            project_id=project_id,
            url=url,
            secret_hash=hashlib.sha256(raw.encode()).hexdigest(),
        )
        self.endpoints[endpoint.id] = (endpoint, raw)
        self._audit(project_id, "webhook.created", endpoint.id, opaque("cor"))
        return endpoint, raw

    def deliver(self, project_id: str, endpoint_id: str, event_id: str, event_type: str) -> WebhookDelivery:
        endpoint, secret = self.endpoints[endpoint_id]
        if endpoint.project_id != project_id:
            raise PermissionError("OBJECT_ACCESS_DENIED")
        delivery_id = opaque("dlv")
        timestamp = int(time.time())
        body = json.dumps({"id": event_id, "type": event_type}, sort_keys=True).encode()
        delivery = WebhookDelivery(
            id=delivery_id,
            endpoint_id=endpoint_id,
            event_id=event_id,
            event_type=event_type,
            attempt=1,
            status="delivered",
            signature=sign_webhook(secret, timestamp, delivery_id, body),
            timestamp=timestamp,
        )
        self.deliveries[delivery.id] = delivery
        return delivery

    def replay_delivery(self, project_id: str, delivery_id: str) -> WebhookDelivery:
        original = self.deliveries[delivery_id]
        endpoint = self.endpoints[original.endpoint_id][0]
        if endpoint.project_id != project_id:
            raise PermissionError("OBJECT_ACCESS_DENIED")
        replay = self.deliver(project_id, original.endpoint_id, original.event_id, original.event_type)
        replay = replay.model_copy(
            update={"original_delivery_id": original.id, "attempt": original.attempt + 1}
        )
        self.deliveries[replay.id] = replay
        return replay

    def usage_for(self, project_id: str) -> list[UsageRecord]:
        self._project(project_id)
        return [record for record in self.usage.values() if record.project_id == project_id]

    def audit_for(self, project_id: str) -> list[AuditEvent]:
        self._project(project_id)
        return [event for event in self.audit if event.project_id == project_id]

    def _record_usage(self, job: Job, quantity: float, unit: str) -> None:
        key = f"{job.id}:{job.provider_submission_id}:{unit}"
        if any(record.deduplication_key == key for record in self.usage.values()):
            return
        record = UsageRecord(
            id=opaque("use"),
            project_id=job.project_id,
            environment=job.environment,
            operation=job.request.operation,
            quantity=quantity,
            unit=unit,
            classification="actual",
            source=job.request.provider,
            deduplication_key=key,
            reconciliation_status="reconciled",
        )
        self.usage[record.id] = record

    def _create_manifest(self, job: Job) -> None:
        content = json.dumps(
            {
                "job_id": job.id,
                "request_revision": job.request_revision,
                "provider_submission_id": job.provider_submission_id,
                "state": job.state.value,
                "result": job.result,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        digest = hashlib.sha256(content.encode()).hexdigest()
        artifact = Artifact(
            id=f"art_{digest[:16]}",
            project_id=job.project_id,
            job_id=job.id,
            media_type="application/json",
            bytes_count=len(content.encode()),
            sha256=digest,
            content=content,
        )
        self.artifacts[artifact.id] = artifact

    def _project(self, project_id: str) -> Project:
        try:
            return self.projects[project_id]
        except KeyError as exc:
            raise KeyError("project not found") from exc

    def _key(self, project_id: str, key_id: str) -> StoredKey:
        stored = self.keys[key_id]
        if stored.resource.project_id != project_id:
            raise PermissionError("OBJECT_ACCESS_DENIED")
        return stored

    def _job(self, project_id: str, job_id: str) -> Job:
        job = self.jobs[job_id]
        if job.project_id != project_id:
            raise PermissionError("OBJECT_ACCESS_DENIED")
        return job
