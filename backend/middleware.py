"""Global exception handling and structured API error responses."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("streamspeech")


def _error_payload(
    *,
    status_code: int,
    message: str,
    error_type: str,
    details: Any = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "success": False,
        "error": {
            "type": error_type,
            "message": message,
            "status_code": status_code,
        },
    }
    if details is not None:
        body["error"]["details"] = details
    return body


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        detail = exc.detail
        message = detail if isinstance(detail, str) else str(detail)
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(
                status_code=exc.status_code,
                message=message,
                error_type="http_error",
                details=detail if not isinstance(detail, str) else None,
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def starlette_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(
                status_code=exc.status_code,
                message=str(exc.detail),
                error_type="http_error",
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=_error_payload(
                status_code=422,
                message="Request validation failed",
                error_type="validation_error",
                details=exc.errors(),
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled server error")
        return JSONResponse(
            status_code=500,
            content=_error_payload(
                status_code=500,
                message="Internal server error",
                error_type="internal_error",
            ),
        )
