from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
METRICS_PATH = ROOT / "notebooks" / "metrics.json"
REQUIRED_KEYS = {"accuracy", "precision", "recall", "f1"}


def main() -> int:
    if not METRICS_PATH.exists():
        print(f"Missing metrics file: {METRICS_PATH}")
        return 1

    data = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    missing = REQUIRED_KEYS - set(data.keys())
    if missing:
        print("Missing metric keys:", ", ".join(sorted(missing)))
        return 1

    for key in REQUIRED_KEYS:
        value = data[key]
        if not isinstance(value, (int, float)):
            print(f"Metric {key} must be numeric, got {type(value).__name__}")
            return 1
        if not 0.0 <= float(value) <= 1.0:
            print(f"Metric {key} out of [0,1] range: {value}")
            return 1

    print("Metrics validation passed")
    for key in sorted(REQUIRED_KEYS):
        print(f"- {key}: {data[key]:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
