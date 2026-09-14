"""Immutable domain records. No crypto key or certificate bytes are represented."""

from dataclasses import dataclass
from typing import Literal

Knowledge = Literal["verified", "inferred", "declared_by_vendor", "conflicting", "unknown", "stale"]
Band = Literal["urgent", "high", "planned", "verify"]


@dataclass(frozen=True)
class Organization:
    id: str
    name: str
    synthetic: bool = True


@dataclass(frozen=True)
class Asset:
    id: str
    tenant_id: str
    service: str
    kind: str
    owner_id: str
    data_lifetime_years: int
    business_criticality: int
    external_exposure: bool
    vendor_dependency: bool
    migration_lead_months: int
    blast_radius: int
    synthetic: bool = True


@dataclass(frozen=True)
class Evidence:
    id: str
    tenant_id: str
    asset_id: str
    source_type: str
    source_id: str
    observed_at: str
    scope: str
    parser_version: str
    sha256: str
    confidence: float
    knowledge: Knowledge
    algorithm: str
    function: str
    note: str = ""
    synthetic: bool = True


@dataclass(frozen=True)
class Finding:
    id: str
    tenant_id: str
    asset_id: str
    evidence_ids: tuple[str, ...]
    knowledge: Knowledge
    band: Band
    factors: tuple[str, ...]
    uncertainty: tuple[str, ...]
    recommendation: str
    owner_id: str
    confidence: float
    engine_version: str = "pqc-risk.v1"


@dataclass(frozen=True)
class MigrationAction:
    id: str
    tenant_id: str
    finding_id: str
    owner_id: str
    phase: str
    due_window: str
    acceptance_evidence: str
    blocker: str | None = None
