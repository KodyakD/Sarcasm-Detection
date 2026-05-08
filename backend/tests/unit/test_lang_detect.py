from __future__ import annotations

from lang_detect import detect_language


def test_detect_language_darija_marker() -> None:
    assert detect_language("wach hadchi mzyan") == "darija"


def test_detect_language_arabic_script() -> None:
    assert detect_language("هذا نص عربي واضح") == "arabic"


def test_detect_language_unknown_for_empty() -> None:
    assert detect_language("   ") == "unknown"
