import json
import time

import pytest

from quantum_platform.models import Job, JobRequest, JobState
from quantum_platform.security import sign_webhook, verify_webhook
from quantum_platform.state_machine import assert_transition, can_transition


@pytest.mark.parametrize(
    "current,target,allowed",
    [
        (JobState.ACCEPTED, JobState.VALIDATING, True),
        (JobState.VALIDATING, JobState.QUEUED, True),
        (JobState.VALIDATING, JobState.REJECTED, True),
        (JobState.QUEUED, JobState.DISPATCHING, True),
        (JobState.QUEUED, JobState.CANCELLED, True),
        (JobState.DISPATCHING, JobState.RUNNING, True),
        (JobState.RUNNING, JobState.CANCELLING, True),
        (JobState.CANCELLING, JobState.CANCELLED, True),
        (JobState.RUNNING, JobState.SUCCEEDED, True),
        (JobState.SUCCEEDED, JobState.RUNNING, False),
        (JobState.FAILED, JobState.RUNNING, False),
        (JobState.ACCEPTED, JobState.SUCCEEDED, False),
    ],
)
def test_state_machine(current: JobState, target: JobState, allowed: bool) -> None:
    assert can_transition(current, target) is allowed
    if allowed:
        assert_transition(current, target)
    else:
        with pytest.raises(ValueError, match="illegal transition"):
            assert_transition(current, target)


def test_optimistic_concurrency_and_cancel(seeded) -> None:
    control, project_id, _ = seeded
    request = JobRequest(operation="workflow.run")
    job = Job(
        id="job_manual",
        project_id=project_id,
        environment="sandbox",
        request=request,
        state=JobState.QUEUED,
        correlation_id="cor_manual",
    )
    control.jobs[job.id] = job
    with pytest.raises(ValueError, match="OPTIMISTIC_CONCURRENCY_CONFLICT"):
        control.transition(job.id, JobState.DISPATCHING, 9)
    cancelled = control.cancel(project_id, job.id)
    assert cancelled.state is JobState.CANCELLED
    with pytest.raises(ValueError, match="JOB_NOT_CANCELLABLE"):
        control.cancel(project_id, job.id)


def test_running_cancel_path(seeded) -> None:
    control, project_id, _ = seeded
    job = Job(
        id="job_running",
        project_id=project_id,
        environment="sandbox",
        request=JobRequest(operation="workflow.run"),
        state=JobState.RUNNING,
        correlation_id="cor_running",
    )
    control.jobs[job.id] = job
    assert control.cancel(project_id, job.id).state is JobState.CANCELLED


def test_webhook_signatures_replay_and_ssrf_policy(seeded) -> None:
    control, project_id, other_id = seeded
    endpoint, secret = control.create_webhook(project_id, "https://receiver.example/hooks")
    delivery = control.deliver(project_id, endpoint.id, "evt_1", "job.succeeded")
    body = json.dumps({"id": "evt_1", "type": "job.succeeded"}, sort_keys=True).encode()
    assert verify_webhook(secret, delivery.timestamp, delivery.id, body, delivery.signature)
    assert not verify_webhook(secret, delivery.timestamp, delivery.id, b"tampered", delivery.signature)
    assert not verify_webhook(
        secret,
        delivery.timestamp,
        delivery.id,
        body,
        delivery.signature,
        now=delivery.timestamp + 301,
    )
    replay = control.replay_delivery(project_id, delivery.id)
    assert replay.id != delivery.id
    assert replay.event_id == delivery.event_id
    assert replay.original_delivery_id == delivery.id
    with pytest.raises(PermissionError, match="OBJECT_ACCESS_DENIED"):
        control.deliver(other_id, endpoint.id, "evt_2", "job.failed")
    with pytest.raises(PermissionError, match="OBJECT_ACCESS_DENIED"):
        control.replay_delivery(other_id, delivery.id)
    with pytest.raises(ValueError, match="WEBHOOK_TARGET_DENIED"):
        control.create_webhook(project_id, "http://169.254.169.254/latest/meta-data")


@pytest.mark.parametrize("timestamp_delta", [-400, -301, 0, 300, 301, 400])
def test_webhook_replay_window(timestamp_delta: int) -> None:
    now = int(time.time())
    body = b"{}"
    signature = sign_webhook("secret", now, "delivery", body)
    expected = abs(timestamp_delta) <= 300
    assert verify_webhook("secret", now, "delivery", body, signature, now=now + timestamp_delta) is expected
