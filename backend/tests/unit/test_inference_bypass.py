from __future__ import annotations

from inference import predict


def test_predict_bypass_for_short_text() -> None:
    result = predict("ok", "english")
    assert result["is_sarcastic"] is False
    assert result["confidence"] == 0.51


def test_predict_bypass_for_emoji_only() -> None:
    result = predict("😂😂😂", "arabic")
    assert result["is_sarcastic"] is False
    assert result["confidence"] == 0.51
