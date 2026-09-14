"""Explainable priority bands and human-owned migration actions."""

from collections import defaultdict

from pqc_product.domain import Asset, Band, Evidence, Finding, Knowledge, MigrationAction

LEGACY = frozenset({"RSA-2048", "ECDSA-P256", "ECDH-P256", "DH-2048"})
PHASES = ("discover", "verify", "plan", "lab-test", "stage", "migrate", "validate", "monitor")


def evaluate(assets: tuple[Asset, ...], evidence: tuple[Evidence, ...]) -> tuple[Finding, ...]:
    by_asset: dict[str, list[Evidence]] = defaultdict(list)
    for item in evidence:
        by_asset[item.asset_id].append(item)
    findings: list[Finding] = []
    for asset in assets:
        items = by_asset[asset.id]
        if not items:
            continue
        algorithms = {item.algorithm for item in items}
        states = {item.knowledge for item in items}
        conflicting = "conflicting" in states or len(algorithms) > 1
        unknown = "unknown" in states or "unidentified" in algorithms
        legacy = bool(algorithms & LEGACY)
        if not (conflicting or unknown or legacy):
            continue
        factors: list[str] = []
        uncertainty: list[str] = []
        knowledge: Knowledge
        band: Band
        if legacy:
            factors.append("observed public-key mechanism requiring migration review")
        if asset.data_lifetime_years >= 10:
            factors.append("long-lived protected data")
        if asset.external_exposure:
            factors.append("external exposure")
        if asset.business_criticality >= 4:
            factors.append("high business criticality")
        if asset.vendor_dependency:
            factors.append("vendor dependency")
        if asset.migration_lead_months >= 12:
            factors.append("long migration lead time")
        if asset.blast_radius >= 4:
            factors.append("large blast radius")
        if conflicting:
            knowledge, band = "conflicting", "verify"
            uncertainty.append("source observations disagree; reconcile before planning")
        elif unknown:
            knowledge, band = "unknown", "verify"
            uncertainty.append("mechanism not identified; never treat as safe")
        elif "stale" in states:
            knowledge, band = "stale", "verify"
            uncertainty.append("observation is stale; refresh evidence before planning")
        else:
            knowledge = "verified" if all(item.knowledge == "verified" for item in items) else "inferred"
            if max(item.confidence for item in items) < 0.6:
                band = "verify"
                uncertainty.append("no sufficiently confident observation")
            else:
                urgency = (
                    2 * (asset.data_lifetime_years >= 10)
                    + 2 * asset.external_exposure
                    + 2 * (asset.business_criticality >= 4)
                    + asset.vendor_dependency
                    + (asset.migration_lead_months >= 12)
                    + (asset.blast_radius >= 4)
                )
                band = "urgent" if urgency >= 6 else "high" if urgency >= 2 else "planned"
        recommendation = (
            "Verify evidence with asset owner" if band == "verify" else "Plan laboratory migration assessment"
        )
        findings.append(
            Finding(
                id=f"finding-{asset.id}",
                tenant_id=asset.tenant_id,
                asset_id=asset.id,
                evidence_ids=tuple(item.id for item in items),
                knowledge=knowledge,
                band=band,
                factors=tuple(factors),
                uncertainty=tuple(uncertainty),
                recommendation=recommendation,
                owner_id=asset.owner_id,
                confidence=min(item.confidence for item in items),
            )
        )
    return tuple(findings)


def migration_actions(findings: tuple[Finding, ...]) -> tuple[MigrationAction, ...]:
    return tuple(
        MigrationAction(
            id=f"action-{finding.id}",
            tenant_id=finding.tenant_id,
            finding_id=finding.id,
            owner_id=finding.owner_id,
            phase="verify" if finding.band == "verify" else "plan",
            due_window="owner-agreed; not auto-scheduled",
            acceptance_evidence="Owner-approved observation reconciliation or lab test report",
            blocker="Evidence conflict or unknown mechanism" if finding.band == "verify" else None,
        )
        for finding in findings
    )
