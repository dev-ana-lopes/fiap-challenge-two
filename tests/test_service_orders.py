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

    async def update(self, customer: Customer) -> None:
        self.customers[customer.id] = customer

    async def delete(self, customer_id) -> bool:
        return self.customers.pop(customer_id, None) is not None

    async def get_by_id(self, customer_id) -> Customer | None:
        return self.customers.get(customer_id)

    async def get_by_email(self, email: str) -> Customer | None:
        for customer in self.customers.values():
            if customer.email == email:
                return customer
        return None

    async def get_by_cpf_cnpj(self, cpf_cnpj: str) -> Customer | None:
        for customer in self.customers.values():
            if customer.cpf_cnpj == cpf_cnpj:
                return customer
        return None

    async def list(self) -> list[Customer]:
        return list(self.customers.values())


class MockVehicleRepository(VehicleRepository):
    def __init__(self):
        self.vehicles = {}

    async def save(self, vehicle) -> None:
        self.vehicles[vehicle.id] = vehicle

    async def update(self, vehicle) -> None:
        self.vehicles[vehicle.id] = vehicle

    async def delete(self, vehicle_id) -> bool:
        return self.vehicles.pop(vehicle_id, None) is not None

    async def get_by_id(self, vehicle_id) -> None:
        return self.vehicles.get(vehicle_id)

    async def get_by_plate(self, plate: str):
        for vehicle in self.vehicles.values():
            if vehicle.plate == plate:
                return vehicle
        return None

    async def list(self) -> list:
        return list(self.vehicles.values())

    async def list_by_customer_id(self, customer_id):
        return [v for v in self.vehicles.values() if v.customer_id == customer_id]


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

    async def set_started_at(self, service_order_id) -> None:
        if service_order_id in self.service_orders:
            so = self.service_orders[service_order_id]
            so.started_at = datetime.utcnow()

    async def set_finished_at(self, service_order_id) -> None:
        if service_order_id in self.service_orders:
            so = self.service_orders[service_order_id]
            so.finished_at = datetime.utcnow()

    async def get_average_execution_time_seconds(self) -> float | None:
        durations = []
        for so in self.service_orders.values():
            if so.started_at and so.finished_at:
                durations.append((so.finished_at - so.started_at).total_seconds())
        if not durations:
            return None
        return sum(durations) / len(durations)

    async def list_active(self) -> list[ServiceOrder]:
        return [
            so
            for so in self.service_orders.values()
            if so.status
            not in [
                ServiceOrderStatus.FINISHED,
                ServiceOrderStatus.DELIVERED,
                ServiceOrderStatus.CANCELLED,
            ]
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
        self, customer_email: str, service_order_id: str, total: float | None = None
    ) -> None:
        self.sent.append(
            {
                "type": "approval_request",
                "to": customer_email,
                "service_order_id": service_order_id,
                "total": total,
            }
        )


class MockCatalogServiceRepository:
    def __init__(self):
        self.services = {}

    async def create(self, service) -> None:
        self.services[service.id] = service

    async def update(self, service) -> None:
        self.services[service.id] = service

    async def delete(self, service_id) -> bool:
        return self.services.pop(service_id, None) is not None

    async def get_by_id(self, service_id):
        return self.services.get(service_id)

    async def list(self):
        return list(self.services.values())


class MockInventoryPartRepository:
    def __init__(self):
        self.parts = {}

    async def create(self, part) -> None:
        self.parts[part.id] = part

    async def update(self, part) -> None:
        self.parts[part.id] = part

    async def delete(self, part_id) -> bool:
        return self.parts.pop(part_id, None) is not None

    async def get_by_id(self, part_id):
        return self.parts.get(part_id)

    async def get_by_name(self, name: str):
        for p in self.parts.values():
            if p.name == name:
                return p
        return None

    async def list(self):
        return list(self.parts.values())

    async def decrease_stock(self, part_id, quantity: int) -> bool:
        part = self.parts.get(part_id)
        if part is None:
            return False
        if part.stock_quantity < quantity:
            return False
        part.stock_quantity -= quantity
        return True


@pytest.mark.asyncio
async def test_create_service_order():
    customer_repo = MockCustomerRepository()
    vehicle_repo = MockVehicleRepository()
    service_order_repo = MockServiceOrderRepository()
    service_item_repo = MockServiceItemRepository()
    part_item_repo = MockPartItemRepository()
    catalog_service_repo = MockCatalogServiceRepository()
    inventory_part_repo = MockInventoryPartRepository()
    email_sender = MockEmailSender()

    use_case = CreateServiceOrderUseCase(
        customer_repo,
        vehicle_repo,
        service_order_repo,
        service_item_repo,
        part_item_repo,
        catalog_service_repo,
        inventory_part_repo,
        email_sender,
    )

    dto = CreateServiceOrderDTO(
        customer_name="John Doe",
        customer_cpf_cnpj=None,
        customer_email="john@example.com",
        customer_phone="123456789",
        vehicle_brand="Toyota",
        vehicle_model="Corolla",
        vehicle_year=2020,
        vehicle_plate="ABC123",
        services=[{"description": "Oil change", "price": 50.0}],
        parts=[{"name": "Oil filter", "price": 30.0, "quantity": 1}],
        service_ids=None,
        part_refs=None,
    )

    service_order_id = await use_case.execute(dto)

    assert service_order_id is not None
    service_order = await service_order_repo.get_by_id(
        __import__("uuid").UUID(service_order_id)
    )
    assert service_order is not None
    assert service_order.status == ServiceOrderStatus.WAITING_APPROVAL
    assert any(
        m["type"] == "approval_request"
        and m["to"] == "john@example.com"
        and m["total"] == 80.0
        for m in email_sender.sent
    )


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
            cpf_cnpj=None,
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
        and m["service_order_id"] == str(service_order_id)
        for m in email_sender.sent
    )


@pytest.mark.asyncio
async def test_reject_service_order_budget_sets_cancelled_and_notifies():
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
            cpf_cnpj=None,
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
    assert updated_order.status == ServiceOrderStatus.CANCELLED
    assert any(
        m["type"] == "status_changed"
        and m["to"] == "jane@example.com"
        and m["new_status"] == ServiceOrderStatus.CANCELLED.value
        and m["service_order_id"] == str(service_order_id)
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
            cpf_cnpj=None,
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
        and m["service_order_id"] == str(service_order_id)
        for m in email_sender.sent
    )
