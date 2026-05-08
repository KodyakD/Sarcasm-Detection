# Data Audit Report

## Scope
- data/raw/training_data.csv
- data/raw/testing_data.csv
- data/raw/iSarcasmEval-main/train/train.Ar.csv
- data/raw/iSarcasmEval-main/test/task_A_Ar_test.csv
- data/raw/ar_sarcasm_hf_train.csv
- data/train.csv
- data/val.csv
- data/test.csv

## Per-file Summary

### data\raw\training_data.csv
- Shape: 12548 rows x 4 columns
- Label column: sarcasm
- Text column: tweet
- Duplicate rows: 16
- Duplicate text values: 61
- Missing values: none
- Label distribution: False: 10380 (82.72%), True: 2168 (17.28%)
- Text length stats: min=4, mean=102.9, median=108.0, p95=142.0, max=303, empty=0

### data\raw\testing_data.csv
- Shape: 3000 rows x 4 columns
- Label column: sarcasm
- Text column: tweet
- Duplicate rows: 2
- Duplicate text values: 4
- Missing values: none
- Label distribution: False: 2179 (72.63%), True: 821 (27.37%)
- Text length stats: min=2, mean=101.11, median=97.0, p95=242.0, max=304, empty=0

### data\raw\iSarcasmEval-main\train\train.Ar.csv
- Shape: 3102 rows x 5 columns
- Label column: sarcastic
- Text column: text
- Duplicate rows: 0
- Duplicate text values: 0
- Missing values: rephrase=2357 (75.98%)
- Label distribution: 0: 2357 (75.98%), 1: 745 (24.02%)
- Text length stats: min=5, mean=76.77, median=72.0, p95=138.0, max=191, empty=0

### data\raw\iSarcasmEval-main\test\task_A_Ar_test.csv
- Shape: 1400 rows x 3 columns
- Label column: sarcastic
- Text column: text
- Duplicate rows: 0
- Duplicate text values: 0
- Missing values: none
- Label distribution: 0: 1200 (85.71%), 1: 200 (14.29%)
- Text length stats: min=3, mean=32.29, median=28.0, p95=68.0, max=280, empty=0

### data\raw\ar_sarcasm_hf_train.csv
- Shape: 8437 rows x 6 columns
- Label column: sarcasm
- Text column: tweet
- Duplicate rows: 96
- Duplicate text values: 259
- Missing values: none
- Label distribution: 0: 7100 (84.15%), 1: 1337 (15.85%)
- Text length stats: min=8, mean=102.08, median=109.0, p95=139.0, max=143, empty=0

### data\train.csv
- Shape: 8 rows x 4 columns
- Label column: label
- Text column: text
- Duplicate rows: 0
- Duplicate text values: 0
- Missing values: none
- Label distribution: 1: 4 (50.0%), 0: 4 (50.0%)
- Text length stats: min=19, mean=26.62, median=26.5, p95=33.95, max=35, empty=0

### data\val.csv
- Shape: 2 rows x 4 columns
- Label column: label
- Text column: text
- Duplicate rows: 0
- Duplicate text values: 0
- Missing values: none
- Label distribution: 1: 1 (50.0%), 0: 1 (50.0%)
- Text length stats: min=21, mean=24.5, median=24.5, p95=27.65, max=28, empty=0

### data\test.csv
- Shape: 2 rows x 4 columns
- Label column: label
- Text column: text
- Duplicate rows: 0
- Duplicate text values: 0
- Missing values: none
- Label distribution: 1: 1 (50.0%), 0: 1 (50.0%)
- Text length stats: min=20, mean=23.0, median=23.0, p95=25.7, max=26, empty=0

## Combined Arabic Sources Overview
- rows_before_cleaning: 28487
- label_missing: 0
- empty_text: 0
- duplicate_text: 3363
- rows_after_basic_cleaning: 28487
- label_distribution_after_cleaning: {'0': {'count': 23216, 'pct': 81.5}, '1': {'count': 5271, 'pct': 18.5}}