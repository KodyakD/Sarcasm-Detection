from __future__ import annotations

import statistics
import time

from fastapi.testclient import TestClient

from main import app


def test_analyze_median_latency_under_5_seconds() -> None:
    durations = []
    payload = {"text": "yeah right this is exactly what we needed today"}

    with TestClient(app) as client:
        for _ in range(10):
            started = time.perf_counter()
            response = client.post("/analyze", json=payload)
            durations.append(time.perf_counter() - started)
            assert response.status_code == 200

    median = statistics.median(durations)
    assert median < 5.0
