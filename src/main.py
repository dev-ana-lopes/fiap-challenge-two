from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .infrastructure.config.settings import get_settings
from .infrastructure.database.session import DatabaseSession
from .presentation.api.routes import (
    auth_router,
    catalog_router,
    customer_router,
    metrics_router,
    public_router,
    service_order_router,
    vehicle_router,
)
from .presentation.dependencies.db_dependencies import init_database


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database(settings)
    yield
    db = DatabaseSession(settings)
    await db.dispose()


app = FastAPI(
    title="Service Order Management API",
    description="API for managing mechanical workshop service orders",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(public_router)
app.include_router(service_order_router)
app.include_router(customer_router)
app.include_router(vehicle_router)
app.include_router(catalog_router)
app.include_router(metrics_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app, host="0.0.0.0", port=8000, reload=True
    )
