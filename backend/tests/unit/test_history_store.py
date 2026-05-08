from __future__ import annotations

from schemas import AnalyzeResponse, Language, SarcasmType, TargetType
from services.history_service import HistoryStore


def _sample_response(index: int) -> AnalyzeResponse:
    return AnalyzeResponse(
        is_sarcastic=index % 2 == 0,
        confidence=0.6,
        language=Language.ENGLISH,
        sarcasm_type=SarcasmType.NONE,
        target=TargetType.NONE,
        intensity=1,
        explanation="ok",
        indicators=[],
    )


def test_history_store_keeps_max_items() -> None:
    store = HistoryStore(max_items=3)
    for i in range(5):
        store.add(f"text-{i}", _sample_response(i))

    history = store.list()
    assert len(history) == 3
    assert history[0].text == "text-4"
    assert history[-1].text == "text-2"
