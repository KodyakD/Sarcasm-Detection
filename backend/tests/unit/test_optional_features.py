from __future__ import annotations

from analysis_features import build_feature_enrichment


def test_feature_enrichment_detects_sarcasm_cues() -> None:
    text = "رائع جداً، ألغوا الاجتماع بعد أن وصل الجميع!!!"

    result = build_feature_enrichment(text, confidence=0.87, is_sarcastic=True)

    assert result["sarcasm_type"] in {
        "polarity_contrast",
        "exaggeration",
        "rhetorical_question",
        "ironic_comparison",
    }
    assert result["target"] in {
        "person",
        "organization",
        "product",
        "situation",
        "government",
    }
    assert isinstance(result["intensity"], int)
    assert 1 <= result["intensity"] <= 5
    assert result["indicators"]
    assert "Detected" in result["explanation"]


def test_feature_enrichment_returns_none_for_non_sarcastic_text() -> None:
    text = "اليوم الطقس جميل وذهبت للتنزه مع العائلة"

    result = build_feature_enrichment(text, confidence=0.12, is_sarcastic=False)

    assert result["sarcasm_type"] == "none"
    assert result["target"] == "none"
    assert result["intensity"] == 1
    assert result["indicators"] == []
    assert "did not cross" in result["explanation"]


def test_feature_enrichment_detects_government_and_product_targets() -> None:
    government_text = "الوزارة قالت إن الإصلاحات الاقتصادية ناجحة جداً"
    product_text = "اللاب توب الجبار ده رخيص، بس بيسخن لدرجة تقدر تسوي عليه بيض"

    government_result = build_feature_enrichment(
        government_text, confidence=0.78, is_sarcastic=True
    )
    product_result = build_feature_enrichment(
        product_text, confidence=0.84, is_sarcastic=True
    )

    assert government_result["target"] == "government"
    assert product_result["target"] == "product"