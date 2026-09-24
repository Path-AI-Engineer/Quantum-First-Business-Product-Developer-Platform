from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

EVENT_TYPES = (
    "EvidenceRecorded",
    "RiskChanged",
    "RecommendationCreated",
    "ApprovalRequested",
    "ApprovalGranted",
    "ApprovalDenied",
    "ApprovalExpired",
    "MigrationWaveProposed",
    "BenchmarkCompleted",
    "QuantumJobCompleted",
    "QuotaThresholdReached",
    "DecisionRecorded",
    "ReportPublished",
)


class Outbox:
    def __init__(self) -> None:
        self._events: list[dict[str, Any]] = []
        self._seen: set[str] = set()

    def publish(self, event_type: str, tenant_id: str, subject: str, correlation_id: str) -> dict[str, Any]:
        if event_type not in EVENT_TYPES:
            raise ValueError("unsupported event type")
        event = {
            "specversion": "1.0",
            "id": str(uuid4()),
            "source": "/enterprise-suite/reference",
            "type": f"com.decodelabs.enterprise.{event_type}.v1",
            "subject": subject,
            "time": datetime.now(UTC).isoformat(),
            "tenantid": tenant_id,
            "correlationid": correlation_id,
        }
        self._events.append(event)
        return event

    def consume(self, event: dict[str, Any]) -> bool:
        event_id = str(event["id"])
        if event_id in self._seen:
            return False
        self._seen.add(event_id)
        return True

    @property
    def events(self) -> tuple[dict[str, Any], ...]:
        return tuple(self._events)
