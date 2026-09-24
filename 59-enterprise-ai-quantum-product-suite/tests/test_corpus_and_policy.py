from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from enterprise_suite.corpus import TENANTS, build_corpus, corpus_counts
from enterprise_suite.models import Approval, Principal
from enterprise_suite.policy import approval_valid, authorize


def test_corpus_exact_minimums() -> None:
    counts = corpus_counts(build_corpus())
    assert counts == {
        "tenants": 3,
        "identities": 30,
        "business_units": 15,
        "evidence": 180,
        "opportunities": 12,
        "experiments": 9,
        "decisions": 36,
    }


@pytest.mark.parametrize("tenant_id,_", TENANTS)
def test_synthetic_only_and_bilingual(tenant_id: str, _: str) -> None:
    corpus = build_corpus()
    tenant = next(item for item in corpus["tenants"] if item["tenant_id"] == tenant_id)
    evidence = [item for item in corpus["evidence"] if item.tenant_id == tenant_id]
    assert tenant["synthetic"] is True
    assert len(evidence) == 60
    assert all("Observacion sintetica" in item.title for item in evidence)


@pytest.mark.parametrize("index", range(240))
def test_authorization_matrix_has_no_cross_tenant_exposure(index: int) -> None:
    corpus = build_corpus()
    principal: Principal = corpus["identities"][index % 30]
    same_resource = next(resource for resource in corpus["resources"] if resource.tenant_id == principal.tenant_id)
    other_resource = next(resource for resource in corpus["resources"] if resource.tenant_id != principal.tenant_id)
    cross_allowed, reason = authorize(principal, "can_view", other_resource)
    assert cross_allowed is False
    assert reason == "TENANT_MISMATCH"
    same_allowed, same_reason = authorize(principal, "can_view", same_resource)
    assert isinstance(same_allowed, bool)
    assert same_reason in {"ALLOW_POLICY_V1", "CLASSIFICATION_DENIED"}


def test_deny_by_default_and_service_restriction() -> None:
    corpus = build_corpus()
    resource = corpus["resources"][1]
    unknown = Principal(identity_id="unknown", tenant_id=resource.tenant_id, role="unknown", workspace_ids=(resource.workspace_id,))
    assert authorize(unknown, "can_view", resource) == (False, "DENY_BY_DEFAULT")
    service = Principal(
        identity_id="svc",
        tenant_id=resource.tenant_id,
        role="support-analyst",
        workspace_ids=(resource.workspace_id,),
        service=True,
    )
    assert authorize(service, "can_export", resource)[1] == "SERVICE_IDENTITY_RESTRICTED"


@pytest.mark.parametrize(
    "change,reason",
    [
        ({"tenant_id": "atlas"}, "TENANT_MISMATCH"),
        ({"status": "consumed"}, "APPROVAL_NOT_GRANTED"),
        ({"expires_at": datetime.now(UTC) - timedelta(seconds=1)}, "APPROVAL_EXPIRED"),
        ({"resource_revision": 2}, "APPROVAL_REVISION_MISMATCH"),
        ({"scope": "export"}, "APPROVAL_SCOPE_MISMATCH"),
        ({"budget_limit": 5}, "APPROVAL_BUDGET_EXCEEDED"),
    ],
)
def test_approval_binding_rejects_replay(change: dict[str, object], reason: str) -> None:
    base = Approval(
        approval_id="approval-1",
        tenant_id="meridian",
        requester_id="user-1",
        resource_id="local-simulator",
        resource_revision=1,
        scope="sandbox-job",
        budget_limit=100,
        expires_at=datetime.now(UTC) + timedelta(hours=1),
        status="granted",
    )
    approval = base.model_copy(update=change)
    valid, actual = approval_valid(
        approval,
        tenant_id="meridian",
        resource_id="local-simulator",
        revision=1,
        scope="sandbox-job",
        budget=10,
    )
    assert valid is False
    assert actual == reason


def test_valid_approval() -> None:
    approval = Approval(
        approval_id="a",
        tenant_id="meridian",
        requester_id="u",
        resource_id="r",
        resource_revision=1,
        scope="sandbox-job",
        budget_limit=100,
        expires_at=datetime.now(UTC) + timedelta(hours=1),
        status="granted",
    )
    assert approval_valid(
        approval,
        tenant_id="meridian",
        resource_id="r",
        revision=1,
        scope="sandbox-job",
        budget=99,
    ) == (True, "APPROVAL_VALID")
