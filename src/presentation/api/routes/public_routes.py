from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from ....application.use_cases.approve_service_order_by_token_use_case import (
    ApproveServiceOrderByTokenUseCase,
)
from ....application.use_cases.apply_service_order_approval_decision_use_case import (
    ApplyServiceOrderApprovalDecisionUseCase,
)
from ....domain.errors import (
    ApprovalActionAlreadyProcessedError,
    ApprovalTokenMismatchError,
    ExpiredApprovalTokenError,
    InvalidApprovalTokenError,
    ServiceOrderNotFoundError,
)
from ....application.use_cases.get_service_order_status_use_case import (
    GetServiceOrderStatusUseCase,
)
from ....presentation.dependencies.db_dependencies import (
    get_approval_token_service,
    get_customer_repository,
    get_email_sender,
    get_service_order_repository,
)
from ....presentation.schemas.service_order_schema import (
    ApproveServiceOrderResponse,
    ServiceOrderStatusResponse,
)

router = APIRouter(prefix="/public", tags=["public"])

ServiceOrderRepo = Annotated[object, Depends(get_service_order_repository)]
CustomerRepo = Annotated[object, Depends(get_customer_repository)]
EmailSender = Annotated[object, Depends(get_email_sender)]
ApprovalTokenSvc = Annotated[object, Depends(get_approval_token_service)]


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


@router.get("/service-orders/{id}/approval")
async def approve_service_order_from_email_link(
    id: UUID,
    token: str,
    service_order_repo: ServiceOrderRepo,
    customer_repo: CustomerRepo,
    email_sender: EmailSender,
    approval_token_service: ApprovalTokenSvc,
) -> ApproveServiceOrderResponse:
    apply_decision_use_case = ApplyServiceOrderApprovalDecisionUseCase(
        service_order_repo,
        customer_repo,
        email_sender,
    )
    use_case = ApproveServiceOrderByTokenUseCase(
        approval_token_service,
        apply_decision_use_case,
    )

    try:
        updated_status = await use_case.execute(id, token)
    except InvalidApprovalTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except ExpiredApprovalTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail=str(exc),
        ) from exc
    except ApprovalTokenMismatchError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
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
        decision=("APPROVED" if updated_status.value == "IN_PROGRESS" else "REJECTED"),
    )
