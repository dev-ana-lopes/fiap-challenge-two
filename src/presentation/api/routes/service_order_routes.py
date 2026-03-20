from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from ....application.dto.create_service_order_dto import CreateServiceOrderDTO
from ....application.use_cases.approve_service_order_use_case import (
    ApproveServiceOrderUseCase,
)
from ....application.use_cases.create_service_order_use_case import (
    CreateServiceOrderUseCase,
)
from ....application.use_cases.get_service_order_details_use_case import (
    GetServiceOrderDetailsUseCase,
)
from ....application.use_cases.get_service_order_status_use_case import (
    GetServiceOrderStatusUseCase,
)
from ....application.use_cases.list_active_service_orders_use_case import (
    ListActiveServiceOrdersUseCase,
)
from ....application.use_cases.list_service_orders_use_case import (
    ListServiceOrdersUseCase,
)
from ....application.use_cases.update_service_order_status_use_case import (
    UpdateServiceOrderStatusUseCase,
)
from ....domain.errors import (
    ApprovalActionAlreadyProcessedError,
    InvalidServiceOrderTransitionError,
    ServiceOrderNotFoundError,
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


def _to_service_order_response(service_order) -> ServiceOrderResponse:
    return ServiceOrderResponse(
        id=str(service_order.id),
        customer_id=str(service_order.customer_id),
        vehicle_id=str(service_order.vehicle_id),
        status=service_order.status.value,
        created_at=service_order.created_at.isoformat(),
        updated_at=service_order.updated_at.isoformat(),
        started_at=(
            service_order.started_at.isoformat()
            if service_order.started_at is not None
            else None
        ),
        finished_at=(
            service_order.finished_at.isoformat()
            if service_order.finished_at is not None
            else None
        ),
        budget_total=service_order.budget_total,
        approval_decision=(
            service_order.approval_decision.value
            if service_order.approval_decision is not None
            else None
        ),
        approval_decision_at=(
            service_order.approval_decision_at.isoformat()
            if service_order.approval_decision_at is not None
            else None
        ),
        rejection_reason=service_order.rejection_reason,
        service_items=[
            ServiceItemResponse(
                id=str(item.id),
                description=item.description,
                price=item.price,
            )
            for item in service_order.service_items
        ],
        part_items=[
            PartItemResponse(
                id=str(item.id),
                name=item.name,
                price=item.price,
                quantity=item.quantity,
            )
            for item in service_order.part_items
        ],
    )


@router.post("", status_code=status.HTTP_201_CREATED)
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
        customer_id=request.customer_id,
        vehicle_id=request.vehicle_id,
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
    except LookupError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    return CreateServiceOrderResponse(service_order_id=service_order_id)


@router.get("/active")
async def list_active_service_orders(
    service_order_repo: ServiceOrderRepo,
) -> list[ServiceOrderResponse]:
    use_case = ListActiveServiceOrdersUseCase(service_order_repo)
    return [
        _to_service_order_response(service_order)
        for service_order in await use_case.execute()
    ]


@router.get("/{id}/status")
async def get_service_order_status(
    id: UUID,
    service_order_repo: ServiceOrderRepo,
) -> ServiceOrderStatusResponse:
    use_case = GetServiceOrderStatusUseCase(service_order_repo)
    order_status = await use_case.execute(id)
    detail_use_case = GetServiceOrderDetailsUseCase(service_order_repo)
    service_order = await detail_use_case.execute(id)

    if order_status is None or service_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service order not found",
        )

    return ServiceOrderStatusResponse(
        status=order_status,
        approval_decision=(
            service_order.approval_decision.value
            if service_order.approval_decision is not None
            else None
        ),
        rejection_reason=service_order.rejection_reason,
    )


@router.get("/{id}")
async def get_service_order(
    id: UUID,
    service_order_repo: ServiceOrderRepo,
) -> ServiceOrderResponse:
    use_case = GetServiceOrderDetailsUseCase(service_order_repo)
    service_order = await use_case.execute(id)
    if service_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service order not found",
        )
    return _to_service_order_response(service_order)


@router.get("")
async def list_service_orders(
    service_order_repo: ServiceOrderRepo,
) -> list[ServiceOrderResponse]:
    use_case = ListServiceOrdersUseCase(service_order_repo)
    return [
        _to_service_order_response(service_order)
        for service_order in await use_case.execute()
    ]


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
        updated_status = await use_case.execute(
            id,
            request.approved,
            request.rejection_reason,
        )
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
        rejection_reason=request.rejection_reason if not request.approved else None,
    )


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
