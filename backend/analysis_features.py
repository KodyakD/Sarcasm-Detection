from __future__ import annotations

import re
from dataclasses import dataclass

try:
    from .schemas import SarcasmType
except ImportError:  # pragma: no cover - supports top-level test imports
    from schemas import SarcasmType


_POSITIVE_WORDS = [
    "رائع",
    "ممتاز",
    "جميل",
    "عظيم",
    "مذهل",
    "تحفة",
    "فخم",
    "يعطيك الصحة",
    "صحيت",
    "شكرا",
    "برافو",
    "هايل",
    "فور",
    "شباب",
    "مليح",
    "طوب",
]

_NEGATIVE_WORDS = [
    "تأخر",
    "فشل",
    "خرب",
    "كارثة",
    "سيء",
    "هدرت",
    "فاشل",
    "ماكاش",
    "والو",
    "زلط",
    "زفت",
    "خايب",
    "غبي",
    "أهبل",
]

_EXAGGERATION_PATTERNS = [
    r"(?:عام كامل|5 سنين|10 مرات|ساعتين|من هنا للصين|الكون كله|العالم كله|كل[^.]*ما)[^.]*",
    r"(?:بزاف|هايل|معجزة|عبقرية|أسطورة)[^.]*",
]

_RHETORICAL_PATTERNS = [
    r".*(?:واش|علاش|كيفاش|شكون|وين|كيف|ليش|إيمتا|هل|أليس)[^؟?]*[؟?]"
]

_COMPARISON_PATTERNS = [
    r"(?:بحال|مثل|زي|كأنه|تشبه|تذكرني|قد|كيف|بزبط)[^.]*(?:السلحفاة|مريض|وجه القمر|نمو الشعر|اللي يعاونك في مصيبة)[^.]*",
    r"(?:بحال|مثل|زي|كأنه|تشبه|تذكرني|قد|كيف|بزبط)[^.]+",
]

_GOVERNMENT_HINTS = [
    r"(?:الحكومة|الوزارة|البلدية|الدولة|الرئيس|الوزير|المسؤول|الضرائب|الوالي|المير|الشرطة|لادوان|الجمارك|المحكمة)"
]
_ORGANIZATION_HINTS = [
    r"(?:الشركة|المؤسسة|البنك|المستشفى|الجامعة|المدرسة|اتصالات|كهرباء|البريد|سونلغاز|لابوست|سبيطار|الفاك)"
]
_PERSON_HINTS = [
    r"(?:الدكتور|المهندس|الأستاذ|المدير|الموظف|العامل|صاحبي|صديقي|أنت|نتايا|خويا|الشيخ|الفورنيسور|طبيب)"
]
_PRODUCT_HINTS = [
    r"(?:السيارة|الهاتف|الجهاز|التطبيق|الأكل|القهوة|الشاي|البيتزا|الماكلة|تليفون|لوطو|طوموبيل|سلعة|الويفي|الكونيكسيون)"
]
_SITUATION_HINTS = [
    r"(?:الوضع|الحال|المشهد|الحفلة|الاجتماع|الموعد|المباراة|الامتحان|الطابور|لاشان|الزحمة|السيركولاسيون|روطار)"
]

_AGGRESSIVE_EMOJIS = [r"🤡", r"🙄", r"🙃", r"🤥", r"🐢", r"🗑️", r"💩"]
_STRONG_EMOJIS = [r"😏", r"😂", r"👏", r"🎉", r"💸", r"🎁", r"😒"]
_SARCASM_EMOJIS = set("😏🙄👏😂🤣💀😒🤦😑😤🤡🙃🤥🐢🗑️💩🎉💸🎁")


def _match_any(text: str, candidates: list[str]) -> list[str]:
    return [candidate for candidate in candidates if candidate in text]


def _has_pattern(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text) for pattern in patterns)


def classify_sarcasm_type(text: str, is_sarcastic: bool) -> SarcasmType:
    if not is_sarcastic:
        return SarcasmType.NONE

    scores = {
        SarcasmType.POLARITY_CONTRAST: 0,
        SarcasmType.EXAGGERATION: 0,
        SarcasmType.RHETORICAL_QUESTION: 0,
        SarcasmType.IRONIC_COMPARISON: 0,
    }

    positive_hits = _match_any(text, _POSITIVE_WORDS)
    negative_hits = _match_any(text, _NEGATIVE_WORDS)
    if positive_hits and negative_hits:
        scores[SarcasmType.POLARITY_CONTRAST] += len(positive_hits) + len(negative_hits)

    if _has_pattern(text, _EXAGGERATION_PATTERNS):
        scores[SarcasmType.EXAGGERATION] += 2

    if "؟" in text or "?" in text or _has_pattern(text, _RHETORICAL_PATTERNS):
        scores[SarcasmType.RHETORICAL_QUESTION] += 2

    if _has_pattern(text, _COMPARISON_PATTERNS):
        scores[SarcasmType.IRONIC_COMPARISON] += 2

    best_type = max(scores, key=scores.get)
    return best_type if scores[best_type] > 0 else SarcasmType.POLARITY_CONTRAST


def identify_target(text: str, is_sarcastic: bool) -> str:
    if not is_sarcastic:
        return "none"

    if _has_pattern(text, _GOVERNMENT_HINTS):
        return "government"
    if _has_pattern(text, _PRODUCT_HINTS):
        return "product"
    if _has_pattern(text, _ORGANIZATION_HINTS):
        return "organization"
    if _has_pattern(text, _PERSON_HINTS):
        return "person"
    return "situation"


def compute_intensity(text: str, sarcasm_confidence: float, is_sarcastic: bool) -> int:
    if not is_sarcastic:
        return 1

    intensity = 1.0
    if sarcasm_confidence < 0.5:
        intensity += 1.0
    elif sarcasm_confidence < 0.7:
        intensity += 1.5
    elif sarcasm_confidence < 0.9:
        intensity += 2.0
    else:
        intensity += 3.0

    for m in _AGGRESSIVE_EMOJIS:
        if re.search(m, text):
            intensity += 1.5
            break
    else:
        for m in _STRONG_EMOJIS:
            if re.search(m, text):
                intensity += 0.8
                break

    aggressive_hits = _match_any(
        text,
        [
            "خرا",
            "حمار",
            "غبي",
            "مجنون",
            "حقير",
            "كذاب",
            "فاشل",
            "تافه",
            "خسيس",
            "حثالة",
            "حرقت",
            "هدمت",
            "دمرت",
            "خربت",
            "زلط",
            "زفت",
            "خايب",
            "أهبل",
        ],
    )
    if aggressive_hits:
        intensity += 1.5

    if text.count("!") >= 2 or text.count("؟") >= 2:
        intensity += 0.5

    return max(1, min(5, int(round(intensity))))


def extract_indicators(text: str, is_sarcastic: bool) -> list[str]:
    indicators: list[str] = []

    positive_hits = _match_any(text, _POSITIVE_WORDS)
    negative_hits = _match_any(text, _NEGATIVE_WORDS)
    if positive_hits and negative_hits:
        words = ", ".join(positive_hits + negative_hits)
        indicators.append(f"تباين بين كلمات إيجابية وسياق سلبي ({words})")

    exaggeration_matches = []
    for pattern in _EXAGGERATION_PATTERNS:
        matches = re.findall(pattern, text)
        exaggeration_matches.extend([m for m in matches if m.strip()])
    if exaggeration_matches:
        words = ", ".join(exaggeration_matches)
        indicators.append(f"مبالغة لغوية واضحة ({words})")

    if "؟" in text or "?" in text or _has_pattern(text, _RHETORICAL_PATTERNS):
        rhetorical_matches = []
        for pattern in _RHETORICAL_PATTERNS:
            matches = re.findall(pattern, text)
            rhetorical_matches.extend([m for m in matches if m.strip()])
        words = f" ({', '.join(rhetorical_matches)})" if rhetorical_matches else ""
        indicators.append(f"صياغة سؤال بلاغي{words}")

    comparison_matches = []
    for pattern in _COMPARISON_PATTERNS:
        matches = re.findall(pattern, text)
        comparison_matches.extend([m for m in matches if m.strip()])
    if comparison_matches:
        words = ", ".join(comparison_matches)
        indicators.append(f"مقارنة ساخرة أو تحقيرية ({words})")

    emoji_hits = [char for char in text if char in _SARCASM_EMOJIS]
    if emoji_hits:
        indicators.append(f"إيموجي ساخر: {' '.join(sorted(set(emoji_hits)))}")

    punct_count = len(re.findall(r"[!?؟]", text))
    if punct_count >= 2:
        indicators.append(f"علامات تعجب/استفهام متعددة ({punct_count})")

    if re.search(r"(.)\1{3,}", text):
        indicators.append("تمديد حروف للمبالغة")

    aggressive_words = [
        "خرا", "حمار", "غبي", "مجنون", "حقير", "كذاب", "فاشل", "خسيس", "حثالة",
        "حرقت", "هدمت", "دمرت", "خربت", "زلط", "زفت", "خايب", "أهبل",
    ]
    aggressive_hits = _match_any(text, aggressive_words)
    if aggressive_hits:
        words = ", ".join(aggressive_hits)
        indicators.append(f"مفردات عدوانية ({words})")

    if not indicators and is_sarcastic:
        indicators.append("تباين دلالي اكتشفه النموذج")

    return indicators

def build_feature_enrichment(
    text: str, confidence: float, is_sarcastic: bool, language: str | None = None
) -> dict[str, object]:
    sarcasm_type = classify_sarcasm_type(text, is_sarcastic)
    target = identify_target(text, is_sarcastic)
    intensity = compute_intensity(text, confidence, is_sarcastic)
    indicators = extract_indicators(text, is_sarcastic)

    if not is_sarcastic:
        explanation = "The model did not cross the sarcasm threshold."
    else:
        type_label = sarcasm_type.value.replace("_", " ")
        target_label = target.replace("_", " ")
        summary = f"Detected {type_label} sarcasm directed at {target_label}."
        if indicators:
            summary += f" Key cues: {', '.join(indicators[:3])}."
        summary += f" Intensity level: {intensity}/5."
        explanation = summary

    return {
        "sarcasm_type": sarcasm_type.value,
        "target": target,
        "intensity": intensity,
        "explanation": explanation,
        "indicators": indicators,
    }
