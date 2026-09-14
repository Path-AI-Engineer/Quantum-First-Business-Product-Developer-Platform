"""Deterministic reconciled reports; no implied security certification."""

import hashlib
import json
from collections import Counter
from typing import Any

from pqc_product.domain import Asset, Evidence, Finding, MigrationAction
from pqc_product.engine import evaluate

REPORT_TYPES = frozenset({"executive", "technical", "exposure", "migration", "conflicts", "vendor", "delta"})


def build_report(
    tenant_id: str,
    report_type: str,
    assets: tuple[Asset, ...],
    evidence: tuple[Evidence, ...],
    findings: tuple[Finding, ...],
    actions: tuple[MigrationAction, ...],
    baseline_evidence: tuple[Evidence, ...] | None = None,
) -> dict[str, Any]:
    if report_type not in REPORT_TYPES:
        raise ValueError("unsupported report type")
    asset_ids = {a.id for a in assets}
    if (
        any(a.tenant_id != tenant_id for a in assets)
        or any(e.tenant_id != tenant_id for e in evidence)
        or any(f.tenant_id != tenant_id for f in findings)
        or any(a.tenant_id != tenant_id for a in actions)
    ):
        raise ValueError("cross-tenant report input")
    if any(f.asset_id not in asset_ids or not f.evidence_ids for f in findings):
        raise ValueError("untraceable finding")
    if baseline_evidence is not None and any(
        e.tenant_id != tenant_id or e.asset_id not in asset_ids for e in baseline_evidence
    ):
        raise ValueError("cross-tenant report baseline")
    bands = dict(sorted(Counter(f.band for f in findings).items()))
    states = dict(sorted(Counter(f.knowledge for f in findings).items()))
    summary: dict[str, Any] = {
        "tenant_id": tenant_id,
        "type": report_type,
        "synthetic": True,
        "engine_version": "pqc-risk.v1",
        "asset_count": len(assets),
        "observation_count": len(evidence),
        "finding_count": len(findings),
        "action_count": len(actions),
        "by_band": bands,
        "by_knowledge": states,
        "caveat": "Synthetic offline assessment; not a quantum-safe certification or migration authorization.",
    }
    if report_type in {"technical", "conflicts"}:
        summary["findings"] = [
            {
                "id": f.id,
                "asset_id": f.asset_id,
                "evidence_ids": f.evidence_ids,
                "knowledge": f.knowledge,
                "band": f.band,
                "confidence": f.confidence,
                "uncertainty": f.uncertainty,
            }
            for f in findings
            if report_type == "technical" or f.knowledge in {"unknown", "conflicting"}
        ]
    elif report_type == "migration":
        summary["actions"] = [a.id for a in actions]
    elif report_type == "vendor":
        summary["vendor_dependent_assets"] = [a.id for a in assets if a.vendor_dependency]
    elif report_type == "exposure":
        summary["externally_exposed_assets"] = [a.id for a in assets if a.external_exposure]
    elif report_type == "delta":
        if baseline_evidence is None:
            summary["delta"] = "No baseline supplied; comparison unavailable"
        else:
            before = {f.id: f.band for f in evaluate(assets, baseline_evidence)}
            after = {f.id: f.band for f in findings}
            summary["delta"] = {
                "baseline_id": "synthetic-fixture-v1",
                "baseline_observations": len(baseline_evidence),
                "current_observations": len(evidence),
                "added_observations": len(evidence) - len(baseline_evidence),
                "changed_priority": sorted(fid for fid in before.keys() & after.keys() if before[fid] != after[fid]),
                "new_findings": sorted(after.keys() - before.keys()),
                "resolved_findings": sorted(before.keys() - after.keys()),
                "scope": "Evidence update only; not a migration outcome or approved improvement",
            }
    encoded = json.dumps(summary, sort_keys=True, separators=(",", ":")).encode()
    summary["sha256"] = hashlib.sha256(encoded).hexdigest()
    return summary
