import json
from dataclasses import replace
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from pqc_product.api import create_app
from pqc_product.corpus import build_corpus
from pqc_product.domain import Evidence
from pqc_product.engine import evaluate, migration_actions
from pqc_product.ingestion import ImportRejected, parse_import
from pqc_product.reporting import build_report
from pqc_product.security import IDENTITIES, allowed


def test_corpus_contract() -> None:
    corpus = build_corpus()
    assert [(o.id, sum(a.tenant_id == o.id for a in corpus.assets)) for o in corpus.organizations] == [
        ("northstar", 45),
        ("aster", 38),
        ("harbor", 42),
    ]
    assert (len(corpus.assets), len(corpus.evidence), len(corpus.dependencies), len(corpus.owner_ids)) == (
        125,
        220,
        35,
        28,
    )
    assert len(corpus.gold_finding_asset_ids) == 30
    assert all(a.synthetic for a in corpus.assets)
    findings = evaluate(corpus.assets, corpus.evidence)
    assert set(corpus.gold_finding_asset_ids) <= {f.asset_id for f in findings}
    assert all(f.evidence_ids and f.tenant_id for f in findings)
    assert all(f.band == "verify" for f in findings if f.knowledge in {"unknown", "conflicting"})


@pytest.mark.parametrize("identity_id", sorted(IDENTITIES))
@pytest.mark.parametrize("case", range(6))
def test_72_authorization_cases(identity_id: str, case: int) -> None:
    identity = IDENTITIES[identity_id]
    other = next(t for t in ("northstar", "aster", "harbor") if t != identity.tenant_id)
    expectations = (
        (identity.tenant_id, "read", True),
        (other, "read", False),
        (identity.tenant_id, "import", identity.role in {"owner", "architect"}),
        (identity.tenant_id, "decide", identity.role in {"owner", "architect"}),
        (other, "wave", False),
        (identity.tenant_id, "export", True),
    )
    tenant, action, expected = expectations[case]
    assert allowed(identity, tenant, action) is expected


@pytest.mark.parametrize("case", range(45))
def test_45_rejected_imports_fail_closed(case: int) -> None:
    asset_id = "northstar-asset-000"
    source = "cbom"
    if case < 6:
        payload = [b"", b"not-json", b"[]", b"{}", b'{"observations":[]}', b"x" * 64_001][case]
    elif case < 16:
        payload = json.dumps(
            {"observations": [{"asset_id": f"aster-asset-{case - 6:03}", "algorithm": "RSA-2048"}]}
        ).encode()
    elif case < 26:
        forbidden = [
            "private_key",
            "privateKey",
            "secret",
            "password",
            "access_token",
            "certificate_pem",
            "key_material",
            "SECRET",
            "Password",
            "key-material",
        ][case - 16]
        payload = json.dumps(
            {"observations": [{"asset_id": asset_id, "algorithm": "RSA-2048", forbidden: f"synthetic-rejected-{case}"}]}
        ).encode()
    elif case < 36:
        invalid = [None, 17, [], {}, "", " " * 2, "X" * 81, False, 1.2, ["RSA-2048"]][case - 26]
        payload = json.dumps({"observations": [{"asset_id": asset_id, "algorithm": invalid}]}).encode()
    else:
        source = f"active_scan_{case}"
        payload = json.dumps({"observations": [{"asset_id": asset_id, "algorithm": "RSA-2048"}]}).encode()
    with pytest.raises(ImportRejected):
        parse_import("northstar", source, payload, frozenset({asset_id}))


def test_import_is_atomic_and_detects_conflict() -> None:
    payload = {
        "observations": [
            {"asset_id": "northstar-asset-011", "algorithm": "RSA-2048"},
            {"asset_id": "aster-asset-000", "algorithm": "ECDSA-P256"},
        ]
    }
    with pytest.raises(ImportRejected):
        parse_import("northstar", "cbom", json.dumps(payload).encode(), frozenset({"northstar-asset-011"}))
    payload["observations"].pop()
    items = parse_import("northstar", "cbom", json.dumps(payload).encode(), frozenset({"northstar-asset-011"}))
    assert len(items) == 1 and len(items[0].sha256) == 64


@pytest.mark.parametrize(
    "source_type,filename",
    [
        ("cbom", "cbom.json"),
        ("cyclonedx", "cyclonedx.json"),
        ("tls_csv", "tls.csv"),
        ("sarif", "sarif.json"),
        ("kms_json", "kms.json"),
        ("vendor_csv", "vendor.csv"),
        ("manual", "manual.json"),
    ],
)
def test_all_offline_connectors(source_type: str, filename: str) -> None:
    payload = (Path(__file__).resolve().parents[1] / "data" / "fixtures" / filename).read_bytes()
    known = frozenset(f"northstar-asset-{i:03}" for i in range(45))
    items = parse_import("northstar", source_type, payload, known)
    assert len(items) == 1
    assert items[0].source_type == source_type and items[0].tenant_id == "northstar"


@pytest.mark.parametrize("case", range(24))
def test_24_pairwise_priority_orderings(case: int) -> None:
    corpus = build_corpus()
    base = corpus.assets[0]
    variant = case // 3
    urgent = replace(
        base,
        id="pair-urgent",
        data_lifetime_years=20,
        business_criticality=5,
        external_exposure=True,
        vendor_dependency=variant % 2 == 0,
    )
    high = replace(
        base,
        id="pair-high",
        data_lifetime_years=10 if variant % 3 == 0 else 1,
        business_criticality=4 if variant % 3 == 1 else 1,
        external_exposure=variant % 3 == 2,
    )
    planned = replace(
        base,
        id="pair-planned",
        data_lifetime_years=1,
        business_criticality=1,
        external_exposure=False,
        migration_lead_months=3,
    )
    assets = (urgent, high, planned)
    template = corpus.evidence[0]
    observations: tuple[Evidence, ...] = tuple(replace(template, id=f"e-{a.id}", asset_id=a.id) for a in assets)
    bands = {f.asset_id: f.band for f in evaluate(assets, observations)}
    left, right = (("pair-urgent", "pair-high"), ("pair-high", "pair-planned"), ("pair-urgent", "pair-planned"))[
        case % 3
    ]
    assert {"urgent": 3, "high": 2, "planned": 1}[bands[left]] > {"urgent": 3, "high": 2, "planned": 1}[bands[right]]


def test_vendor_and_lead_time_affect_priority_without_hiding_uncertainty() -> None:
    corpus = build_corpus()
    base = corpus.assets[0]
    plain = replace(
        base,
        id="plain",
        data_lifetime_years=1,
        business_criticality=1,
        external_exposure=False,
        vendor_dependency=False,
        migration_lead_months=3,
        blast_radius=1,
    )
    dependent = replace(plain, id="dependent", vendor_dependency=True, migration_lead_months=24)
    template = corpus.evidence[0]
    evidence = (
        replace(template, id="plain-e", asset_id="plain"),
        replace(template, id="dependent-e", asset_id="dependent"),
    )
    bands = {f.asset_id: f.band for f in evaluate((plain, dependent), evidence)}
    assert bands == {"plain": "planned", "dependent": "high"}
    stale = replace(evidence[0], knowledge="stale")
    [finding] = evaluate((plain,), (stale,))
    assert finding.band == "verify" and finding.knowledge == "stale"


@pytest.mark.parametrize("identity_id", sorted(IDENTITIES))
@pytest.mark.parametrize("case", range(6))
def test_72_api_authorization_cases(identity_id: str, case: int) -> None:
    client = TestClient(create_app())
    identity = IDENTITIES[identity_id]
    tenant = identity.tenant_id
    other = next(t for t in ("northstar", "aster", "harbor") if t != tenant)
    header = {"x-demo-identity": identity_id}
    if case == 0:
        assert client.get("/v1/assets", headers=header).status_code == 200
    elif case == 1:
        assert client.get(f"/v1/assets/{other}-asset-000", headers=header).status_code == 404
    elif case == 2:
        assert client.get(f"/v1/findings/finding-{other}-asset-000", headers=header).status_code == 404
    elif case == 3:
        foreign = client.post(
            "/v1/reports", json={"type": "executive"}, headers={"x-demo-identity": f"demo-{other}-owner"}
        ).json()["id"]
        assert client.get(f"/v1/reports/{foreign}", headers=header).status_code == 404
    elif case == 4:
        assessment = f"assessment-{tenant}-synthetic-v1"
        body = {
            "source_type": "cbom",
            "payload": {"observations": [{"asset_id": f"{tenant}-asset-000", "algorithm": "RSA-2048"}]},
        }
        status = client.post(f"/v1/assessments/{assessment}/imports", json=body, headers=header).status_code
        assert status == (200 if identity.role in {"owner", "architect"} else 403)
    else:
        body = {
            "name": "Synthetic test wave",
            "action_ids": [f"action-finding-{tenant}-asset-000"],
            "owner_id": f"{tenant}-owner-00",
            "acceptance_evidence": "Synthetic lab report",
        }
        status = client.post("/v1/migration-waves", json=body, headers=header).status_code
        assert status == (200 if identity.role in {"owner", "architect"} else 403)


def test_api_tenant_isolation_and_reports() -> None:
    client = TestClient(create_app())
    assert client.get("/v1/assets").status_code == 403
    north = {"x-demo-identity": "demo-northstar-owner"}
    aster = {"x-demo-identity": "demo-aster-owner"}
    assert len(client.get("/v1/assets", headers=north).json()) == 45
    assert len(client.get("/v1/assets", headers=aster).json()) == 38
    assert client.get("/v1/assets/aster-asset-000", headers=north).status_code == 404
    assessment = client.post("/v1/assessments", headers=north).json()["id"]
    before = len(client.get("/v1/observations", headers=north).json())
    invalid = {
        "source_type": "cbom",
        "payload": {
            "observations": [
                {"asset_id": "northstar-asset-000", "algorithm": "RSA-2048"},
                {"asset_id": "aster-asset-000", "algorithm": "RSA-2048"},
            ]
        },
    }
    assert client.post(f"/v1/assessments/{assessment}/imports", json=invalid, headers=north).status_code == 422
    assert len(client.get("/v1/observations", headers=north).json()) == before
    report = client.post("/v1/reports", json={"type": "executive"}, headers=north).json()
    assert report["asset_count"] == 45
    assert report["finding_count"] == sum(report["by_band"].values())
    assert client.get(f"/v1/reports/{report['id']}", headers=aster).status_code == 404
    assert client.get("/v1/audit", headers=north).json()


def test_delta_report_compares_evidence_snapshots_not_migration_success() -> None:
    client = TestClient(create_app())
    headers = {"x-demo-identity": "demo-northstar-owner"}
    before = client.post("/v1/reports", headers=headers, json={"type": "delta"}).json()
    assert before["delta"]["added_observations"] == 0
    assessment = client.post("/v1/assessments", headers=headers).json()["id"]
    imported = client.post(
        f"/v1/assessments/{assessment}/imports",
        headers=headers,
        json={
            "source_type": "cbom",
            "payload": {
                "observations": [{"asset_id": "northstar-asset-000", "algorithm": "ML-KEM", "knowledge": "inferred"}]
            },
        },
    )
    assert imported.status_code == 200 and imported.json()["accepted"] == 1
    after = client.post("/v1/reports", headers=headers, json={"type": "delta"}).json()
    assert after["delta"]["added_observations"] == 1
    assert "finding-northstar-asset-000" in after["delta"]["changed_priority"]
    assert "not a migration outcome" in after["delta"]["scope"]


@pytest.mark.parametrize("report_index", range(18))
def test_18_report_reconciliations(report_index: int) -> None:
    corpus = build_corpus()
    tenant = ("northstar", "aster", "harbor")[report_index % 3]
    report_type = ("executive", "technical", "exposure", "migration", "conflicts", "vendor")[report_index // 3]
    assets = tuple(a for a in corpus.assets if a.tenant_id == tenant)
    evidence = tuple(e for e in corpus.evidence if e.tenant_id == tenant)
    findings = evaluate(assets, evidence)
    actions = migration_actions(findings)
    report = build_report(tenant, report_type, assets, evidence, findings, actions)
    assert report["asset_count"] == len(assets)
    assert report["observation_count"] == len(evidence)
    assert report["finding_count"] == sum(report["by_band"].values())
    assert report == build_report(tenant, report_type, assets, evidence, findings, actions)


def test_no_migration_execution_endpoint() -> None:
    paths = create_app().openapi()["paths"]
    assert not any("/execute" in path or "/rotate" in path or "/scan" in path for path in paths)
