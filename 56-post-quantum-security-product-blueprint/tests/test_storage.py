import hashlib
import json
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import inspect

from pqc_product.api import create_app
from pqc_product.object_store import ObjectStore
from pqc_product.storage import DatabaseStore

ROOT = Path(__file__).resolve().parents[1]
HEADER = {"x-demo-identity": "demo-northstar-owner"}


def test_alembic_upgrade_creates_expected_tables(tmp_path: Path) -> None:
    url = f"sqlite:///{(tmp_path / 'migration.db').as_posix()}"
    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT / "migrations"))
    config.set_main_option("sqlalchemy.url", url)
    command.upgrade(config, "head")
    db = DatabaseStore(url)
    assert {"evidence", "decisions", "waves", "reports", "audit_events", "alembic_version"} <= set(
        inspect(db.engine).get_table_names()
    )
    db.engine.dispose()


def test_metadata_and_audit_survive_api_restart() -> None:
    db = DatabaseStore("sqlite:///:memory:", initialize=True)
    client = TestClient(create_app(db=db))
    assessment = client.post("/v1/assessments", headers=HEADER).json()["id"]
    payload = json.loads((ROOT / "data" / "fixtures" / "cbom.json").read_text(encoding="utf-8"))
    response = client.post(
        f"/v1/assessments/{assessment}/imports", headers=HEADER, json={"source_type": "cbom", "payload": payload}
    )
    assert response.status_code == 200 and response.json()["accepted"] == 1
    finding_id = "finding-northstar-asset-000"
    decision = client.post(
        f"/v1/findings/{finding_id}/decisions",
        headers=HEADER,
        json={"decision": "confirm", "rationale": "Synthetic review confirmed evidence path"},
    )
    assert decision.status_code == 200
    wave = client.post(
        "/v1/migration-waves",
        headers=HEADER,
        json={
            "name": "Synthetic wave",
            "action_ids": [f"action-{finding_id}"],
            "owner_id": "northstar-owner-00",
            "acceptance_evidence": "Synthetic lab report",
        },
    )
    assert wave.status_code == 200
    report = client.post("/v1/reports", headers=HEADER, json={"type": "executive"}).json()
    audit_before = client.get("/v1/audit", headers=HEADER).json()
    previous = "GENESIS"
    for event in audit_before:
        assert event["previous_hash"] == previous
        original = {key: value for key, value in event.items() if key != "hash"}
        assert event["hash"] == hashlib.sha256(json.dumps(original, sort_keys=True).encode()).hexdigest()
        previous = event["hash"]
    restarted = TestClient(create_app(db=db))
    assert len(restarted.get("/v1/observations", headers=HEADER).json()) == 91
    assert restarted.get(f"/v1/reports/{report['id']}", headers=HEADER).status_code == 200
    assert restarted.app.state.lab.decisions[finding_id]["decision"] == "confirm"
    assert wave.json()["id"] in restarted.app.state.lab.waves
    assert len(restarted.get("/v1/audit", headers=HEADER).json()) >= len(audit_before)
    db.engine.dispose()


def test_generated_report_object_is_content_addressed(tmp_path: Path) -> None:
    objects = ObjectStore(tmp_path / "objects")
    client = TestClient(create_app(objects=objects))
    report = client.post("/v1/reports", headers=HEADER, json={"type": "executive"}).json()
    stored = objects.read_report(report["object_sha256"])
    assert stored["sha256"] == report["sha256"] and stored["synthetic"] is True
    assert len(list((tmp_path / "objects").glob("*.json"))) == 1
