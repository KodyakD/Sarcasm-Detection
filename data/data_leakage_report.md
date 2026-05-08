# Cross-source Overlap & Leakage Risk

## Unique Text Counts
- arsarcasm_train: 12487 unique texts
- arsarcasm_test: 2996 unique texts
- isemeval_ar_train: 3102 unique texts
- isemeval_ar_test_A: 1400 unique texts
- ar_sarcasm_hf: 8178 unique texts

## Pairwise Overlap
- arsarcasm_train ∩ arsarcasm_test: 2
- arsarcasm_train ∩ isemeval_ar_train: 659
- arsarcasm_train ∩ isemeval_ar_test_A: 0
- arsarcasm_train ∩ ar_sarcasm_hf: 2368
- arsarcasm_test ∩ isemeval_ar_train: 0
- arsarcasm_test ∩ isemeval_ar_test_A: 0
- arsarcasm_test ∩ ar_sarcasm_hf: 0
- isemeval_ar_train ∩ isemeval_ar_test_A: 0
- isemeval_ar_train ∩ ar_sarcasm_hf: 703
- isemeval_ar_test_A ∩ ar_sarcasm_hf: 0

## Leakage Warnings
- ArSarcasm official train/test overlap: 2
- iSarcasmEval Ar train/test overlap (Task A): 0
- Risk: If original test files are merged into training pool and then re-split, evaluation may be optimistic.