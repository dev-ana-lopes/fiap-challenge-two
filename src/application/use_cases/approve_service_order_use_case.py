from uuid import UUID

from ...domain.repositories import CustomerRepository
from ...domain.repositories import ServiceOrderRepository
from ...domain.enums import ServiceOrderStatus
from ...infrastructure.email.smtp_client import SmtpEmailSender


class ApproveServiceOrderUseCase:

    def __init__(
        self,
        service_order_repo: ServiceOrderRepository,
        customer_repo: CustomerRepository,
        email_sender: SmtpEmailSender,
    ):
        self.service_order_repo = service_order_repo
        self.customer_repo = customer_repo
        self.email_sender = email_sender

    async def execute(self, service_order_id: UUID, approved: bool) -> bool:
        service_order = await self.service_order_repo.get_by_id(
            service_order_id
        )

        if service_order is None:
            return False

        customer = await self.customer_repo.get_by_id(
            service_order.customer_id)
        customer_email = customer.email if customer is not None else ""

        if approved:
            await self.service_order_repo.update_status(
                service_order_id, ServiceOrderStatus.IN_PROGRESS
            )
            await self.service_order_repo.set_started_at(service_order_id)
            await self.email_sender.send_status_changed(
                customer_email,
                str(service_order_id),
                ServiceOrderStatus.IN_PROGRESS.value,
            )
            return True

        await self.service_order_repo.update_status(
            service_order_id, ServiceOrderStatus.CANCELLED
        )
        if customer is not None:
            await self.email_sender.send_status_changed(
                customer_email,
                str(service_order_id),
                ServiceOrderStatus.CANCELLED.value,
            )
        return True
