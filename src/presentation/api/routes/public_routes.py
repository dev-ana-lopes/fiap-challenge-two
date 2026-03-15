from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from ....application.use_cases.get_service_order_status_use_case import (
    GetServiceOrderStatusUseCase,
)
from ....presentation.dependencies.db_dependencies import get_service_order_repository
from ....presentation.schemas.service_order_schema import ServiceOrderStatusResponse

router = APIRouter(prefix="/public", tags=["public"])

ServiceOrderRepo = Annotated[object, Depends(get_service_order_repository)]


@router.get("/service-orders/{id}/status")
async def get_public_service_order_status(
    id: UUID,
    service_order_repo: ServiceOrderRepo,
) -> ServiceOrderStatusResponse:
    use_case = GetServiceOrderStatusUseCase(service_order_repo)
    order_status = await use_case.execute(id)

    if order_status is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service order not found",
        )

    return ServiceOrderStatusResponse(status=order_status)

