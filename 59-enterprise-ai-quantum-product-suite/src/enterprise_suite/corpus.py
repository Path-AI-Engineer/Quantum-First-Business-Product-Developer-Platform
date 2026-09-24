from __future__ import annotations

import hashlib
from typing import Any

from enterprise_suite.models import Evidence, Module, Principal, Recommendation, ResourceRef

TENANTS = (
    ("meridian", "Meridian Financial Group"),
    ("atlas", "Atlas Health Network"),
    ("northport", "Northport Manufacturing"),
)
ROLES = (
    "executive-sponsor",
    "crypto-lead",
    "operations-lead",
    "platform-lead",
    "optimization-scientist",
    "quantum-developer",
    "risk-reviewer",
    "procurement-finance",
    "auditor",
    "support-analyst",
)


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def build_corpus() -> dict[str, Any]:
    identities: list[Principal] = []
    units: list[dict[str, str]] = []
    evidence: list[Evidence] = []
    resources: list[ResourceRef] = []
    opportunities: list[dict[str, Any]] = []
    experiments: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    recommendations: list[Recommendation] = []
    for tenant_id, tenant_name in TENANTS:
        for index, role in enumerate(ROLES):
            identities.append(
                Principal(
                    identity_id=f"id-{tenant_id}-{index:02d}",
                    tenant_id=tenant_id,
                    role=role,
                    workspace_ids=(f"ws-{tenant_id}-core",),
                    service=role == "support-analyst",
                )
            )
        for index in range(5):
            units.append(
                {
                    "unit_id": f"bu-{tenant_id}-{index + 1}",
                    "tenant_id": tenant_id,
                    "name": f"{tenant_name} Unit {index + 1}",
                }
            )
        for index in range(60):
            module = tuple(Module)[index % 4]
            evidence_id = f"ev-{tenant_id}-{index:03d}"
            evidence.append(
                Evidence(
                    evidence_id=evidence_id,
                    tenant_id=tenant_id,
                    module=module,
                    title=f"Synthetic observation {index + 1} / Observacion sintetica",
                    source=f"synthetic://{tenant_id}/records/{index}",
                    sha256=_digest(f"{tenant_id}:{index}:synthetic-only"),
                    confidence=round(0.65 + (index % 30) / 100, 2),
                    correlation_id=f"corr-{tenant_id}-{index // 4:03d}",
                )
            )
            resources.append(
                ResourceRef(
                    resource_id=f"res-{tenant_id}-{index:03d}",
                    tenant_id=tenant_id,
                    workspace_id=f"ws-{tenant_id}-core",
                    module=module,
                    classification="restricted" if index % 7 == 0 else "internal",
                )
            )
        for index in range(4):
            opportunity_id = f"opt-{tenant_id}-{index + 1}"
            opportunities.append(
                {
                    "opportunity_id": opportunity_id,
                    "tenant_id": tenant_id,
                    "title": f"Synthetic optimization opportunity {index + 1}",
                    "estimated_value_hypothesis": 100_000 * (index + 1),
                    "actual_value": None,
                    "status": "assessment",
                }
            )
        for index in range(3):
            experiments.append(
                {
                    "template_id": f"exp-{tenant_id}-{index + 1}",
                    "tenant_id": tenant_id,
                    "capability": ("sampling", "optimization", "simulation")[index],
                    "execution": "sandbox-local-only",
                }
            )
        for index in range(12):
            decisions.append(
                {
                    "decision_id": f"dec-{tenant_id}-{index:02d}",
                    "tenant_id": tenant_id,
                    "module": tuple(Module)[index % 4],
                    "status": "synthetic-gold-scenario",
                    "outcome": ("invest", "hold", "kill")[index % 3],
                    "evidence_id": f"ev-{tenant_id}-{index:03d}",
                }
            )
        for index, module in enumerate(Module):
            recommendations.append(
                Recommendation(
                    recommendation_id=f"rec-{tenant_id}-{index + 1}",
                    tenant_id=tenant_id,
                    module=module,
                    summary=f"Review synthetic {module.value} candidate",
                    evidence_ids=(f"ev-{tenant_id}-{index:03d}",),
                    uncertainty="Evidence is synthetic and external validation is pending.",
                    decision_owner=f"id-{tenant_id}-00",
                )
            )
    return {
        "tenants": [{"tenant_id": key, "name": name, "synthetic": True} for key, name in TENANTS],
        "identities": identities,
        "business_units": units,
        "evidence": evidence,
        "resources": resources,
        "opportunities": opportunities,
        "experiments": experiments,
        "decisions": decisions,
        "recommendations": recommendations,
    }


def corpus_counts(corpus: dict[str, Any]) -> dict[str, int]:
    return {
        "tenants": len(corpus["tenants"]),
        "identities": len(corpus["identities"]),
        "business_units": len(corpus["business_units"]),
        "evidence": len(corpus["evidence"]),
        "opportunities": len(corpus["opportunities"]),
        "experiments": len(corpus["experiments"]),
        "decisions": len(corpus["decisions"]),
    }
