# MARBERT-safe Cleaned Dataset Summary

## Config
- Arabic ratio threshold: 0.3
- Excluded all iSarcasmEval English files
- Dropped code-switched rows
- Split ratio train/val/test: 0.8/0.1/0.1
- Dialect-aware strat key min dialect count: 25
- Train max imbalance ratio: 20.0

## Cleaning Metrics
- rows_initial: 31399
- rows_after_label_valid: 31396
- rows_after_non_empty_text: 31396
- dropped_low_arabic_or_non_arabic: 161
- dropped_code_switched: 4789
- rows_after_dedup_conflict_resolution: 22789
- conflict_rows_discarded_due_to_tie: 66
- duplicate_text_groups_after_cleaning: 0

## Overall cleaned
- rows: 22789
- label_0: 15933
- label_1: 6856
- majority_to_minority_ratio: 2.324
- arabic_ratio_min: 0.7009
- arabic_ratio_mean: 0.943
- dialect_counts: {'msa': 11411, 'egypt': 4447, 'levant': 3668, 'gulf': 1467, 'egyptian': 803, 'algerian': 791, 'magreb': 202}
- source_counts: {'arsarcasm_train': 9802, 'ar_sarcasm_hf_train': 3831, 'arsarcasm_test': 2721, 'training_generated': 2592, 'isemeval_ar_train': 2443, 'isemeval_ar_test_A': 1400}

## Train
- rows: 18231
- label_0: 12746
- label_1: 5485
- majority_to_minority_ratio: 2.324
- arabic_ratio_min: 0.7009
- arabic_ratio_mean: 0.943
- dialect_counts: {'msa': 9128, 'egypt': 3558, 'levant': 2934, 'gulf': 1174, 'egyptian': 642, 'algerian': 633, 'magreb': 162}
- source_counts: {'arsarcasm_train': 7826, 'ar_sarcasm_hf_train': 3057, 'arsarcasm_test': 2187, 'training_generated': 2068, 'isemeval_ar_train': 1979, 'isemeval_ar_test_A': 1114}

## Validation
- rows: 2279
- label_0: 1593
- label_1: 686
- majority_to_minority_ratio: 2.322
- arabic_ratio_min: 0.701
- arabic_ratio_mean: 0.943
- dialect_counts: {'msa': 1119, 'egypt': 458, 'levant': 357, 'gulf': 145, 'egyptian': 91, 'algerian': 87, 'magreb': 22}
- source_counts: {'arsarcasm_train': 984, 'ar_sarcasm_hf_train': 381, 'training_generated': 273, 'arsarcasm_test': 261, 'isemeval_ar_train': 238, 'isemeval_ar_test_A': 142}

## Test
- rows: 2279
- label_0: 1594
- label_1: 685
- majority_to_minority_ratio: 2.327
- arabic_ratio_min: 0.7009
- arabic_ratio_mean: 0.9425
- dialect_counts: {'msa': 1164, 'egypt': 431, 'levant': 377, 'gulf': 148, 'algerian': 71, 'egyptian': 70, 'magreb': 18}
- source_counts: {'arsarcasm_train': 992, 'ar_sarcasm_hf_train': 393, 'arsarcasm_test': 273, 'training_generated': 251, 'isemeval_ar_train': 226, 'isemeval_ar_test_A': 144}