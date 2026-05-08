from __future__ import annotations

from typing import Any

try:
    from ..gemini import analyze_with_gemini
    from ..inference import get_threshold, predict
    from ..lang_detect import detect_language
    from ..schemas import AnalyzeResponse, Language, LanguageOverride, SarcasmType
except ImportError:  # pragma: no cover - supports top-level test imports
    from gemini import analyze_with_gemini
    from inference import get_threshold, predict
    from lang_detect import detect_language
    from schemas import AnalyzeResponse, Language, LanguageOverride, SarcasmType


def resolve_language(text: str, language_override: LanguageOverride | None) -> str:
    if language_override is not None:
        return language_override.value
    return detect_language(text)


def analyze_text(
    text: str, language_override: LanguageOverride | None
) -> AnalyzeResponse:
    language = resolve_language(text, language_override)
    predicted = predict(text=text, language=language)

    enrichment: dict[str, Any] = analyze_with_gemini(
        text=text,
        language=language,
        is_sarcastic=bool(predicted["is_sarcastic"]),
        confidence=float(predicted["confidence"]),
    )

    normalized_language = (
        language
        if language in {lang.value for lang in Language}
        else Language.UNKNOWN.value
    )

    return AnalyzeResponse(
        is_sarcastic=bool(predicted["is_sarcastic"]),
        confidence=float(predicted["confidence"]),
        language=Language(normalized_language),
        sarcasm_type=SarcasmType(
            str(enrichment.get("sarcasm_type", SarcasmType.NONE.value))
        ),
        target=str(enrichment.get("target", "none")),
        intensity=int(enrichment.get("intensity", 1)),
        explanation=str(enrichment.get("explanation", "Analysis unavailable")),
        indicators=[str(item) for item in enrichment.get("indicators", [])],
        threshold=get_threshold(),
    )
