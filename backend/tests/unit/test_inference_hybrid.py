from __future__ import annotations

import torch
import torch.nn as nn

import inference


class _DummyTokenizer:
    def __call__(
        self, text: str, return_tensors: str, truncation: bool, max_length: int
    ):
        _ = (text, return_tensors, truncation, max_length)
        return {
            "input_ids": torch.tensor([[101, 102]]),
            "attention_mask": torch.tensor([[1, 1]]),
        }


class _DummyHybridModel(nn.Module):
    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        extra_features: torch.Tensor,
    ):
        _ = (input_ids, attention_mask)
        assert extra_features.shape == (1, 3)
        return torch.tensor([[0.2, 0.8]])


def test_is_hybrid_checkpoint_detects_artifacts(tmp_path) -> None:
    (tmp_path / "pytorch_model.bin").write_bytes(b"weights")
    (tmp_path / "tokenizer.json").write_text("{}", encoding="utf-8")
    (tmp_path / "tokenizer_config.json").write_text("{}", encoding="utf-8")

    assert inference._is_hybrid_checkpoint(tmp_path) is True

    (tmp_path / "config.json").write_text("{}", encoding="utf-8")
    assert inference._is_hybrid_checkpoint(tmp_path) is False


def test_predict_uses_hybrid_runtime(monkeypatch) -> None:
    monkeypatch.setattr(
        inference, "_extract_manual_features", lambda text: [1.0, 0.2, 1.0]
    )
    monkeypatch.setattr(inference._registry, "loaded", True)
    monkeypatch.setattr(inference._registry, "model_kind", "hybrid")
    monkeypatch.setattr(inference._registry, "tokenizer", _DummyTokenizer())
    monkeypatch.setattr(inference._registry, "model", _DummyHybridModel())

    result = inference.predict("this is definitely enough tokens", "arabic")

    assert result["is_sarcastic"] is True
    assert float(result["confidence"]) > 0.6
