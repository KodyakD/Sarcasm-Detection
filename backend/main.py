from __future__ import annotations

import logging
import time

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

try:
    from .errors import AppError, register_exception_handlers
    from .inference import (
        get_model_runtime_kind,
        get_threshold,
        is_model_loaded,
        set_threshold,
        startup_load_models,
    )
    from .schemas import (
        AnalyzeFileResponse,
        AnalyzeRequest,
        AnalyzeResponse,
        HealthResponse,
        HistoryItem,
        LanguageOverride,
        ThresholdResponse,
        ThresholdUpdateRequest,
    )
    from .services.analyze_service import analyze_text
    from .services.file_extraction_service import extract_text
    from .services.history_service import HistoryStore
except ImportError:  # pragma: no cover - supports top-level test imports
    from errors import AppError, register_exception_handlers
    from inference import (
        get_model_runtime_kind,
        get_threshold,
        is_model_loaded,
        set_threshold,
        startup_load_models,
    )
    from schemas import (
        AnalyzeFileResponse,
        AnalyzeRequest,
        AnalyzeResponse,
        HealthResponse,
        HistoryItem,
        LanguageOverride,
        ThresholdResponse,
        ThresholdUpdateRequest,
    )
    from services.analyze_service import analyze_text
    from services.file_extraction_service import extract_text
    from services.history_service import HistoryStore


_history = HistoryStore(max_items=10)
logger = logging.getLogger("sarcasm-api")


if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s"
    )


def create_app() -> FastAPI:
    app = FastAPI(title="Intelligent Sarcasm & Irony Detection API", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    @app.middleware("http")
    async def request_timing_middleware(request: Request, call_next):
        started_at = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - started_at) * 1000.0
        response.headers["X-Process-Time"] = f"{elapsed_ms:.3f}ms"
        logger.info(
            "%s %s -> %s in %.3fms",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )
        return response

    @app.on_event("startup")
    async def startup_event() -> None:
        startup_load_models()

    @app.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            model_loaded=is_model_loaded(),
            model_kind=get_model_runtime_kind(),
        )

    @app.post("/analyze", response_model=AnalyzeResponse)
    async def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
        if not payload.text.strip():
            raise AppError("bad_request", "Text cannot be empty", 400)

        response = analyze_text(payload.text, payload.language_override)
        _history.add(payload.text, response)
        return response

    @app.post("/analyze-file", response_model=AnalyzeFileResponse)
    async def analyze_file(
        file: UploadFile = File(...),
        context: str | None = Form(default=None),
        language_override: str | None = Form(default=None),
    ) -> AnalyzeFileResponse:
        extracted_text = await extract_text(file)

        override_value = None
        if language_override:
            try:
                override_value = LanguageOverride(language_override)
            except ValueError as exc:
                raise AppError(
                    "validation_error", "Invalid language_override value", 422
                ) from exc

        _ = context  # Reserved for future enrichment prompt context.
        response = analyze_text(extracted_text, override_value)
        _history.add(extracted_text, response)
        return AnalyzeFileResponse(
            **response.model_dump(), extracted_text=extracted_text
        )

    @app.get("/history", response_model=list[HistoryItem])
    async def history() -> list[HistoryItem]:
        return _history.list()

    @app.get("/threshold", response_model=ThresholdResponse)
    async def get_current_threshold() -> ThresholdResponse:
        return ThresholdResponse(threshold=get_threshold())

    @app.post("/threshold", response_model=ThresholdResponse)
    async def update_threshold(payload: ThresholdUpdateRequest) -> ThresholdResponse:
        try:
            result = set_threshold(payload.threshold)
            return ThresholdResponse(threshold=float(result["threshold"]))
        except ValueError as exc:
            raise AppError("validation_error", str(exc), 422) from exc
        except RuntimeError as exc:
            raise AppError("internal_error", str(exc), 500) from exc

    return app


app = create_app()
