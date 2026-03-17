from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from ....domain.errors import (
    ApprovalActionAlreadyProcessedError,
    InvalidServiceOrderTransitionError,
    ServiceOrderNotFoundError,
)
from ....application.dto.create_service_order_dto import CreateServiceOrderDTO
from ....application.use_cases.approve_service_order_use_case import (
    ApproveServiceOrderUseCase,
)
from ....application.use_cases.create_service_order_use_case import (
    CreateServiceOrderUseCase,
)
from ....application.use_cases.get_service_order_status_use_case import (
    GetServiceOrderStatusUseCase,
)
from ....application.use_cases.list_active_service_orders_use_case import (
    ListActiveServiceOrdersUseCase,
)
from ....application.use_cases.update_service_order_status_use_case import (
    UpdateServiceOrderStatusUseCase,
)
from ....presentation.dependencies.auth_dependencies import get_current_user
from ....presentation.dependencies.db_dependencies import (
    get_approval_token_service,
    get_catalog_service_repository,
    get_customer_repository,
    get_email_sender,
    get_inventory_part_repository,
    get_part_item_repository,
    get_service_item_repository,
    get_service_order_repository,
    get_vehicle_repository,
)
from ....presentation.schemas.service_order_schema import (
    ApproveServiceOrderRequest,
    ApproveServiceOrderResponse,
    CreateServiceOrderRequest,
    CreateServiceOrderResponse,
    PartItemResponse,
    ServiceItemResponse,
    ServiceOrderResponse,
    ServiceOrderStatusResponse,
    UpdateServiceOrderStatusRequest,
)

router = APIRouter(
    prefix="/service-orders",
    tags=["service-orders"],
    dependencies=[Depends(get_current_user)],
)

CustomerRepo = Annotated[object, Depends(get_customer_repository)]
CatalogServiceRepo = Annotated[object, Depends(get_catalog_service_repository)]
VehicleRepo = Annotated[object, Depends(get_vehicle_repository)]
ServiceOrderRepo = Annotated[object, Depends(get_service_order_repository)]
ServiceItemRepo = Annotated[object, Depends(get_service_item_repository)]
PartItemRepo = Annotated[object, Depends(get_part_item_repository)]
InventoryPartRepo = Annotated[object, Depends(get_inventory_part_repository)]
EmailSender = Annotated[object, Depends(get_email_sender)]
ApprovalTokenSvc = Annotated[object, Depends(get_approval_token_service)]


@router.post("")
async def create_service_order(
    request: CreateServiceOrderRequest,
    customer_repo: CustomerRepo,
    vehicle_repo: VehicleRepo,
    service_order_repo: ServiceOrderRepo,
    service_item_repo: ServiceItemRepo,
    part_item_repo: PartItemRepo,
    catalog_service_repo: CatalogServiceRepo,
    inventory_part_repo: InventoryPartRepo,
    email_sender: EmailSender,
    approval_token_service: ApprovalTokenSvc,
) -> CreateServiceOrderResponse:
    if not request.service_ids and not request.services:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Either services or service_ids must be provided",
        )
    dto = CreateServiceOrderDTO(
        customer_name=request.customer_name,
        customer_cpf_cnpj=request.customer_cpf_cnpj,
        customer_email=request.customer_email,
        customer_phone=request.customer_phone,
        vehicle_brand=request.vehicle_brand,
        vehicle_model=request.vehicle_model,
        vehicle_year=request.vehicle_year,
        vehicle_plate=request.vehicle_plate,
        services=(
            [
                {"description": s.description, "price": s.price}
                for s in (request.services or [])
            ]
            if request.services is not None
            else None
        ),
        parts=(
            [
                {"name": p.name, "price": p.price, "quantity": p.quantity}
                for p in (request.parts or [])
            ]
            if request.parts is not None
            else None
        ),
        service_ids=request.service_ids,
        part_refs=(
            [
                {"part_id": p.part_id, "quantity": p.quantity}
                for p in (request.part_refs or [])
            ]
            if request.part_refs is not None
            else None
        ),
    )

    use_case = CreateServiceOrderUseCase(
        customer_repo,
        vehicle_repo,
        service_order_repo,
        service_item_repo,
        part_item_repo,
        catalog_service_repo,
        inventory_part_repo,
        email_sender,
        approval_token_service,
    )

    try:
        service_order_id = await use_case.execute(dto)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    return CreateServiceOrderResponse(service_order_id=service_order_id)


@router.get("/{id}/status")
async def get_service_order_status(
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


@router.post("/{id}/approval")
async def approve_service_order(
    id: UUID,
    request: ApproveServiceOrderRequest,
    customer_repo: CustomerRepo,
    service_order_repo: ServiceOrderRepo,
    email_sender: EmailSender,
) -> ApproveServiceOrderResponse:
    use_case = ApproveServiceOrderUseCase(
        service_order_repo, customer_repo, email_sender
    )
    try:
        updated_status = await use_case.execute(id, request.approved)
    except ServiceOrderNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service order not found",
        ) from exc
    except ApprovalActionAlreadyProcessedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return ApproveServiceOrderResponse(
        status=updated_status.value,
        decision="APPROVED" if request.approved else "REJECTED",
    )


@router.get("")
async def list_service_orders(
    service_order_repo: ServiceOrderRepo,
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
    customer_repo: CustomerRepo,
    service_order_repo: ServiceOrderRepo,
    email_sender: EmailSender,
    approval_token_service: ApprovalTokenSvc,
) -> dict:
    use_case = UpdateServiceOrderStatusUseCase(
        service_order_repo,
        customer_repo,
        email_sender,
        approval_token_service,
    )
    try:
        await use_case.execute(id, request.status)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except ServiceOrderNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service order not found",
        ) from exc
    except InvalidServiceOrderTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return {"success": True}
