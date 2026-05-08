from __future__ import annotations

import re

from langdetect import DetectorFactory, detect

DetectorFactory.seed = 0

_DARIJA_WORDS = {
    "wach",
    "rahi",
    "bezzaf",
    "chwiya",
    "khoya",
    "3ndek",
    "marhba",
    "wlah",
    "bzaf",
    "labas",
}
_ARABIZI_PATTERN = re.compile(r"[a-zA-Z].*[379]|[379].*[a-zA-Z]")
_ARABIC_SCRIPT = re.compile(r"[\u0600-\u06FF]")


def _contains_darija_markers(text: str) -> bool:
    lowered = text.lower()
    if any(word in lowered for word in _DARIJA_WORDS):
        return True
    return bool(_ARABIZI_PATTERN.search(lowered))


def detect_language(text: str) -> str:
    candidate = text.strip()
    if not candidate:
        return "unknown"

    if _contains_darija_markers(candidate):
        return "darija"

    try:
        code = detect(candidate)
    except Exception:
        return "unknown"

    if code == "ar":
        return "arabic" if _ARABIC_SCRIPT.search(candidate) else "darija"
    if code == "fr":
        return "french"
    if code == "en":
        return "english"
    return "unknown"
