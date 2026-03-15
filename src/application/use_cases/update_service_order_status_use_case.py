from uuid import UUID

from ...domain.repositories import CustomerRepository
from ...domain.repositories import ServiceOrderRepository
from ...domain.enums import ServiceOrderStatus
from ...infrastructure.email.smtp_client import SmtpEmailSender


class UpdateServiceOrderStatusUseCase:

    def __init__(
        self,
        service_order_repo: ServiceOrderRepository,
        customer_repo: CustomerRepository,
        email_sender: SmtpEmailSender,
    ):
        self.service_order_repo = service_order_repo
        self.customer_repo = customer_repo
        self.email_sender = email_sender

    async def execute(self, service_order_id: UUID, status: str) -> bool:
        try:
            status_enum = ServiceOrderStatus(status)
        except ValueError:
            return False

        service_order = await self.service_order_repo.get_by_id(
            service_order_id
        )

        if service_order is None:
            return False

        await self.service_order_repo.update_status(
            service_order_id, status_enum
        )
        if status_enum == ServiceOrderStatus.IN_PROGRESS:
            await self.service_order_repo.set_started_at(service_order_id)
        if status_enum == ServiceOrderStatus.FINISHED:
            await self.service_order_repo.set_finished_at(service_order_id)

        customer = await self.customer_repo.get_by_id(
            service_order.customer_id
        )
        if customer is not None:
            await self.email_sender.send_status_changed(
                customer.email,
                str(service_order_id),
                status_enum.value,
            )

        return True
