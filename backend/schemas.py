from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Language(str, Enum):
    ARABIC = "arabic"
    DARIJA = "darija"
    FRENCH = "french"
    ENGLISH = "english"
    UNKNOWN = "unknown"


class LanguageOverride(str, Enum):
    ARABIC = "arabic"
    DARIJA = "darija"
    FRENCH = "french"
    ENGLISH = "english"


class SarcasmType(str, Enum):
    POLARITY_CONTRAST = "polarity_contrast"
    EXAGGERATION = "exaggeration"
    RHETORICAL_QUESTION = "rhetorical_question"
    IRONIC_COMPARISON = "ironic_comparison"
    NONE = "none"


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1)
    context: Optional[str] = None
    language_override: Optional[LanguageOverride] = None


class AnalyzeResponse(BaseModel):
    is_sarcastic: bool
    confidence: float = Field(ge=0.0, le=1.0)
    language: Language
    sarcasm_type: SarcasmType
    target: str
    intensity: int = Field(ge=1, le=5)
    explanation: str
    indicators: list[str]
    threshold: float = Field(ge=0.0, le=1.0)


class AnalyzeFileResponse(AnalyzeResponse):
    extracted_text: str


class HistoryItem(AnalyzeResponse):
    text: str
    timestamp: datetime


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_kind: str


class ErrorResponse(BaseModel):
    error: str
    detail: str


class ThresholdResponse(BaseModel):
    threshold: float = Field(ge=0.0, le=1.0)


class ThresholdUpdateRequest(BaseModel):
    threshold: float = Field(ge=0.0, le=1.0)
