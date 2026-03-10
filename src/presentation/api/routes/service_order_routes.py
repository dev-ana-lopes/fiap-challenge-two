from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from ....application.dto.create_service_order_dto import CreateServiceOrderDTO
from ....application.use_cases.approve_service_order_use_case import (
    ApproveServiceOrderUseCase
)
from ....application.use_cases.create_service_order_use_case import (
    CreateServiceOrderUseCase
)
from ....application.use_cases.get_service_order_status_use_case import (
    GetServiceOrderStatusUseCase
)
from ....application.use_cases.list_active_service_orders_use_case import (
    ListActiveServiceOrdersUseCase)
from ....application.use_cases.update_service_order_status_use_case import (
    UpdateServiceOrderStatusUseCase)
from ....presentation.dependencies.auth_dependencies import get_current_user
from ....presentation.dependencies.db_dependencies import (
    get_customer_repository,
    get_email_sender,
    get_part_item_repository,
    get_service_item_repository,
    get_service_order_repository,
    get_vehicle_repository
)
from ....presentation.schemas.service_order_schema import (
    ApproveServiceOrderRequest,
    CreateServiceOrderRequest,
    CreateServiceOrderResponse,
    PartItemResponse,
    ServiceItemResponse,
    ServiceOrderResponse,
    ServiceOrderStatusResponse,
    UpdateServiceOrderStatusRequest
)

router = APIRouter(prefix="/service-orders", tags=["service-orders"])

CurrentUser = Annotated[dict, Depends(get_current_user)]
CustomerRepo = Annotated[object, Depends(get_customer_repository)]
VehicleRepo = Annotated[object, Depends(get_vehicle_repository)]
ServiceOrderRepo = Annotated[object, Depends(get_service_order_repository)]
ServiceItemRepo = Annotated[object, Depends(get_service_item_repository)]
PartItemRepo = Annotated[object, Depends(get_part_item_repository)]
EmailSender = Annotated[object, Depends(get_email_sender)]


@router.post("")
async def create_service_order(
    request: CreateServiceOrderRequest,
    current_user=CurrentUser,
    customer_repo=CustomerRepo,
    vehicle_repo=VehicleRepo,
    service_order_repo=ServiceOrderRepo,
    service_item_repo=ServiceItemRepo,
    part_item_repo=PartItemRepo,
    email_sender=EmailSender,
) -> CreateServiceOrderResponse:
    dto = CreateServiceOrderDTO(
        customer_name=request.customer_name,
        customer_email=request.customer_email,
        customer_phone=request.customer_phone,
        vehicle_brand=request.vehicle_brand,
        vehicle_model=request.vehicle_model,
        vehicle_year=request.vehicle_year,
        vehicle_plate=request.vehicle_plate,
        services=[
            {"description": s.description, "price": s.price}
            for s in request.services
        ],
        parts=[
            {"name": p.name, "price": p.price, "quantity": p.quantity}
            for p in request.parts
        ],
    )

    use_case = CreateServiceOrderUseCase(
        customer_repo,
        vehicle_repo,
        service_order_repo,
        service_item_repo,
        part_item_repo,
        email_sender,
    )

    service_order_id = await use_case.execute(dto)
    return CreateServiceOrderResponse(service_order_id=service_order_id)


@router.get("/{id}/status")
async def get_service_order_status(
    id: UUID,
    current_user=CurrentUser,
    service_order_repo=ServiceOrderRepo,
) -> ServiceOrderStatusResponse:
    use_case = GetServiceOrderStatusUseCase(service_order_repo)
    order_status = await use_case.execute(id)

    if order_status is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service order not found",
        )

    return ServiceOrderStatusResponse(status=order_status)


@router.post("/{id}/approval")
async def approve_service_order(
    id: UUID,
    request: ApproveServiceOrderRequest,
    current_user=CurrentUser,
    customer_repo=CustomerRepo,
    service_order_repo=ServiceOrderRepo,
    email_sender=EmailSender,
) -> dict:
    use_case = ApproveServiceOrderUseCase(
        service_order_repo, customer_repo, email_sender
    )
    result = await use_case.execute(id, request.approved)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service order not found",
        )

    return {"success": True}


@router.get("")
async def list_service_orders(
    current_user=CurrentUser,
    service_order_repo=ServiceOrderRepo,
) -> list[ServiceOrderResponse]:
    use_case = ListActiveServiceOrdersUseCase(service_order_repo)
    service_orders = await use_case.execute()

    response = []
    for so in service_orders:
        service_items = [
            ServiceItemResponse(
                id=str(s.id),
                description=s.description,
                price=s.price,
            )
            for s in so.service_items
        ]
        part_items = [
            PartItemResponse(
                id=str(p.id),
                name=p.name,
                price=p.price,
                quantity=p.quantity,
            )
            for p in so.part_items
        ]

        response.append(
            ServiceOrderResponse(
                id=str(so.id),
                customer_id=str(so.customer_id),
                vehicle_id=str(so.vehicle_id),
                status=so.status.value,
                created_at=so.created_at.isoformat(),
                service_items=service_items,
                part_items=part_items,
            )
        )

    return response


@router.patch("/{id}/status")
async def update_service_order_status(
    id: UUID,
    request: UpdateServiceOrderStatusRequest,
    current_user=CurrentUser,
    customer_repo=CustomerRepo,
    service_order_repo=ServiceOrderRepo,
    email_sender=EmailSender,
) -> dict:
    use_case = UpdateServiceOrderStatusUseCase(
        service_order_repo, customer_repo, email_sender
    )
    result = await use_case.execute(id, request.status)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to update service order status",
        )

    return {"success": True}
