from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

try:
    from .config import get_settings
    from .schemas import Language
except ImportError:  # pragma: no cover - supports top-level test imports
    from config import get_settings
    from schemas import Language


@dataclass
class ModelRegistry:
    loaded: bool = False
    model: AutoModelForSequenceClassification | None = None
    tokenizer: AutoTokenizer | None = None
    model_path: Path | None = None
    model_kind: str = ""
    threshold: float = 0.5
    threshold_path: Path | None = None


_registry = ModelRegistry(loaded=False)
_EMOJI_OR_SYMBOL_PATTERN = re.compile(r"^[\W_\d\s]+$", re.UNICODE)
_logger = logging.getLogger("sarcasm-api.inference")


def _resolve_model_path() -> Path | str:
    settings = get_settings()
    
    # Try marbert_sarcasm_model first (trained model)
    project_root = Path(__file__).resolve().parents[1]
    sarcasm_model_path = project_root / settings.marbert_sarcasm_model_dir
    if sarcasm_model_path.is_dir() and _is_hf_checkpoint(sarcasm_model_path):
        return sarcasm_model_path.resolve()
    
    configured = Path(settings.model_dir)
    if configured.is_dir() and _is_hf_checkpoint(configured):
        return configured

    bundled = (
        project_root / "sarcasm_model" / "kaggle" / "working" / "marbert_sarcasm_final"
    )
    if bundled.is_dir() and _is_hf_checkpoint(bundled):
        return bundled

    _logger.warning(
        "No local fine-tuned model checkpoint found. Falling back to base model: %s",
        settings.marbert_model_name
    )
    return settings.marbert_model_name


def _is_hf_checkpoint(path: Path) -> bool:
    return (path / "config.json").exists() and (
        (path / "model.safetensors").exists() or (path / "pytorch_model.bin").exists()
    )


def _normalize_arabic(text: str) -> str:
    if not isinstance(text, str) or not text.strip():
        return ""
    import emoji
    # Demojize emojis to Arabic text descriptions, as the models were trained with this feature.
    text = emoji.demojize(text, language="ar")
    text = re.sub(r':([^:\s]+):', lambda m: " " + m.group(1).replace("_", " ") + " ", text)
    
    # Simplified normalization to match marbert4/inference.py
    # - Here we focus on the regexes used in the model's production code.
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"@\w+", " ", text)
    text = re.sub(r"#(\w+)", lambda m: " " + m.group(1).replace("_", " ") + " ", text)
    text = re.sub(r"[إأآ]", "ا", text)
    text = re.sub(r"[ؐ-ًؚ-ٰٟۖ-ۜ۟-۪ۤۧۨ-ۭ]", "", text)  # Diacritics
    text = re.sub(r"ـ", "", text)  # Tatweel
    text = re.sub(r"(.)\1{2,}", r"\1\1", text) # Repeat characters
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _is_low_information_input(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return True
    if _EMOJI_OR_SYMBOL_PATTERN.match(stripped):
        return True
    if len([t for t in stripped.split() if t.strip()]) < 3:
        return True
    return False


def startup_load_models() -> None:
    model_path = _resolve_model_path()
    settings = get_settings()

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    model.eval()

    # Load threshold from JSON if available (only for local paths)
    threshold = 0.5
    threshold_path = None
    
    if isinstance(model_path, Path):
        threshold_path = model_path / "threshold.json"
        if threshold_path.exists():
            try:
                with open(threshold_path, "r") as f:
                    threshold_data = json.load(f)
                    threshold = float(threshold_data.get("threshold", 0.5))
            except (json.JSONDecodeError, ValueError, OSError) as exc:
                _logger.warning("Failed to load threshold from %s: %s", threshold_path, exc)
    else:
        _logger.info("Using remote model %s; using default threshold 0.5", model_path)

    _registry.model = model
    _registry.tokenizer = tokenizer
    _registry.model_path = model_path
    _registry.model_kind = "hf"
    _registry.threshold = threshold
    _registry.threshold_path = threshold_path
    _registry.loaded = True

    _logger.info(
        "Loaded sarcasm model from %s (max_length=%s, threshold=%.4f)",
        model_path,
        settings.model_max_length,
        threshold,
    )


def is_model_loaded() -> bool:
    return _registry.loaded


def get_model_runtime_kind() -> str:
    return _registry.model_kind


def predict(text: str, language: str) -> dict[str, object]:
    _logger.info("predict called — text length: %d, low_info: %s", len(text), _is_low_information_input(text))

    # Handle low-information inputs deterministically
    if _is_low_information_input(text):
        return {"is_sarcastic": False, "confidence": 0.0}

    if not is_model_loaded():
        raise RuntimeError("Models are not loaded")

    tokenizer = _registry.tokenizer
    model = _registry.model
    settings = get_settings()

    if tokenizer is None or model is None:
        raise RuntimeError("Model registry is inconsistent")

    # Normalize text before tokenizing
    normalized = _normalize_arabic(text)

    encoded = tokenizer(
        normalized,
        return_tensors="pt",
        truncation=True,
        max_length=settings.model_max_length,
        padding=True,
    )

    with torch.no_grad():
        logits = model(**encoded).logits
        probabilities = torch.softmax(logits, dim=-1)[0]

    confidence = float(probabilities[1].item())  # Confidence for sarcasm class
    is_sarcastic = confidence >= _registry.threshold
    _logger.info(
    "predict result — is_sarcastic: %s, confidence: %.4f, threshold: %.4f, class_0: %.4f, class_1: %.4f",
    is_sarcastic,
    confidence,
    _registry.threshold,
    float(probabilities[0].item()),
    float(probabilities[1].item()),
)

    return {"is_sarcastic": is_sarcastic, "confidence": confidence}


def get_threshold() -> float:
    return _registry.threshold


def set_threshold(new_threshold: float) -> dict[str, object]:
    if not 0.0 <= new_threshold <= 1.0:
        raise ValueError("Threshold must be between 0.0 and 1.0")

    _registry.threshold = new_threshold

    # Persist to JSON if path is available
    if _registry.threshold_path and _registry.threshold_path.exists():
        try:
            with open(_registry.threshold_path, "r") as f:
                threshold_data = json.load(f)
            threshold_data["threshold"] = new_threshold
            with open(_registry.threshold_path, "w") as f:
                json.dump(threshold_data, f, indent=2)
            _logger.info("Threshold updated to %.4f and persisted to %s", new_threshold, _registry.threshold_path)
        except (json.JSONDecodeError, OSError) as exc:
            _logger.error("Failed to persist threshold to %s: %s", _registry.threshold_path, exc)
            raise RuntimeError(f"Failed to save threshold: {exc}") from exc
    else:
        _logger.warning("Cannot persist threshold: path not available or does not exist")

    return {"threshold": _registry.threshold}
