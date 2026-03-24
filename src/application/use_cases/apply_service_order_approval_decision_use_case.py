from __future__ import annotations

import logging
from uuid import UUID

from ...domain.enums import ServiceOrderStatus
from ...domain.errors import (
    ApprovalActionAlreadyProcessedError,
    ServiceOrderNotFoundError,
)
from ...domain.repositories import CustomerRepository, ServiceOrderRepository
from ...domain.services import EmailSender
from ...domain.time import utcnow

logger = logging.getLogger(__name__)


class ApplyServiceOrderApprovalDecisionUseCase:
    def __init__(
        self,
        service_order_repo: ServiceOrderRepository,
        customer_repo: CustomerRepository,
        email_sender: EmailSender,
    ):
        self.service_order_repo = service_order_repo
        self.customer_repo = customer_repo
        self.email_sender = email_sender

    async def execute(
        self,
        service_order_id: UUID,
        approved: bool,
        rejection_reason: str | None = None,
    ) -> ServiceOrderStatus:
        service_order = await self.service_order_repo.get_by_id(service_order_id)
        if service_order is None:
            raise ServiceOrderNotFoundError(service_order_id)

        if service_order.status != ServiceOrderStatus.WAITING_APPROVAL:
            raise ApprovalActionAlreadyProcessedError(service_order.status)

        new_status = service_order.apply_budget_decision(
            approved,
            changed_at=utcnow(),
            rejection_reason=rejection_reason,
        )
        await self.service_order_repo.update(service_order)

        customer = await self.customer_repo.get_by_id(service_order.customer_id)
        if customer is not None:
            logger.info(
                "Service order %s %s by customer approval flow",
                service_order_id,
                "approved" if approved else "rejected",
            )
            await self.email_sender.send_status_changed(
                customer.email,
                str(service_order_id),
                new_status.value,
            )

        return new_status
