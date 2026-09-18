import hashlib

import pytest

from quantum_platform.models import Environment, JobRequest, JobState, Operation


@pytest.mark.parametrize("environment", list(Environment))
def test_tenant_bootstrap_and_one_time_key(seeded, environment: Environment) -> None:
    control, project_id, _ = seeded
    key = control.create_api_key(project_id, ("jobs:read", "jobs:write"))
    assert key.secret.startswith(key.prefix)
    assert key.secret not in repr(control.keys[key.id])
    authenticated = control.authenticate(key.secret, "jobs:write")
    assert authenticated.project_id == project_id
    assert authenticated.last_used_at is not None
    assert control.projects[project_id].environment is not environment or environment is Environment.SANDBOX


def test_key_scope_rotation_and_revocation(seeded) -> None:
    control, project_id, other_id = seeded
    original = control.create_api_key(project_id, ("jobs:read",))
    with pytest.raises(PermissionError, match="SCOPE_DENIED"):
        control.authenticate(original.secret, "jobs:write")
    with pytest.raises(PermissionError, match="OBJECT_ACCESS_DENIED"):
        control.rotate_api_key(other_id, original.id)
    rotated = control.rotate_api_key(project_id, original.id)
    with pytest.raises(PermissionError, match="CREDENTIAL_REVOKED"):
        control.authenticate(original.secret, "jobs:read")
    control.revoke_api_key(project_id, rotated.id)
    with pytest.raises(PermissionError, match="CREDENTIAL_REVOKED"):
        control.authenticate(rotated.secret, "jobs:read")
    with pytest.raises(PermissionError, match="CREDENTIAL_INVALID"):
        control.authenticate("qdp_sandbox_invalid", "jobs:read")


@pytest.mark.parametrize("operation", list(Operation))
def test_fake_provider_golden_paths_are_idempotent(seeded, operation: Operation) -> None:
    control, project_id, _ = seeded
    request = JobRequest(operation=operation, provider="fake", payload={"shots": 32, "label": operation})
    first = control.submit_job(project_id, request, f"idem-{operation}")
    second = control.submit_job(project_id, request, f"idem-{operation}")
    assert first.id == second.id
    assert first.state is JobState.SUCCEEDED
    assert first.result and first.result["normalized"] is True
    assert len(control.submission_ledger) == 1
    assert len(control.usage_for(project_id)) == 1
    artifacts = control.list_artifacts(project_id, first.id)
    assert len(artifacts) == 1
    assert control.get_artifact(project_id, artifacts[0].id).sha256 == artifacts[0].sha256


@pytest.mark.parametrize("qubits,shots", [(1, 1), (2, 64), (3, 257), (8, 4096)])
def test_local_sampler_is_bounded_and_reproducible(seeded, qubits: int, shots: int) -> None:
    control, project_id, _ = seeded
    request = JobRequest(
        operation=Operation.CIRCUIT_SAMPLE,
        provider="local",
        payload={"qubits": qubits, "shots": shots},
    )
    job = control.submit_job(project_id, request, f"local-{qubits}-{shots}")
    assert job.result
    counts = job.result["counts"]
    assert isinstance(counts, dict)
    assert sum(counts.values()) == shots
    assert len(counts) == 2**qubits


@pytest.mark.parametrize(
    "job_request,code",
    [
        (JobRequest(operation="workflow.run", provider="local"), "CAPABILITY_UNSUPPORTED"),
        (
            JobRequest(operation="circuit.sample", provider="local", payload={"shots": 5000}),
            "WORKLOAD_LIMIT_EXCEEDED",
        ),
        (JobRequest(operation="circuit.sample", provider="missing"), "PROVIDER_UNKNOWN"),
        (
            JobRequest(operation="circuit.sample", provider="fake", payload={"mode": "permanent_failure"}),
            "PROVIDER_REQUEST_REJECTED",
        ),
        (JobRequest(operation="circuit.sample", provider="azure"), "PROVIDER_UNAVAILABLE_NO_CREDENTIALS"),
    ],
)
def test_explicit_provider_failures(seeded, job_request: JobRequest, code: str) -> None:
    control, project_id, _ = seeded
    job = control.submit_job(project_id, job_request, f"failure-{code}")
    assert job.state is JobState.FAILED
    assert job.error_code == code


def test_idempotency_poisoning_is_rejected(seeded) -> None:
    control, project_id, _ = seeded
    control.submit_job(project_id, JobRequest(operation="circuit.sample"), "stable-key")
    with pytest.raises(ValueError, match="IDEMPOTENCY_CONFLICT"):
        control.submit_job(project_id, JobRequest(operation="workflow.run"), "stable-key")
    with pytest.raises(ValueError, match="IDEMPOTENCY_KEY_REQUIRED"):
        control.submit_job(project_id, JobRequest(operation="workflow.run"), "")
    with pytest.raises(ValueError, match="IDEMPOTENCY_KEY_REQUIRED"):
        control.submit_job(project_id, JobRequest(operation="workflow.run"), "x" * 129)


def test_object_level_authorization_and_integrity(seeded) -> None:
    control, project_id, other_id = seeded
    job = control.submit_job(project_id, JobRequest(operation="resource.estimate"), "ownership")
    artifact = control.list_artifacts(project_id, job.id)[0]
    with pytest.raises(PermissionError, match="OBJECT_ACCESS_DENIED"):
        control.get_job(other_id, job.id)
    with pytest.raises(PermissionError, match="OBJECT_ACCESS_DENIED"):
        control.get_artifact(other_id, artifact.id)
    control.artifacts[artifact.id] = artifact.model_copy(update={"content": "tampered"})
    with pytest.raises(ValueError, match="ARTIFACT_INTEGRITY_FAILED"):
        control.get_artifact(project_id, artifact.id)


def test_quota_and_usage_reconciliation(seeded) -> None:
    control, project_id, _ = seeded
    control.daily_job_limit = 2
    for index in range(2):
        control.submit_job(project_id, JobRequest(operation="resource.estimate"), f"quota-{index}")
    decision = control.quota_decision(project_id)
    assert decision.allowed is False
    assert decision.code == "DAILY_JOB_LIMIT"
    with pytest.raises(ValueError, match="DAILY_JOB_LIMIT"):
        control.submit_job(project_id, JobRequest(operation="resource.estimate"), "quota-over")
    estimate = control.estimate(project_id, JobRequest(operation="circuit.sample", payload={"shots": 10}))
    assert estimate["classification"] == "estimate"
    assert estimate["provenance"] == "sandbox pricing fixture; not billing"
    usage = control.usage_for(project_id)
    assert len({item.deduplication_key for item in usage}) == len(usage)


def test_concurrent_quota_branch(seeded) -> None:
    control, project_id, _ = seeded
    control.concurrent_limit = 0
    decision = control.quota_decision(project_id)
    assert decision.code == "CONCURRENT_JOB_LIMIT"
    assert decision.retry_after_seconds == 10


def test_artifact_digest_matches_content(seeded) -> None:
    control, project_id, _ = seeded
    job = control.submit_job(project_id, JobRequest(operation="workflow.run"), "manifest")
    artifact = control.list_artifacts(project_id, job.id)[0]
    assert hashlib.sha256(artifact.content.encode()).hexdigest() == artifact.sha256
