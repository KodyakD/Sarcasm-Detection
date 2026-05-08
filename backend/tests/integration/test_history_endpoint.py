from __future__ import annotations

from fastapi.testclient import TestClient

from main import app


def test_history_returns_recent_items() -> None:
    with TestClient(app) as client:
        client.post("/analyze", json={"text": "yeah right this is perfect"})
        client.post("/analyze", json={"text": "normal sentence without sarcasm"})

        response = client.get("/history")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) >= 2
    assert "timestamp" in body[0]
