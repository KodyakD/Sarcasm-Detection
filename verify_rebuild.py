import json
summary = json.load(open('data/cleaned/marbert_safe_summary.json'))
print('✅ DATASET REBUILD COMPLETE\n')
print('SPLITS:')
print(f"  Train: {summary['train']['rows']:,} rows ({summary['train']['label_1']:,} sarcasm)")
print(f"  Val:   {summary['val']['rows']:,} rows ({summary['val']['label_1']:,} sarcasm)")
print(f"  Test:  {summary['test']['rows']:,} rows ({summary['test']['label_1']:,} sarcasm)")
print('\nCLASS DISTRIBUTION:')
print(f"  Overall ratio: {summary['overall_cleaned']['majority_to_minority_ratio']:.3f}:1 (natural)")
print(f"  Min Arabic ratio: {summary['overall_cleaned']['arabic_ratio_min']:.4f}")
print(f"  Mean Arabic ratio: {summary['overall_cleaned']['arabic_ratio_mean']:.4f}")
print('\nSOURCES INCLUDED (ADArabic removed ✓):')
for src, count in summary['overall_cleaned']['source_counts'].items():
    print(f"  {src}: {count:,}")
