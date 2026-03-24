from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from ...domain.errors import DomainError
from ...infrastructure.config.settings import Settings

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI, settings: Settings) -> None:
    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        logger.warning(
            "Request validation failed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "errors": exc.errors(),
            },
        )
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Validation failed",
                "errors": exc.errors(),
            },
        )

    @app.exception_handler(DomainError)
    async def handle_domain_error(
        request: Request,
        exc: DomainError,
    ) -> JSONResponse:
        logger.warning(
            "Domain error",
            extra={
                "method": request.method,
                "path": request.url.path,
                "error_type": exc.__class__.__name__,
            },
        )
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(Exception)
    async def handle_unexpected_error(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.exception(
            "Unhandled application error",
            extra={
                "method": request.method,
                "path": request.url.path,
                "error_type": exc.__class__.__name__,
            },
        )
        detail = (
            str(exc)
            if settings.ENVIRONMENT in {"development", "test"}
            else "Internal server error"
        )
        return JSONResponse(status_code=500, content={"detail": detail})
