"""Reproducible, fictional evaluation organizations. No network calls."""

import hashlib
import json
from dataclasses import dataclass

from pqc_product.domain import Asset, Evidence, Knowledge, Organization

SIZES = (
    ("northstar", "Northstar Bank", 45, 10),
    ("aster", "Aster Health", 38, 9),
    ("harbor", "Harbor Industrial", 42, 9),
)
SOURCE_TYPES = ("cbom", "cyclonedx", "tls_csv", "sarif", "kms_json", "vendor_csv", "manual")


@dataclass(frozen=True)
class Corpus:
    organizations: tuple[Organization, ...]
    assets: tuple[Asset, ...]
    evidence: tuple[Evidence, ...]
    dependencies: tuple[tuple[str, str], ...]
    owner_ids: tuple[str, ...]
    gold_finding_asset_ids: tuple[str, ...]


def _hash(value: dict[str, object]) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def build_corpus() -> Corpus:
    organizations: list[Organization] = []
    assets: list[Asset] = []
    evidence: list[Evidence] = []
    dependencies: list[tuple[str, str]] = []
    owners: list[str] = []
    gold: list[str] = []
    for tenant_id, name, count, owner_count in SIZES:
        organizations.append(Organization(tenant_id, name))
        tenant_owners = tuple(f"{tenant_id}-owner-{i:02}" for i in range(owner_count))
        owners.extend(tenant_owners)
        for i in range(count):
            asset_id = f"{tenant_id}-asset-{i:03}"
            asset = Asset(
                id=asset_id,
                tenant_id=tenant_id,
                service=f"{name} synthetic service {i // 5:02}",
                kind=("application", "pki", "device", "vendor", "gateway")[i % 5],
                owner_id=tenant_owners[i % owner_count],
                data_lifetime_years=(1, 5, 10, 20)[i % 4],
                business_criticality=1 + i % 5,
                external_exposure=i % 3 == 0,
                vendor_dependency=i % 5 in (2, 3),
                migration_lead_months=(3, 6, 12, 24)[i % 4],
                blast_radius=1 + i % 5,
            )
            assets.append(asset)
            if i < 10:
                gold.append(asset_id)
            if i < (12 if tenant_id != "aster" else 11) and i + 1 < count:
                dependencies.append((asset_id, f"{tenant_id}-asset-{i + 1:03}"))
            observations = 2 if len(assets) <= 95 else 1
            for j in range(observations):
                knowledge: Knowledge
                if i < 10:
                    algorithm, knowledge = "RSA-2048", "verified"
                elif i % 17 == 12:
                    algorithm, knowledge = ("ECDSA-P256", "verified") if j == 0 else ("ML-DSA", "conflicting")
                elif i % 17 == 13:
                    algorithm, knowledge = "unidentified", "unknown"
                else:
                    algorithm, knowledge = "AES-256-GCM", "verified"
                source_type = SOURCE_TYPES[(i + j) % len(SOURCE_TYPES)]
                raw: dict[str, object] = {
                    "asset_id": asset_id,
                    "source_type": source_type,
                    "algorithm": algorithm,
                    "function": "key_exchange" if i % 2 == 0 else "signature",
                    "observation": j,
                }
                evidence.append(
                    Evidence(
                        id=f"{asset_id}-ev-{j}",
                        tenant_id=tenant_id,
                        asset_id=asset_id,
                        source_type=source_type,
                        source_id=f"synthetic/{source_type}/{asset_id}/{j}",
                        observed_at="2026-09-01T00:00:00Z",
                        scope="synthetic-lab",
                        parser_version="fixture-generator.v1",
                        sha256=_hash(raw),
                        confidence=0.95 if j == 0 else 0.7,
                        knowledge=knowledge,
                        algorithm=algorithm,
                        function=str(raw["function"]),
                        note="fictional observation; no real cryptographic material",
                    )
                )
    assert len(assets) == 125 and len(evidence) == 220 and len(dependencies) == 35
    assert len(owners) == 28 and len(gold) == 30
    return Corpus(tuple(organizations), tuple(assets), tuple(evidence), tuple(dependencies), tuple(owners), tuple(gold))
