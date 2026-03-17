from fastapi import FastAPI

from src.presentation.api.routes import public_router, service_order_router


def create_test_app() -> FastAPI:
    app = FastAPI(title="Service Order API Test App")
    app.include_router(public_router)
    app.include_router(service_order_router)
    return app
