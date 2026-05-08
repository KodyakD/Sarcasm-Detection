from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")
    model_dir: Path = Field(default=Path("./models"), alias="MODEL_DIR")
    marbert_model_name: str = Field(
        default="UBC-NLP/MARBERTv2", alias="MARBERT_MODEL_NAME"
    )
    marbert_sarcasm_model_dir: Path = Field(
        # Default now points to the higher-performing marbert3 checkpoint.
        default=Path("marbert3/marbert-sarcasm-arabic"),
        alias="MARBERT_SARCASM_MODEL_DIR",
    )
    # Notes: To switch which local sarcasm checkpoint the backend loads, set the
    # `MARBERT_SARCASM_MODEL_DIR` environment variable or update this default.
    # Examples (relative to project root):
    # - Path("marbert3/marbert-sarcasm-arabic") -> use the local marbert3 checkpoint
    # - Path("marbert_sarcasm_model") -> use a custom folder named `marbert_sarcasm_model`
    # - Path("../marbert3/marbert-sarcasm-arabic") -> older marbert3 checkpoint
    # - Path("../marbert2/marbert-sarcasm") -> legacy marbert2 checkpoint
    # You can also point to an HF identifier string via `MARBERT_MODEL_NAME` for
    # remote model loading (the code prefers local HF-style folders first).
    dziribert_model_name: str = Field(
        default="alger-ia/dziribert", alias="DZIRIBERT_MODEL_NAME"
    )
    model_max_length: int = Field(default=128, alias="MODEL_MAX_LENGTH")
    app_env: str = Field(default="development", alias="APP_ENV")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
