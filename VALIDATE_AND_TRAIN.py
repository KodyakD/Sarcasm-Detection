#!/usr/bin/env python
"""
Complete validation and training prep script.
Run this to verify all fixes are working before uploading to Kaggle.
"""

import pandas as pd
import json
import sys

def validate_datasets():
    """Validate that all rebuilt datasets are correct."""
    print("=" * 70)
    print("STEP 1: VALIDATING DATASETS")
    print("=" * 70)
    
    try:
        train = pd.read_csv('data/train.csv')
        val = pd.read_csv('data/val.csv')
        test = pd.read_csv('data/test.csv')
        
        # Check sizes
        assert len(train) == 16157, f"Train size mismatch: {len(train)}"
        assert len(val) == 2020, f"Val size mismatch: {len(val)}"
        assert len(test) == 2020, f"Test size mismatch: {len(test)}"
        
        # Check labels
        assert (train['label'] == 1).sum() == 3463, "Train sarcasm count mismatch"
        assert (val['label'] == 1).sum() == 433, "Val sarcasm count mismatch"
        assert (test['label'] == 1).sum() == 433, "Test sarcasm count mismatch"
        
        # Check integrity
        assert train['text'].isnull().sum() == 0, "Train has NaN text"
        assert val['text'].isnull().sum() == 0, "Val has NaN text"
        assert test['text'].isnull().sum() == 0, "Test has NaN text"
        
        assert train['text'].duplicated().sum() == 0, "Train has duplicates"
        
        print("✅ All datasets valid")
        print(f"   Train: {len(train):,} rows ({(train['label']==1).sum():,} sarcasm)")
        print(f"   Val:   {len(val):,} rows ({(val['label']==1).sum():,} sarcasm)")
        print(f"   Test:  {len(test):,} rows ({(test['label']==1).sum():,} sarcasm)")
        print()
        return True
    except Exception as e:
        print(f"❌ Dataset validation failed: {e}")
        return False

def validate_config():
    """Validate that all fixes are in the configuration."""
    print("=" * 70)
    print("STEP 2: VALIDATING FIXES IN CONFIGURATION")
    print("=" * 70)
    
    try:
        with open('data/cleaned/marbert_safe_summary.json') as f:
            summary = json.load(f)
        
        config = summary['config']
        
        # Check key settings
        assert config['arabic_ratio_threshold'] == 0.3, "Arabic threshold not relaxed"
        
        # Check data sources
        sources = summary['overall_cleaned']['source_counts']
        assert 'adarabic_cla_45000' not in str(sources), "ADArabic still in sources"
        assert len(sources) == 5, f"Wrong number of sources: {len(sources)}"
        
        # Check ratio is natural
        ratio = summary['overall_cleaned']['majority_to_minority_ratio']
        assert 3.6 < ratio < 3.7, f"Class ratio not natural: {ratio}"
        
        print("✅ All fixes verified in configuration")
        print(f"   Arabic ratio threshold: 0.3 ✓")
        print(f"   ADArabic removed ✓")
        print(f"   Natural class ratio: {ratio:.3f}:1 ✓")
        print(f"   Sources: {len(sources)} (verified) ✓")
        print()
        return True
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False

def validate_code():
    """Validate that all code fixes are applied."""
    print("=" * 70)
    print("STEP 3: VALIDATING CODE FIXES")
    print("=" * 70)
    
    try:
        with open('data/build_marbert_safe_dataset.py') as f:
            code = f.read()
        
        checks = [
            ("MAX_TRAIN_IMBALANCE_RATIO = 20.0", "Double-weighting fix"),
            ("ARABIC_RATIO_THRESHOLD = 0.30", "Arabic threshold relaxation"),
            ('# "adarabic_cla_45000"', "ADArabic removal"),
        ]
        
        for check_str, label in checks:
            assert check_str in code, f"Missing: {label}"
            print(f"   ✓ {label}")
        
        print("\n✅ All code fixes verified")
        print()
        return True
    except Exception as e:
        print(f"❌ Code validation failed: {e}")
        return False

def main():
    """Run all validations."""
    print("\n" + "=" * 70)
    print("COMPREHENSIVE VALIDATION: Dataset Fixes & Ready for Kaggle")
    print("=" * 70)
    print()
    
    results = [
        validate_datasets(),
        validate_config(),
        validate_code(),
    ]
    
    if all(results):
        print("=" * 70)
        print("✅ ALL VALIDATIONS PASSED")
        print("=" * 70)
        print()
        print("NEXT STEPS:")
        print("1. Upload data/train.csv, data/val.csv, data/test.csv to Kaggle")
        print("2. Run notebooks/latest.ipynb on Kaggle")
        print("3. Monitor metrics for 65-75%+ F1 on new data")
        print()
        print("Expected improvement: 25-35 percentage point F1 gain")
        print()
        return 0
    else:
        print()
        print("❌ VALIDATION FAILED - Please fix issues before proceeding")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
