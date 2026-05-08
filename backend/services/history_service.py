from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from typing import Deque

try:
    from ..schemas import AnalyzeResponse, HistoryItem
except ImportError:  # pragma: no cover - supports top-level test imports
    from schemas import AnalyzeResponse, HistoryItem


class HistoryStore:
    def __init__(self, max_items: int = 10) -> None:
        self._items: Deque[HistoryItem] = deque(maxlen=max_items)

    def add(self, text: str, result: AnalyzeResponse) -> None:
        self._items.appendleft(
            HistoryItem(
                text=text,
                timestamp=datetime.now(timezone.utc),
                **result.model_dump(),
            )
        )

    def list(self) -> list[HistoryItem]:
        return list(self._items)
