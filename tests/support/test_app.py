from fastapi import FastAPI

from src.presentation.api.routes import (
    auth_router,
    catalog_router,
    customer_router,
    metrics_router,
    public_router,
    service_order_router,
    vehicle_router,
)


def create_test_app() -> FastAPI:
    app = FastAPI(title="Service Order API Test App")
    app.include_router(auth_router)
    app.include_router(customer_router)
    app.include_router(vehicle_router)
    app.include_router(catalog_router)
    app.include_router(metrics_router)
    app.include_router(public_router)
    app.include_router(service_order_router)
    return app
