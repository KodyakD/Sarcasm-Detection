from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
EXPECTED_FILES = [DATA_DIR / "train.csv", DATA_DIR / "val.csv", DATA_DIR / "test.csv"]
EXPECTED_COLUMNS = ["text", "label", "language", "source"]
EXPECTED_TOTAL_RATIO = {"train.csv": 0.8, "val.csv": 0.1, "test.csv": 0.1}
ALLOWED_LANGUAGES = {"arabic", "darija", "french", "english", "unknown"}
ALLOWED_LABELS = {"0", "1"}


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != EXPECTED_COLUMNS:
            raise ValueError(
                f"{path.name}: invalid columns {reader.fieldnames}, expected {EXPECTED_COLUMNS}"
            )
        rows = list(reader)
    return rows


def main() -> int:
    missing = [p for p in EXPECTED_FILES if not p.exists()]
    if missing:
        print("Missing files:", ", ".join(p.name for p in missing))
        return 1

    splits: dict[str, list[dict[str, str]]] = {}
    for file_path in EXPECTED_FILES:
        rows = _read_rows(file_path)
        if not rows:
            print(f"{file_path.name}: empty split")
            return 1
        splits[file_path.name] = rows

    for split_name, rows in splits.items():
        for idx, row in enumerate(rows, start=1):
            text = row["text"].strip()
            if not text:
                print(f"{split_name} row {idx}: empty text")
                return 1
            if row["label"] not in ALLOWED_LABELS:
                print(f"{split_name} row {idx}: invalid label {row['label']}")
                return 1
            if row["language"] not in ALLOWED_LANGUAGES:
                print(f"{split_name} row {idx}: invalid language {row['language']}")
                return 1
            if not row["source"].strip():
                print(f"{split_name} row {idx}: empty source")
                return 1

    total = sum(len(rows) for rows in splits.values())
    for split_name, rows in splits.items():
        ratio = len(rows) / total
        expected = EXPECTED_TOTAL_RATIO[split_name]
        if abs(ratio - expected) > 0.2:
            print(f"{split_name}: ratio {ratio:.3f} too far from target {expected:.3f}")
            return 1

    print("Data pipeline validation passed")
    for split_name, rows in splits.items():
        print(f"- {split_name}: {len(rows)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
