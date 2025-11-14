from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

def test_add_and_export():
    payload = {
        "round_id": 9999,
        "attacker_action": "test_attack",
        "defender_action": "test_defend",
        "outcome": "failure",
        "reward": -1.0,
        "metadata": {"note": "unit test"}
    }

    post = client.post("/train/data", json=payload)
    assert post.status_code == 201, post.text

    r = client.get("/train/data/export?limit=10")
    assert r.status_code == 200
    assert "training_data.csv" in r.headers.get("Content-Disposition", "")
