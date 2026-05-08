import json
import re
from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

RANDOM_STATE = 42
ARABIC_RATIO_THRESHOLD = 0.30  # ← RELAXED from 0.45 to allow mixed-script sarcasm (brand names, loanwords)
TEST_SIZE = 0.10
VAL_SIZE = 0.10
TRAIN_SIZE = 0.80
MAX_TRAIN_IMBALANCE_RATIO = 20.0  # ← CHANGED from 4.0 to prevent double-weighting with Focal Loss
# If Focal Loss handles imbalance, don't also undersample. Set high to disable undersampling.
MIN_DIALECT_FOR_STRAT = 25

ARABIC_RE = re.compile(r"[\u0600-\u06FF]")
LATIN_RE = re.compile(r"[A-Za-z]")
ARABIZI_RE = re.compile(r"\b(?:[2-9][a-zA-Z]+|[a-zA-Z]+[2-9])[a-zA-Z0-9]*\b")
WS_RE = re.compile(r"\s+")

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DATA_DIR = SCRIPT_DIR


SOURCE_FILES = {
    "arsarcasm_train": Path("raw/training_data.csv"),
    "arsarcasm_test": Path("raw/testing_data.csv"),
    "isemeval_ar_train": Path("raw/iSarcasmEval-main/train/train.Ar.csv"),
    "isemeval_ar_test_A": Path("raw/iSarcasmEval-main/test/task_A_Ar_test.csv"),
    "ar_sarcasm_hf_train": Path("raw/ar_sarcasm_hf_train.csv"),
    "training_generated": Path("raw/Training.csv"),
    # ← REMOVED "adarabic_cla_45000" (DIALECT classification, not sarcasm — labels are 0-5, not binary)
    # ← TODO: audit archive/data.csv to confirm it's sarcasm; if not, remove it too
    # "archive_comments": Path("archive/data.csv"),  # ← Commented out pending audit
}

EXCLUDED_ENGLISH_FILES = [
    "raw/iSarcasmEval-main/train/train.En.csv",
    "raw/iSarcasmEval-main/test/task_A_En_test.csv",
    "raw/iSarcasmEval-main/test/task_B_En_test.csv",
    "raw/iSarcasmEval-main/test/task_C_En_test.csv",
    "raw/iSarcasmEval-main/third-party annotations/english_task_a.csv",
    "raw/iSarcasmEval-main/third-party annotations/english_task_c.csv",
]


def infer_columns(df: pd.DataFrame):
    text_candidates = ["text", "tweet", "comment", "content", "body", "post", "review", "title"]
    text_col = next((col for col in text_candidates if col in df.columns), None)
    label_candidates = ["label", "sarcasm", "sarcastic", "sarcasm_label"]
    label_col = next((col for col in label_candidates if col in df.columns), None)
    return text_col, label_col


def normalize_text(text: str) -> str:
    text = "" if text is None else str(text)
    text = WS_RE.sub(" ", text).strip().lower()
    return text


def to_binary_label(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.astype(int)
    mapped = series.replace(
        {
            "True": 1,
            "False": 0,
            "true": 1,
            "false": 0,
            "sarcastic": 1,
            "non_sarcastic": 0,
            "not_sarcastic": 0,
            "ironic": 1,
            "not_ironic": 0,
            "yes": 1,
            "no": 0,
            "Yes": 1,
            "No": 0,
        }
    )
    return pd.to_numeric(mapped, errors="coerce")


def map_source_labels(source_name: str, series: pd.Series) -> pd.Series:
    if source_name == "adarabic_cla_45000":
        numeric = pd.to_numeric(series, errors="coerce")
        unique_labels = sorted({int(v) for v in numeric.dropna().unique()})
        if set(unique_labels).issubset({0, 1}):
            return numeric
        raise ValueError(
            "non-binary label set detected "
            f"({unique_labels}); this source needs an explicit sarcasm label mapping before it can be merged"
        )
    return to_binary_label(series)


def arabic_latin_ratio(text: str) -> tuple[float, int, int]:
    t = "" if text is None else str(text)
    arabic_chars = len(ARABIC_RE.findall(t))
    latin_chars = len(LATIN_RE.findall(t))
    denom = arabic_chars + latin_chars
    ratio = arabic_chars / denom if denom > 0 else 0.0
    return ratio, arabic_chars, latin_chars


def is_code_switched(text: str, ratio: float, arabic_chars: int, latin_chars: int) -> bool:
    """RELAXED: Allow mixed-script sarcasm (Arabic sarcasm commonly uses English loanwords, brand names).
    
    Arabic ratio filter is already upstream (ARABIC_RATIO_THRESHOLD).
    This function only checks for excessive Latin or Arabizi.
    """
    if arabic_chars == 0 or latin_chars == 0:
        return False
    latin_ratio = latin_chars / max(arabic_chars + latin_chars, 1)
    # ← CHANGED: 0.15 → 0.30 (allow English loanwords, brand names like iPhone, WhatsApp)
    if latin_ratio >= 0.30:
        return True
    # ← Arabizi check removed (Arabizi is extremely common in Darija/Maghrebi sarcasm)
    # The redundant ratio < 0.50 check removed (handled upstream by ARABIC_RATIO_THRESHOLD)
    return False


def source_to_dialect_label(raw_val) -> str:
    if pd.isna(raw_val):
        return "unknown"
    s = str(raw_val).strip().lower()

    # HF dataset encodes dialect as numeric-like strings in this workspace.
    mapping = {
        "0": "msa",
        "0.0": "msa",
        "1": "egypt",
        "1.0": "egypt",
        "2": "gulf",
        "2.0": "gulf",
        "3": "magreb",
        "3.0": "magreb",
        "4": "levant",
        "4.0": "levant",
        "nile": "egypt",
    }
    return mapping.get(s, s)


def resolve_data_path(path: Union[Path, str]) -> Path:
    rel_path = Path(path)
    return rel_path if rel_path.is_absolute() else PROJECT_DATA_DIR / rel_path


def load_all_sources() -> pd.DataFrame:
    parts = []
    skipped_sources = []
    for source_name, path_str in SOURCE_FILES.items():
        path = resolve_data_path(path_str)
        if not path.exists():
            skipped_sources.append((source_name, str(path), "missing file"))
            continue

        df = pd.read_csv(path)
        text_col, label_col = infer_columns(df)
        if text_col is None or label_col is None:
            skipped_sources.append((source_name, str(path), f"unsupported columns: {list(df.columns)}"))
            continue

        out = pd.DataFrame()
        out["text"] = df[text_col].fillna("").astype(str)
        try:
            out["label"] = map_source_labels(source_name, df[label_col])
        except ValueError as exc:
            skipped_sources.append((source_name, str(path), str(exc)))
            continue
        out["source"] = source_name

        if "dialect" in df.columns:
            out["dialect"] = df["dialect"].apply(source_to_dialect_label)
        else:
            out["dialect"] = "unknown"

        parts.append(out)

    if skipped_sources:
        print("Skipped sources:")
        for source_name, path, reason in skipped_sources:
            print(f"  - {source_name}: {path} ({reason})")

    if not parts:
        configured_paths = [str(resolve_data_path(path_str)) for path_str in SOURCE_FILES.values()]
        raise FileNotFoundError(
            "No valid source datasets were loaded. "
            f"Checked {len(configured_paths)} configured paths under {PROJECT_DATA_DIR}."
        )

    merged = pd.concat(parts, ignore_index=True)
    return merged


def clean_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    metrics = {}

    metrics["rows_initial"] = int(len(df))

    if df.empty:
        raise ValueError("No rows available for cleaning after source loading.")

    # Drop rows with invalid labels early
    df = df.dropna(subset=["label"]).copy()
    df["label"] = df["label"].astype(int)
    metrics["rows_after_label_valid"] = int(len(df))

    # Basic text normalization and ratio features
    df["text"] = df["text"].astype(str).map(lambda x: WS_RE.sub(" ", x).strip())
    df = df[df["text"] != ""].copy()
    metrics["rows_after_non_empty_text"] = int(len(df))

    ratio_vals = df["text"].map(arabic_latin_ratio)
    df["arabic_ratio"] = ratio_vals.map(lambda x: x[0])
    df["arabic_chars"] = ratio_vals.map(lambda x: x[1])
    df["latin_chars"] = ratio_vals.map(lambda x: x[2])
    df["code_switched"] = df.apply(
        lambda r: is_code_switched(r["text"], r["arabic_ratio"], int(r["arabic_chars"]), int(r["latin_chars"])),
        axis=1,
    )

    # Keep only Arabic-enough and not code-switched
    before_ratio = len(df)
    df = df[(df["arabic_ratio"] >= ARABIC_RATIO_THRESHOLD) & (df["arabic_chars"] > 0)].copy()
    metrics["dropped_low_arabic_or_non_arabic"] = int(before_ratio - len(df))

    before_cs = len(df)
    df = df[~df["code_switched"]].copy()
    metrics["dropped_code_switched"] = int(before_cs - len(df))

    # Deduplicate with conflict resolution
    df["text_norm"] = df["text"].map(normalize_text)

    grouped = df.groupby("text_norm")

    kept_rows = []
    conflict_discarded = 0

    for _, g in grouped:
        if len(g) == 1:
            kept_rows.append(g.iloc[0])
            continue

        label_counts = g["label"].value_counts()
        if len(label_counts) == 1:
            # same label duplicates: keep one representative (longest text)
            row = g.sort_values(by="text", key=lambda s: s.str.len(), ascending=False).iloc[0]
            kept_rows.append(row)
            continue

        # conflicting labels: keep majority label, discard tie
        top_count = label_counts.max()
        winners = label_counts[label_counts == top_count].index.tolist()
        if len(winners) > 1:
            conflict_discarded += len(g)
            continue

        winner = int(winners[0])
        g_w = g[g["label"] == winner]
        row = g_w.sort_values(by="text", key=lambda s: s.str.len(), ascending=False).iloc[0]
        kept_rows.append(row)

    cleaned = pd.DataFrame(kept_rows).reset_index(drop=True)

    metrics["rows_after_dedup_conflict_resolution"] = int(len(cleaned))
    metrics["conflict_rows_discarded_due_to_tie"] = int(conflict_discarded)
    metrics["duplicate_text_groups_after_cleaning"] = int(cleaned["text_norm"].duplicated().sum())

    if cleaned.empty:
        raise ValueError("Cleaning removed all rows. Check the Arabic/code-switch filters and source labels.")

    cleaned = cleaned[["text", "label", "dialect", "source", "arabic_ratio"]].copy()

    return cleaned, metrics


def build_strat_key(df: pd.DataFrame) -> pd.Series:
    d_counts = df["dialect"].value_counts()
    use_dialect = df["dialect"].map(lambda d: d_counts.get(d, 0) >= MIN_DIALECT_FOR_STRAT)
    strat_key = np.where(use_dialect, df["label"].astype(str) + "__" + df["dialect"].astype(str), df["label"].astype(str))
    strat_key = pd.Series(strat_key, index=df.index)

    # train_test_split requires each class in stratify to have at least 2 samples
    key_counts = strat_key.value_counts()
    if (key_counts < 2).any():
        return df["label"].astype(str)
    return strat_key


def ensure_dialect_presence(train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    all_df = pd.concat([train_df, val_df, test_df], ignore_index=True)
    global_counts = all_df["dialect"].value_counts()
    important = [d for d, c in global_counts.items() if c >= MIN_DIALECT_FOR_STRAT]

    def move_one(src: pd.DataFrame, dst: pd.DataFrame, dialect: str):
        candidates = src[src["dialect"] == dialect]
        if candidates.empty:
            return src, dst
        # move sample with minority label preference in destination for better balance
        dst_label_counts = dst["label"].value_counts() if not dst.empty else pd.Series(dtype=int)
        target_label = 1 if dst_label_counts.get(1, 0) <= dst_label_counts.get(0, 0) else 0
        preferred = candidates[candidates["label"] == target_label]
        row = preferred.iloc[[0]] if not preferred.empty else candidates.iloc[[0]]
        src = src.drop(index=row.index)
        dst = pd.concat([dst, row], ignore_index=True)
        return src, dst

    for d in important:
        if (val_df["dialect"] == d).sum() == 0:
            train_df, val_df = move_one(train_df, val_df, d)
        if (test_df["dialect"] == d).sum() == 0:
            train_df, test_df = move_one(train_df, test_df, d)

    return train_df.reset_index(drop=True), val_df.reset_index(drop=True), test_df.reset_index(drop=True)


def rebalance_train_if_needed(train_df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    stats = {}
    c = train_df["label"].value_counts()
    n0 = int(c.get(0, 0))
    n1 = int(c.get(1, 0))
    if min(n0, n1) == 0:
        stats["rebalanced"] = False
        stats["reason"] = "one_class_only"
        return train_df, stats

    ratio = max(n0, n1) / min(n0, n1)
    stats["before_ratio"] = round(ratio, 3)

    if ratio <= MAX_TRAIN_IMBALANCE_RATIO:
        stats["rebalanced"] = False
        return train_df, stats

    maj_label = 0 if n0 > n1 else 1
    min_label = 1 - maj_label
    n_min = int((train_df["label"] == min_label).sum())
    target_maj = int(MAX_TRAIN_IMBALANCE_RATIO * n_min)

    maj_df = train_df[train_df["label"] == maj_label].sample(n=target_maj, random_state=RANDOM_STATE)
    min_df = train_df[train_df["label"] == min_label]
    out = pd.concat([maj_df, min_df], ignore_index=True).sample(frac=1.0, random_state=RANDOM_STATE).reset_index(drop=True)

    c2 = out["label"].value_counts()
    n0b = int(c2.get(0, 0))
    n1b = int(c2.get(1, 0))
    stats["rebalanced"] = True
    stats["after_ratio"] = round(max(n0b, n1b) / min(n0b, n1b), 3)
    stats["dropped_majority_rows"] = int(len(train_df) - len(out))
    return out, stats


def split_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if df.empty:
        raise ValueError("Cannot split an empty dataset.")
    if df["label"].nunique() < 2:
        raise ValueError("Need at least two label classes to build train/val/test splits.")
    if len(df) < 10:
        raise ValueError(f"Dataset is too small to split reliably: only {len(df)} rows remain.")

    strat_key = build_strat_key(df)
    try:
        train_df, temp_df = train_test_split(
            df,
            test_size=(VAL_SIZE + TEST_SIZE),
            random_state=RANDOM_STATE,
            stratify=strat_key,
        )
    except ValueError:
        train_df, temp_df = train_test_split(
            df,
            test_size=(VAL_SIZE + TEST_SIZE),
            random_state=RANDOM_STATE,
            stratify=df["label"],
        )

    # Second split: stratify on label to avoid sparse key failures
    temp_strat = temp_df["label"]
    try:
        val_df, test_df = train_test_split(
            temp_df,
            test_size=0.5,
            random_state=RANDOM_STATE,
            stratify=temp_strat,
        )
    except ValueError:
        val_df, test_df = train_test_split(
            temp_df,
            test_size=0.5,
            random_state=RANDOM_STATE,
            stratify=None,
        )

    train_df, val_df, test_df = ensure_dialect_presence(train_df, val_df, test_df)
    train_df, _ = rebalance_train_if_needed(train_df)

    return train_df.reset_index(drop=True), val_df.reset_index(drop=True), test_df.reset_index(drop=True)


def summarize_split(df: pd.DataFrame) -> dict:
    c = df["label"].value_counts()
    n0 = int(c.get(0, 0))
    n1 = int(c.get(1, 0))
    ratio = None if min(n0, n1) == 0 else round(max(n0, n1) / min(n0, n1), 3)
    return {
        "rows": int(len(df)),
        "label_0": n0,
        "label_1": n1,
        "majority_to_minority_ratio": ratio,
        "dialect_counts": {str(k): int(v) for k, v in df["dialect"].value_counts().to_dict().items()},
        "source_counts": {str(k): int(v) for k, v in df["source"].value_counts().to_dict().items()},
        "arabic_ratio_min": round(float(df["arabic_ratio"].min()), 4) if len(df) else None,
        "arabic_ratio_mean": round(float(df["arabic_ratio"].mean()), 4) if len(df) else None,
    }


def main():
    out_dir = resolve_data_path("cleaned")
    out_dir.mkdir(parents=True, exist_ok=True)

    raw_df = load_all_sources()
    cleaned_df, clean_metrics = clean_dataset(raw_df)

    train_df, val_df, test_df = split_dataset(cleaned_df)

    # Save cleaned master and splits
    cleaned_df.to_csv(out_dir / "marbert_safe_all.csv", index=False, encoding="utf-8")
    train_df.to_csv(out_dir / "train.csv", index=False, encoding="utf-8")
    val_df.to_csv(out_dir / "val.csv", index=False, encoding="utf-8")
    test_df.to_csv(out_dir / "test.csv", index=False, encoding="utf-8")

    # Rebuild project splits
    train_df[["text", "label", "dialect", "source"]].to_csv(resolve_data_path("train.csv"), index=False, encoding="utf-8")
    val_df[["text", "label", "dialect", "source"]].to_csv(resolve_data_path("val.csv"), index=False, encoding="utf-8")
    test_df[["text", "label", "dialect", "source"]].to_csv(resolve_data_path("test.csv"), index=False, encoding="utf-8")

    summary = {
        "config": {
            "arabic_ratio_threshold": ARABIC_RATIO_THRESHOLD,
            "excluded_english_files": EXCLUDED_ENGLISH_FILES,
            "drop_code_switched": True,
            "train_val_test": [TRAIN_SIZE, VAL_SIZE, TEST_SIZE],
            "min_dialect_for_strat": MIN_DIALECT_FOR_STRAT,
            "max_train_imbalance_ratio": MAX_TRAIN_IMBALANCE_RATIO,
        },
        "cleaning_metrics": clean_metrics,
        "overall_cleaned": summarize_split(cleaned_df),
        "train": summarize_split(train_df),
        "val": summarize_split(val_df),
        "test": summarize_split(test_df),
    }

    (out_dir / "marbert_safe_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = [
        "# MARBERT-safe Cleaned Dataset Summary",
        "",
        "## Config",
        f"- Arabic ratio threshold: {ARABIC_RATIO_THRESHOLD}",
        "- Excluded all iSarcasmEval English files",
        "- Dropped code-switched rows",
        f"- Split ratio train/val/test: {TRAIN_SIZE}/{VAL_SIZE}/{TEST_SIZE}",
        f"- Dialect-aware strat key min dialect count: {MIN_DIALECT_FOR_STRAT}",
        f"- Train max imbalance ratio: {MAX_TRAIN_IMBALANCE_RATIO}",
        "",
        "## Cleaning Metrics",
    ]

    for k, v in clean_metrics.items():
        md_lines.append(f"- {k}: {v}")

    def append_split(name: str, stats: dict):
        md_lines.append("")
        md_lines.append(f"## {name}")
        md_lines.append(f"- rows: {stats['rows']}")
        md_lines.append(f"- label_0: {stats['label_0']}")
        md_lines.append(f"- label_1: {stats['label_1']}")
        md_lines.append(f"- majority_to_minority_ratio: {stats['majority_to_minority_ratio']}")
        md_lines.append(f"- arabic_ratio_min: {stats['arabic_ratio_min']}")
        md_lines.append(f"- arabic_ratio_mean: {stats['arabic_ratio_mean']}")
        md_lines.append(f"- dialect_counts: {stats['dialect_counts']}")
        md_lines.append(f"- source_counts: {stats['source_counts']}")

    append_split("Overall cleaned", summary["overall_cleaned"])
    append_split("Train", summary["train"])
    append_split("Validation", summary["val"])
    append_split("Test", summary["test"])

    (out_dir / "marbert_safe_summary.md").write_text("\n".join(md_lines), encoding="utf-8")

    print("Saved cleaned datasets and rebuilt project splits.")
    print("- data/cleaned/marbert_safe_all.csv")
    print("- data/cleaned/train.csv")
    print("- data/cleaned/val.csv")
    print("- data/cleaned/test.csv")
    print("- data/cleaned/marbert_safe_summary.md")
    print("- data/cleaned/marbert_safe_summary.json")
    print("- data/train.csv")
    print("- data/val.csv")
    print("- data/test.csv")


if __name__ == "__main__":
    main()
