import logging
from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .infrastructure.config.settings import get_settings
from .infrastructure.logging import configure_logging
from .presentation.api.exception_handlers import register_exception_handlers
from .presentation.api.routes import (
    auth_router,
    catalog_router,
    customer_router,
    health_router,
    metrics_router,
    public_router,
    service_order_router,
    vehicle_router,
)
from .presentation.dependencies.db_dependencies import (
    get_database_session,
    init_database,
)

settings = get_settings()
configure_logging(settings)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database(settings)
    yield
    await get_database_session(settings).dispose()


app = FastAPI(
    title="Tech Challenge Workshop Service Orders API",
    description=(
        "Backend monolith for customers, vehicles, services, parts and "
        "mechanical workshop service orders."
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

if settings.TRUSTED_HOSTS and settings.TRUSTED_HOSTS != ["*"]:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.TRUSTED_HOSTS)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app, settings)


@app.middleware("http")
async def add_operational_headers_and_logs(request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    started_at = perf_counter()
    response = await call_next(request)
    duration_ms = round((perf_counter() - started_at) * 1000, 2)

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    logger.info(
        "Request completed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "client": request.client.host if request.client else None,
        },
    )
    return response


app.include_router(health_router)
app.include_router(auth_router)
app.include_router(public_router)
app.include_router(service_order_router)
app.include_router(customer_router)
app.include_router(vehicle_router)
app.include_router(catalog_router)
app.include_router(metrics_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
