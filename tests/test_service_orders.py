from datetime import datetime
from uuid import UUID, uuid4

import pytest

from src.application.dto.create_service_order_dto import CreateServiceOrderDTO
from src.application.use_cases import (
    ApproveServiceOrderByTokenUseCase,
    ApproveServiceOrderUseCase,
    CreateServiceOrderUseCase,
    GetServiceOrderStatusUseCase,
    ListActiveServiceOrdersUseCase,
    SendApprovalRequestEmailUseCase,
    UpdateServiceOrderStatusUseCase,
)
from src.application.use_cases.apply_service_order_approval_decision_use_case import (
    ApplyServiceOrderApprovalDecisionUseCase,
)
from src.domain.entities import Customer, ServiceOrder
from src.domain.enums import ServiceOrderStatus
from src.domain.errors import (
    ApprovalActionAlreadyProcessedError,
    ApprovalTokenMismatchError,
    InvalidServiceOrderTransitionError,
)
from tests.support import (
    FailingEmailSender,
    MockApprovalTokenService,
    MockCatalogServiceRepository,
    MockCustomerRepository,
    MockEmailSender,
    MockInventoryPartRepository,
    MockPartItemRepository,
    MockServiceItemRepository,
    MockServiceOrderRepository,
    MockVehicleRepository,
)


@pytest.mark.asyncio
async def test_create_service_order_sends_approval_request_with_tokens_and_summary():
    customer_repo = MockCustomerRepository()
    vehicle_repo = MockVehicleRepository()
    service_order_repo = MockServiceOrderRepository()
    service_item_repo = MockServiceItemRepository()
    part_item_repo = MockPartItemRepository()
    catalog_service_repo = MockCatalogServiceRepository()
    inventory_part_repo = MockInventoryPartRepository()
    email_sender = MockEmailSender()
    approval_token_service = MockApprovalTokenService()

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
    service_order = await service_order_repo.get_by_id(UUID(service_order_id))
    assert service_order is not None
    assert service_order.status == ServiceOrderStatus.WAITING_APPROVAL
    assert any(
        message["type"] == "approval_request"
        and message["to"] == "john@example.com"
        and message["total"] == 80.0
        and "Servico: Oil change - R$ 50.00" in message["summary_lines"]
        and "Peca: Oil filter x1 - R$ 30.00" in message["summary_lines"]
        and message["approve_token"] != message["reject_token"]
        for message in email_sender.sent
    )


@pytest.mark.asyncio
async def test_send_approval_request_email_use_case_builds_summary_lines():
    email_sender = MockEmailSender()
    token_service = MockApprovalTokenService()
    use_case = SendApprovalRequestEmailUseCase(email_sender, token_service)
    service_order_id = uuid4()

    service_order = ServiceOrder(
        id=service_order_id,
        customer_id=uuid4(),
        vehicle_id=uuid4(),
        status=ServiceOrderStatus.WAITING_APPROVAL,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        service_items=[],
        part_items=[],
    )

    await use_case.execute("john@example.com", service_order)

    assert email_sender.sent[0]["summary_lines"] == (
        "Sem itens detalhados no orcamento.",
    )
    assert email_sender.sent[0]["approve_token"]
    assert email_sender.sent[0]["reject_token"]


@pytest.mark.asyncio
async def test_create_service_order_succeeds_when_email_sending_fails():
    customer_repo = MockCustomerRepository()
    vehicle_repo = MockVehicleRepository()
    service_order_repo = MockServiceOrderRepository()
    service_item_repo = MockServiceItemRepository()
    part_item_repo = MockPartItemRepository()
    catalog_service_repo = MockCatalogServiceRepository()
    inventory_part_repo = MockInventoryPartRepository()
    email_sender = FailingEmailSender()
    approval_token_service = MockApprovalTokenService()

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
    service_order = await service_order_repo.get_by_id(UUID(service_order_id))
    assert service_order is not None
    assert service_order.status == ServiceOrderStatus.WAITING_APPROVAL


@pytest.mark.asyncio
async def test_get_service_order_status():
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
async def test_manual_approve_service_order_moves_to_in_progress_and_notifies():
    service_order_repo = MockServiceOrderRepository()
    customer_repo = MockCustomerRepository()
    email_sender = MockEmailSender()
    service_order_id = uuid4()
    customer_id = uuid4()

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
        service_order_repo,
        customer_repo,
        email_sender,
    )
    updated_status = await use_case.execute(service_order_id, True)

    assert updated_status == ServiceOrderStatus.IN_PROGRESS
    updated_order = await service_order_repo.get_by_id(service_order_id)
    assert updated_order.status == ServiceOrderStatus.IN_PROGRESS
    assert updated_order.started_at is not None
    assert any(
        message["type"] == "status_changed"
        and message["to"] == "john@example.com"
        and message["new_status"] == ServiceOrderStatus.IN_PROGRESS.value
        for message in email_sender.sent
    )


@pytest.mark.asyncio
async def test_reject_service_order_budget_sets_cancelled_and_notifies():
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
        service_order_repo,
        customer_repo,
        email_sender,
    )
    updated_status = await use_case.execute(service_order_id, False)

    assert updated_status == ServiceOrderStatus.CANCELLED
    updated_order = await service_order_repo.get_by_id(service_order_id)
    assert updated_order.status == ServiceOrderStatus.CANCELLED
    assert any(
        message["type"] == "status_changed"
        and message["to"] == "jane@example.com"
        and message["new_status"] == ServiceOrderStatus.CANCELLED.value
        for message in email_sender.sent
    )


@pytest.mark.asyncio
async def test_manual_approval_fails_when_order_is_not_waiting_approval():
    service_order_repo = MockServiceOrderRepository()
    customer_repo = MockCustomerRepository()
    email_sender = MockEmailSender()
    service_order_id = uuid4()

    await service_order_repo.save(
        ServiceOrder(
            id=service_order_id,
            customer_id=uuid4(),
            vehicle_id=uuid4(),
            status=ServiceOrderStatus.IN_PROGRESS,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    )

    use_case = ApproveServiceOrderUseCase(
        service_order_repo,
        customer_repo,
        email_sender,
    )

    with pytest.raises(ApprovalActionAlreadyProcessedError):
        await use_case.execute(service_order_id, True)


@pytest.mark.asyncio
async def test_approve_service_order_by_token_uses_token_decision():
    service_order_repo = MockServiceOrderRepository()
    customer_repo = MockCustomerRepository()
    email_sender = MockEmailSender()
    token_service = MockApprovalTokenService()
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
            status=ServiceOrderStatus.WAITING_APPROVAL,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    )

    token = token_service.generate_token(service_order_id, approved=True)
    apply_decision_use_case = ApplyServiceOrderApprovalDecisionUseCase(
        service_order_repo,
        customer_repo,
        email_sender,
    )
    use_case = ApproveServiceOrderByTokenUseCase(
        token_service,
        apply_decision_use_case,
    )

    updated_status = await use_case.execute(service_order_id, token)

    assert updated_status == ServiceOrderStatus.IN_PROGRESS


@pytest.mark.asyncio
async def test_approve_service_order_by_token_rejects_mismatched_order_id():
    service_order_repo = MockServiceOrderRepository()
    customer_repo = MockCustomerRepository()
    email_sender = MockEmailSender()
    token_service = MockApprovalTokenService()
    token_order_id = uuid4()
    requested_order_id = uuid4()

    token = token_service.generate_token(token_order_id, approved=True)
    apply_decision_use_case = ApplyServiceOrderApprovalDecisionUseCase(
        service_order_repo,
        customer_repo,
        email_sender,
    )
    use_case = ApproveServiceOrderByTokenUseCase(
        token_service,
        apply_decision_use_case,
    )

    with pytest.raises(ApprovalTokenMismatchError):
        await use_case.execute(requested_order_id, token)


@pytest.mark.asyncio
async def test_list_active_service_orders():
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
async def test_update_status_sends_email_for_regular_status_change():
    service_order_repo = MockServiceOrderRepository()
    customer_repo = MockCustomerRepository()
    email_sender = MockEmailSender()
    approval_token_service = MockApprovalTokenService()
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
            status=ServiceOrderStatus.WAITING_APPROVAL,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    )

    use_case = UpdateServiceOrderStatusUseCase(
        service_order_repo,
        customer_repo,
        email_sender,
        approval_token_service,
    )
    updated_status = await use_case.execute(
        service_order_id,
        ServiceOrderStatus.IN_PROGRESS.value,
    )

    assert updated_status == ServiceOrderStatus.IN_PROGRESS
    updated = await service_order_repo.get_by_id(service_order_id)
    assert updated.status == ServiceOrderStatus.IN_PROGRESS
    assert any(
        message["type"] == "status_changed"
        and message["to"] == "john@example.com"
        and message["new_status"] == ServiceOrderStatus.IN_PROGRESS.value
        for message in email_sender.sent
    )


@pytest.mark.asyncio
async def test_update_status_to_waiting_approval_sends_approval_request():
    service_order_repo = MockServiceOrderRepository()
    customer_repo = MockCustomerRepository()
    email_sender = MockEmailSender()
    approval_token_service = MockApprovalTokenService()
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

    use_case = UpdateServiceOrderStatusUseCase(
        service_order_repo,
        customer_repo,
        email_sender,
        approval_token_service,
    )
    updated_status = await use_case.execute(
        service_order_id,
        ServiceOrderStatus.WAITING_APPROVAL.value,
    )

    assert updated_status == ServiceOrderStatus.WAITING_APPROVAL
    assert any(
        message["type"] == "approval_request"
        and message["to"] == "john@example.com"
        and message["approve_token"]
        and message["reject_token"]
        for message in email_sender.sent
    )


@pytest.mark.asyncio
async def test_update_status_rejects_invalid_transition():
    service_order_repo = MockServiceOrderRepository()
    customer_repo = MockCustomerRepository()
    email_sender = MockEmailSender()
    approval_token_service = MockApprovalTokenService()
    service_order_id = uuid4()

    await service_order_repo.save(
        ServiceOrder(
            id=service_order_id,
            customer_id=uuid4(),
            vehicle_id=uuid4(),
            status=ServiceOrderStatus.WAITING_APPROVAL,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    )

    use_case = UpdateServiceOrderStatusUseCase(
        service_order_repo,
        customer_repo,
        email_sender,
        approval_token_service,
    )

    with pytest.raises(InvalidServiceOrderTransitionError):
        await use_case.execute(service_order_id, ServiceOrderStatus.FINISHED.value)
