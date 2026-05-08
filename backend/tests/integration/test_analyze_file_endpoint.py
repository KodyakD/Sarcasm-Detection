from __future__ import annotations

from fastapi.testclient import TestClient

from main import app


def test_analyze_file_txt_success() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/analyze-file",
            files={"file": ("sample.txt", b"yeah right this is perfect", "text/plain")},
        )
    assert response.status_code == 200
    body = response.json()
    assert "extracted_text" in body
    assert "is_sarcastic" in body


def test_analyze_file_invalid_extension() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/analyze-file",
            files={"file": ("sample.doc", b"content", "application/msword")},
        )
    assert response.status_code == 400
