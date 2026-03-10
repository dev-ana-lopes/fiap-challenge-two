import pytest
from datetime import datetime
from uuid import uuid4

from src.application.dto.create_service_order_dto import (
    CreateServiceOrderDTO,
)
from src.application.use_cases.create_service_order_use_case import (
    CreateServiceOrderUseCase,
)
from src.domain.entities import Customer, ServiceOrder
from src.domain.enums import ServiceOrderStatus
from src.domain.repositories import (
    CustomerRepository,
    VehicleRepository,
    ServiceOrderRepository,
    ServiceItemRepository,
    PartItemRepository,
)


class MockCustomerRepository(CustomerRepository):
    def __init__(self):
        self.customers = {}

    async def save(self, customer: Customer) -> None:
        self.customers[customer.id] = customer

    async def get_by_id(self, customer_id) -> Customer | None:
        return self.customers.get(customer_id)

    async def get_by_email(self, email: str) -> Customer | None:
        for customer in self.customers.values():
            if customer.email == email:
                return customer
        return None


class MockVehicleRepository(VehicleRepository):
    def __init__(self):
        self.vehicles = {}

    async def save(self, vehicle) -> None:
        self.vehicles[vehicle.id] = vehicle

    async def get_by_id(self, vehicle_id) -> None:
        return self.vehicles.get(vehicle_id)

    async def get_by_plate(self, plate: str):
        for vehicle in self.vehicles.values():
            if vehicle.plate == plate:
                return vehicle
        return None


class MockServiceOrderRepository(ServiceOrderRepository):
    def __init__(self):
        self.service_orders = {}

    async def save(self, service_order: ServiceOrder) -> None:
        self.service_orders[service_order.id] = service_order

    async def get_by_id(self, service_order_id) -> ServiceOrder | None:
        return self.service_orders.get(service_order_id)

    async def update_status(self, service_order_id, status) -> None:
        if service_order_id in self.service_orders:
            so = self.service_orders[service_order_id]
            so.status = status

    async def list_active(self) -> list[ServiceOrder]:
        return [
            so
            for so in self.service_orders.values()
            if so.status
            not in [ServiceOrderStatus.FINISHED, ServiceOrderStatus.DELIVERED]
        ]


class MockServiceItemRepository(ServiceItemRepository):
    async def save(self, service_item) -> None:
        pass

    async def save_many(self, service_items: list) -> None:
        pass

    async def get_by_service_order_id(self, service_order_id):
        return []


class MockPartItemRepository(PartItemRepository):
    async def save(self, part_item) -> None:
        pass

    async def save_many(self, part_items: list) -> None:
        pass

    async def get_by_service_order_id(self, service_order_id):
        return []


class MockEmailSender:
    def __init__(self):
        self.sent = []

    async def send_email(
        self, to_email: str, subject: str, body: str
    ) -> None:
        self.sent.append(
            {"type": "email", "to": to_email, "subject": subject, "body": body}
        )

    async def send_service_order_created(
        self, customer_email: str, service_order_id: str
    ) -> None:
        self.sent.append(
            {
                "type": "created",
                "to": customer_email,
                "service_order_id": service_order_id,
            }
        )

    async def send_status_changed(
        self, customer_email: str, service_order_id: str, new_status: str
    ) -> None:
        self.sent.append(
            {
                "type": "status_changed",
                "to": customer_email,
                "service_order_id": service_order_id,
                "new_status": new_status,
            }
        )

    async def send_approval_request(
        self, customer_email: str, service_order_id: str
    ) -> None:
        self.sent.append(
            {
                "type": "approval_request",
                "to": customer_email,
                "service_order_id": service_order_id,
            }
        )


@pytest.mark.asyncio
async def test_create_service_order():
    customer_repo = MockCustomerRepository()
    vehicle_repo = MockVehicleRepository()
    service_order_repo = MockServiceOrderRepository()
    service_item_repo = MockServiceItemRepository()
    part_item_repo = MockPartItemRepository()
    email_sender = MockEmailSender()

    use_case = CreateServiceOrderUseCase(
        customer_repo,
        vehicle_repo,
        service_order_repo,
        service_item_repo,
        part_item_repo,
        email_sender,
    )

    dto = CreateServiceOrderDTO(
        customer_name="John Doe",
        customer_email="john@example.com",
        customer_phone="123456789",
        vehicle_brand="Toyota",
        vehicle_model="Corolla",
        vehicle_year=2020,
        vehicle_plate="ABC123",
        services=[{"description": "Oil change", "price": 50.0}],
        parts=[{"name": "Oil filter", "price": 30.0, "quantity": 1}],
    )

    service_order_id = await use_case.execute(dto)

    assert service_order_id is not None
    service_order = await service_order_repo.get_by_id(
        __import__("uuid").UUID(service_order_id)
    )
    assert service_order is not None
    assert service_order.status == ServiceOrderStatus.RECEIVED
    assert any(m["type"] == "created" for m in email_sender.sent)


@pytest.mark.asyncio
async def test_get_service_order_status():
    from src.application.use_cases.get_service_order_status_use_case import (
        GetServiceOrderStatusUseCase,
    )

    service_order_repo = MockServiceOrderRepository()
    service_order_id = uuid4()

    service_order = ServiceOrder(
        id=service_order_id,
        customer_id=uuid4(),
        vehicle_id=uuid4(),
        status=ServiceOrderStatus.RECEIVED,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    await service_order_repo.save(service_order)

    use_case = GetServiceOrderStatusUseCase(service_order_repo)
    status = await use_case.execute(service_order_id)

    assert status == ServiceOrderStatus.RECEIVED.value


@pytest.mark.asyncio
async def test_approve_service_order():
    from src.application.use_cases.approve_service_order_use_case import (
        ApproveServiceOrderUseCase,
    )

    service_order_repo = MockServiceOrderRepository()
    customer_repo = MockCustomerRepository()
    email_sender = MockEmailSender()
    service_order_id = uuid4()
    customer_id = uuid4()

    service_order = ServiceOrder(
        id=service_order_id,
        customer_id=customer_id,
        vehicle_id=uuid4(),
        status=ServiceOrderStatus.WAITING_APPROVAL,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    await service_order_repo.save(service_order)

    await customer_repo.save(
        Customer(
            id=customer_id,
            name="John Doe",
            email="john@example.com",
            phone="123",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    )

    use_case = ApproveServiceOrderUseCase(
        service_order_repo, customer_repo, email_sender
    )
    result = await use_case.execute(service_order_id, True)

    assert result is True

    updated_order = await service_order_repo.get_by_id(service_order_id)
    assert updated_order.status == ServiceOrderStatus.IN_PROGRESS
    assert any(
        m["type"] == "status_changed"
        and m["to"] == "john@example.com"
        and m["new_status"] == ServiceOrderStatus.IN_PROGRESS.value
        for m in email_sender.sent
    )


@pytest.mark.asyncio
async def test_reject_service_order_budget_sets_finished_and_notifies():
    from src.application.use_cases.approve_service_order_use_case import (
        ApproveServiceOrderUseCase,
    )

    service_order_repo = MockServiceOrderRepository()
    customer_repo = MockCustomerRepository()
    email_sender = MockEmailSender()
    service_order_id = uuid4()
    customer_id = uuid4()

    await customer_repo.save(
        Customer(
            id=customer_id,
            name="Jane Doe",
            email="jane@example.com",
            phone="123",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    )

    await service_order_repo.save(
        ServiceOrder(
            id=service_order_id,
            customer_id=customer_id,
            vehicle_id=uuid4(),
            status=ServiceOrderStatus.WAITING_APPROVAL,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    )

    use_case = ApproveServiceOrderUseCase(
        service_order_repo, customer_repo, email_sender
    )
    result = await use_case.execute(service_order_id, False)

    assert result is True
    updated_order = await service_order_repo.get_by_id(service_order_id)
    assert updated_order.status == ServiceOrderStatus.FINISHED
    assert any(
        m["type"] == "status_changed"
        and m["to"] == "jane@example.com"
        and m["new_status"] == ServiceOrderStatus.FINISHED.value
        for m in email_sender.sent
    )


@pytest.mark.asyncio
async def test_list_active_service_orders():
    from src.application.use_cases.list_active_service_orders_use_case import (
        ListActiveServiceOrdersUseCase,
    )

    service_order_repo = MockServiceOrderRepository()

    order1 = ServiceOrder(
        id=uuid4(),
        customer_id=uuid4(),
        vehicle_id=uuid4(),
        status=ServiceOrderStatus.RECEIVED,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    order2 = ServiceOrder(
        id=uuid4(),
        customer_id=uuid4(),
        vehicle_id=uuid4(),
        status=ServiceOrderStatus.IN_PROGRESS,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    await service_order_repo.save(order1)
    await service_order_repo.save(order2)

    use_case = ListActiveServiceOrdersUseCase(service_order_repo)
    orders = await use_case.execute()

    assert len(orders) == 2
    assert orders[0].status == ServiceOrderStatus.IN_PROGRESS
    assert orders[1].status == ServiceOrderStatus.RECEIVED


@pytest.mark.asyncio
async def test_update_status_sends_email():
    from src.application.use_cases import update_service_order_status_use_case

    service_order_repo = MockServiceOrderRepository()
    customer_repo = MockCustomerRepository()
    email_sender = MockEmailSender()
    service_order_id = uuid4()
    customer_id = uuid4()

    await customer_repo.save(
        Customer(
            id=customer_id,
            name="John Doe",
            email="john@example.com",
            phone="123",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    )
    await service_order_repo.save(
        ServiceOrder(
            id=service_order_id,
            customer_id=customer_id,
            vehicle_id=uuid4(),
            status=ServiceOrderStatus.DIAGNOSIS,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    )

    UpdateServiceOrderStatusUseCase = (
        update_service_order_status_use_case.UpdateServiceOrderStatusUseCase
    )
    use_case = UpdateServiceOrderStatusUseCase(
        service_order_repo, customer_repo, email_sender
    )
    result = await use_case.execute(
        service_order_id, ServiceOrderStatus.IN_PROGRESS.value
    )
    assert result is True

    updated = await service_order_repo.get_by_id(service_order_id)
    assert updated.status == ServiceOrderStatus.IN_PROGRESS
    assert any(
        m["type"] == "status_changed"
        and m["to"] == "john@example.com"
        and m["new_status"] == ServiceOrderStatus.IN_PROGRESS.value
        for m in email_sender.sent
    )
