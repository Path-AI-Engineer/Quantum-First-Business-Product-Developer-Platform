import json
import shutil
from pathlib import Path
from zipfile import ZipFile

import pytest
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator
from typer.testing import CliRunner

from venture_evidence.api import app
from venture_evidence.cli import app as cli
from venture_evidence.reporting import export_handoff, export_schemas, verify_handoff
from venture_evidence.repository import ROOT, digest


@pytest.fixture
def research_root(tmp_path):
    for path in ("src", "data", "scripts"):
        shutil.copytree(ROOT / path, tmp_path / path, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy2(ROOT / "pyproject.toml", tmp_path / "pyproject.toml")
    return tmp_path


def test_deterministic_contract_and_zip(research_root):
    target = export_handoff(root=research_root)
    first = verify_handoff(root=research_root)
    export_schemas(research_root)
    export_handoff(root=research_root)
    assert first == verify_handoff(root=research_root)
    assert first["approval"] == "pending_human_review"
    assert first["files"] == 10
    with ZipFile(target.with_suffix(".zip")) as archive:
        assert len(archive.namelist()) == 11
        assert all(not Path(name).is_absolute() and ".." not in name for name in archive.namelist())
    for path in (research_root / "contracts/schemas").glob("*.json"):
        Draft202012Validator.check_schema(json.loads(path.read_text()))


@pytest.mark.parametrize("mutation", ["payload", "source", "approval", "extra", "zip"])
def test_handoff_tampering_is_detected(research_root, mutation):
    target = export_handoff(root=research_root)
    if mutation == "payload":
        (target / "company-thesis.md").write_text("Rewritten evidence")
    elif mutation == "source":
        with (research_root / "src/venture_evidence/scoring.py").open("a") as stream:
            stream.write("\n# changed\n")
    elif mutation == "approval":
        path = target / "manifest.json"
        data = json.loads(path.read_text())
        data["approval"] = "approved"
        path.write_text(json.dumps(data))
    elif mutation == "extra":
        (target / "unexpected.txt").write_text("Not part of contract")
    else:
        with ZipFile(target.with_suffix(".zip"), "a") as archive:
            archive.writestr("../outside.txt", "bad")
    with pytest.raises(ValueError):
        verify_handoff(root=research_root)


@pytest.mark.parametrize("version", ["../outside", "company-vision-v0", "company-vision-v1/../../", "v1"])
def test_version_path_traversal_is_forbidden(version, research_root):
    with pytest.raises(ValueError):
        export_handoff(version, research_root)


def test_api_real_data_scenarios_invalid_inputs_and_read_only():
    client = TestClient(app)
    before = digest(ROOT / "data/evidence/corpus.v1.json")
    assert client.get("/health").json()["mode"] == "local-read-only"
    room = client.get("/api/room").json()
    assert room["audit"]["evidence"] == 32
    low = client.get("/api/score?scenario=conservative").json()["scores"][0]["estimate"]
    high = client.get("/api/score?scenario=aggressive").json()["scores"][0]["estimate"]
    assert high > low
    for query in ("scenario=bad", "dimension=missing", "multiplier=0", "multiplier=nan"):
        assert client.get("/api/score?" + query).status_code == 422
    for query in ("annual_price=-1", "annual_price=nan", "organizations=-10"):
        assert client.get("/api/economics?" + query).status_code == 422
    assert client.get("/api/economics?annual_price=12000").json()["delivery_cost_per_customer"] == 5300
    assert client.post("/api/room", json={}).status_code == 405
    assert client.get("/health", headers={"host": "external.example"}).status_code == 400
    assert "pending" in client.get("/api/thesis").text
    assert client.get("/docs").status_code == 200
    assert before == digest(ROOT / "data/evidence/corpus.v1.json")


@pytest.mark.parametrize(
    "command",
    [
        ["evidence", "validate"],
        ["evidence", "lint"],
        ["opportunity", "score", "--scenario", "conservative"],
        ["opportunity", "score", "--scenario", "base"],
        ["opportunity", "score", "--scenario", "aggressive"],
        ["opportunity", "sensitivity"],
    ],
)
def test_cli_contract(command):
    result = CliRunner().invoke(cli, command)
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)


def test_cli_rejects_unsupported_scenario():
    assert CliRunner().invoke(cli, ["opportunity", "score", "--scenario", "optimistic"]).exit_code != 0
