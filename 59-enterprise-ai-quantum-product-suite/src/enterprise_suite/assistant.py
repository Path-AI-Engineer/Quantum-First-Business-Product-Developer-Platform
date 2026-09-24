from __future__ import annotations

from enterprise_suite.models import AssistantRequest, AssistantResponse, Evidence

INJECTION_MARKERS = ("ignore previous", "system prompt", "reveal secret", "bypass policy")


def grounded_assistant(request: AssistantRequest, evidence: list[Evidence]) -> AssistantResponse:
    if any(marker in request.question.lower() for marker in INJECTION_MARKERS):
        return AssistantResponse(
            answer="Abstained: the request contains a synthetic prompt-injection marker.",
            citations=(),
            abstained=True,
        )
    selected = [item for item in evidence if item.tenant_id == request.tenant_id and item.evidence_id in request.evidence_ids]
    if not selected or len(selected) != len(request.evidence_ids):
        return AssistantResponse(
            answer="Abstained: tenant-scoped evidence is incomplete.",
            citations=tuple(item.evidence_id for item in selected),
            abstained=True,
        )
    titles = "; ".join(item.title for item in selected[:3])
    return AssistantResponse(
        answer=f"Deterministic evidence brief: {titles}. No operational action was taken.",
        citations=tuple(item.evidence_id for item in selected),
        abstained=False,
    )
