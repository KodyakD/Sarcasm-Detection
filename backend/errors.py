from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(self, error: str, detail: str, status_code: int) -> None:
        self.error = error
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


def app_error_response(error: str, detail: str, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code, content={"error": error, "detail": detail}
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return app_error_response(exc.error, exc.detail, exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422, content={"detail": jsonable_encoder(exc.errors())}
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
        return app_error_response("internal_error", str(exc), 500)
