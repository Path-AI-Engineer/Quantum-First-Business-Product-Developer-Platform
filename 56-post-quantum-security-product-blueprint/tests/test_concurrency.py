from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient

from pqc_product.api import create_app


def test_concurrent_reads_keep_audit_chain_ordered() -> None:
    app = create_app()
    client = TestClient(app)
    headers = {"x-demo-identity": "demo-northstar-owner"}
    with ThreadPoolExecutor(max_workers=8) as executor:
        responses = list(executor.map(lambda _: client.get("/v1/assets", headers=headers), range(24)))
    assert all(response.status_code == 200 for response in responses)
    events = app.state.lab.audit
    assert len(events) == 24
    assert [event["sequence"] for event in events] == list(range(1, 25))
    assert events[0]["previous_hash"] == "GENESIS"
    assert all(events[i]["previous_hash"] == events[i - 1]["hash"] for i in range(1, len(events)))
