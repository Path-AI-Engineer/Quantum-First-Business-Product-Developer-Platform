"""Explicit job transitions and optimistic version checks."""

from quantum_platform.models import TERMINAL_STATES, JobState

TRANSITIONS: dict[JobState, set[JobState]] = {
    JobState.ACCEPTED: {JobState.VALIDATING},
    JobState.VALIDATING: {JobState.REJECTED, JobState.QUEUED},
    JobState.QUEUED: {JobState.DISPATCHING, JobState.CANCELLED, JobState.EXPIRED},
    JobState.DISPATCHING: {
        JobState.RUNNING,
        JobState.FAILED,
        JobState.UNKNOWN_RECONCILIATION_REQUIRED,
    },
    JobState.RUNNING: {
        JobState.SUCCEEDED,
        JobState.FAILED,
        JobState.CANCELLING,
        JobState.UNKNOWN_RECONCILIATION_REQUIRED,
    },
    JobState.CANCELLING: {JobState.CANCELLED, JobState.RUNNING},
    JobState.UNKNOWN_RECONCILIATION_REQUIRED: {
        JobState.RUNNING,
        JobState.SUCCEEDED,
        JobState.FAILED,
    },
}


def can_transition(current: JobState, target: JobState) -> bool:
    if current in TERMINAL_STATES:
        return False
    return target in TRANSITIONS.get(current, set())


def assert_transition(current: JobState, target: JobState) -> None:
    if not can_transition(current, target):
        raise ValueError(f"illegal transition: {current.value} -> {target.value}")
