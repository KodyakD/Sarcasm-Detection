from __future__ import annotations

import time

from fastapi.testclient import TestClient

from main import app


def test_startup_time_under_10_seconds() -> None:
    started = time.perf_counter()
    with TestClient(app):
        elapsed = time.perf_counter() - started
    assert elapsed < 10.0
