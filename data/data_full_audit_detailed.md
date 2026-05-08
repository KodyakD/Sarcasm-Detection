# Full Data Audit (Arabic Sarcasm Pipeline)

## 1) Empty or Malformed Arabic Texts
- arsarcasm_train: rows=12548, empty=0, malformed=1672 (13.32%), non_arabic=3 (0.02%)
  reasons: low_arabic_ratio=1559, url_heavy_short=144, too_short_tokens=127, no_arabic_chars=3
- arsarcasm_test: rows=3000, empty=0, malformed=282 (9.4%), non_arabic=2 (0.07%)
  reasons: low_arabic_ratio=192, too_short_tokens=107, url_heavy_short=96, no_arabic_chars=2
- isemeval_ar_train: rows=3102, empty=0, malformed=38 (1.23%), non_arabic=0 (0.0%)
  reasons: too_short_tokens=29, low_arabic_ratio=10
- isemeval_ar_test_A: rows=1400, empty=0, malformed=69 (4.93%), non_arabic=0 (0.0%)
  reasons: too_short_tokens=53, low_arabic_ratio=16
- ar_sarcasm_hf_train: rows=8437, empty=0, malformed=1135 (13.45%), non_arabic=2 (0.02%)
  reasons: low_arabic_ratio=1086, url_heavy_short=60, too_short_tokens=46, no_arabic_chars=2
- project_train: rows=8, empty=0, malformed=6 (75.0%), non_arabic=6 (75.0%)
  reasons: no_arabic_chars=6, low_arabic_ratio=6
- project_val: rows=2, empty=0, malformed=2 (100.0%), non_arabic=2 (100.0%)
  reasons: no_arabic_chars=2, low_arabic_ratio=2
- project_test: rows=2, empty=0, malformed=2 (100.0%), non_arabic=2 (100.0%)
  reasons: no_arabic_chars=2, low_arabic_ratio=2

## 2) Label Balance
- arsarcasm_train: label0=10380, label1=2168, majority:minority=4.79
- arsarcasm_test: label0=2179, label1=821, majority:minority=2.65
- isemeval_ar_train: label0=2357, label1=745, majority:minority=3.16
- isemeval_ar_test_A: label0=1200, label1=200, majority:minority=6.0
- ar_sarcasm_hf_train: label0=7100, label1=1337, majority:minority=5.31
- project_train: label0=4, label1=4, majority:minority=1.0
- project_val: label0=1, label1=1, majority:minority=1.0
- project_test: label0=1, label1=1, majority:minority=1.0

## 3) Dialect Distribution and Scarcity
- arsarcasm_train: total_dialects=5, rare(<50)=1
  rare dialects: magreb=43
- arsarcasm_test: total_dialects=5, rare(<50)=2
  rare dialects: magreb=2, levant=47
- isemeval_ar_train: total_dialects=5, rare(<50)=0
- isemeval_ar_test_A: total_dialects=5, rare(<50)=0
- ar_sarcasm_hf_train: total_dialects=5, rare(<50)=1
  rare dialects: 3.0=28

## 4) English / Code-switched Texts
- arsarcasm_train: code_switched=5288 (42.14%), non_arabic=3 (0.02%)
- arsarcasm_test: code_switched=491 (16.37%), non_arabic=2 (0.07%)
- isemeval_ar_train: code_switched=1 (0.03%), non_arabic=0 (0.0%)
- isemeval_ar_test_A: code_switched=0 (0.0%), non_arabic=0 (0.0%)
- ar_sarcasm_hf_train: code_switched=4038 (47.86%), non_arabic=2 (0.02%)
- project_train: code_switched=0 (0.0%), non_arabic=6 (75.0%)
- project_val: code_switched=0 (0.0%), non_arabic=2 (100.0%)
- project_test: code_switched=0 (0.0%), non_arabic=2 (100.0%)

## 5) Duplicates and Conflicting Labels
- arsarcasm_train: duplicate_texts=61, conflicting_labels_within_file=17
- arsarcasm_test: duplicate_texts=4, conflicting_labels_within_file=1
- isemeval_ar_train: duplicate_texts=0, conflicting_labels_within_file=0
- isemeval_ar_test_A: duplicate_texts=0, conflicting_labels_within_file=0
- ar_sarcasm_hf_train: duplicate_texts=259, conflicting_labels_within_file=41
- project_train: duplicate_texts=0, conflicting_labels_within_file=0
- project_val: duplicate_texts=0, conflicting_labels_within_file=0
- project_test: duplicate_texts=0, conflicting_labels_within_file=0
- Cross-source: duplicate_texts=2763, conflicting_labels=66, unique_texts=24977, total_rows=28499