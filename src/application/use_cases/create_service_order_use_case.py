from datetime import datetime
from uuid import uuid4

from ..dto.create_service_order_dto import CreateServiceOrderDTO
from ...domain.entities import (
    Customer,
    PartItem,
    ServiceItem,
    ServiceOrder,
    Vehicle,
)
from ...domain.enums import ServiceOrderStatus
from ...domain.repositories import (
    CustomerRepository,
    VehicleRepository,
    ServiceOrderRepository,
    ServiceItemRepository,
    PartItemRepository,
)
from ...infrastructure.email.smtp_client import SmtpEmailSender


class CreateServiceOrderUseCase:

    def __init__(
        self,
        customer_repo: CustomerRepository,
        vehicle_repo: VehicleRepository,
        service_order_repo: ServiceOrderRepository,
        service_item_repo: ServiceItemRepository,
        part_item_repo: PartItemRepository,
        email_sender: SmtpEmailSender,
    ):
        self.customer_repo = customer_repo
        self.vehicle_repo = vehicle_repo
        self.service_order_repo = service_order_repo
        self.service_item_repo = service_item_repo
        self.part_item_repo = part_item_repo
        self.email_sender = email_sender

    async def execute(self, dto: CreateServiceOrderDTO) -> str:
        customer_id = uuid4()
        customer = Customer(
            id=customer_id,
            name=dto.customer_name,
            email=dto.customer_email,
            phone=dto.customer_phone,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        await self.customer_repo.save(customer)

        vehicle_id = uuid4()
        vehicle = Vehicle(
            id=vehicle_id,
            customer_id=customer_id,
            brand=dto.vehicle_brand,
            model=dto.vehicle_model,
            year=dto.vehicle_year,
            plate=dto.vehicle_plate,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        await self.vehicle_repo.save(vehicle)

        service_order_id = uuid4()
        service_items = [
            ServiceItem(
                id=uuid4(),
                service_order_id=service_order_id,
                description=service["description"],
                price=float(service["price"]),
                created_at=datetime.utcnow(),
            )
            for service in dto.services
        ]

        part_items = [
            PartItem(
                id=uuid4(),
                service_order_id=service_order_id,
                name=part["name"],
                price=float(part["price"]),
                quantity=int(part["quantity"]),
                created_at=datetime.utcnow(),
            )
            for part in dto.parts
        ]

        service_order = ServiceOrder(
            id=service_order_id,
            customer_id=customer_id,
            vehicle_id=vehicle_id,
            status=ServiceOrderStatus.RECEIVED,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            service_items=service_items,
            part_items=part_items,
        )

        await self.service_order_repo.save(service_order)

        await self.email_sender.send_service_order_created(
            customer.email, str(service_order_id)
        )

        return str(service_order_id)
