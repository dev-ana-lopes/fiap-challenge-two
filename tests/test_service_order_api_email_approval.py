from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.domain.entities import Customer, ServiceOrder
from src.domain.enums import ServiceOrderStatus
from src.presentation.dependencies.auth_dependencies import get_current_user
from src.presentation.dependencies.db_dependencies import (
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
from tests.support import (
    MockApprovalTokenService,
    MockCatalogServiceRepository,
    MockCustomerRepository,
    MockEmailSender,
    MockInventoryPartRepository,
    MockPartItemRepository,
    MockServiceItemRepository,
    MockServiceOrderRepository,
    MockVehicleRepository,
    create_test_app,
)


@pytest_asyncio.fixture
async def api_context():
    app = create_test_app()
    customer_repo = MockCustomerRepository()
    vehicle_repo = MockVehicleRepository()
    service_order_repo = MockServiceOrderRepository()
    service_item_repo = MockServiceItemRepository()
    part_item_repo = MockPartItemRepository()
    catalog_service_repo = MockCatalogServiceRepository()
    inventory_part_repo = MockInventoryPartRepository()
    email_sender = MockEmailSender()
    approval_token_service = MockApprovalTokenService()

    async def override_current_user():
        return {"user_id": "test-user"}

    async def override_customer_repo():
        return customer_repo

    async def override_vehicle_repo():
        return vehicle_repo

    async def override_service_order_repo():
        return service_order_repo

    async def override_service_item_repo():
        return service_item_repo

    async def override_part_item_repo():
        return part_item_repo

    async def override_catalog_repo():
        return catalog_service_repo

    async def override_inventory_repo():
        return inventory_part_repo

    def override_email_sender():
        return email_sender

    def override_approval_token_service():
        return approval_token_service

    app.dependency_overrides[get_current_user] = override_current_user
    app.dependency_overrides[get_customer_repository] = override_customer_repo
    app.dependency_overrides[get_vehicle_repository] = override_vehicle_repo
    app.dependency_overrides[get_service_order_repository] = override_service_order_repo
    app.dependency_overrides[get_service_item_repository] = override_service_item_repo
    app.dependency_overrides[get_part_item_repository] = override_part_item_repo
    app.dependency_overrides[get_catalog_service_repository] = override_catalog_repo
    app.dependency_overrides[get_inventory_part_repository] = override_inventory_repo
    app.dependency_overrides[get_email_sender] = override_email_sender
    app.dependency_overrides[
        get_approval_token_service
    ] = override_approval_token_service

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        yield {
            "app": app,
            "client": client,
            "customer_repo": customer_repo,
            "service_order_repo": service_order_repo,
            "email_sender": email_sender,
            "approval_token_service": approval_token_service,
        }

    app.dependency_overrides.clear()


def _create_service_order_payload(customer_email: str = "john@example.com") -> dict:
    return {
        "customer_name": "John Doe",
        "customer_email": customer_email,
        "customer_phone": "11999999999",
        "vehicle_brand": "Toyota",
        "vehicle_model": "Corolla",
        "vehicle_year": 2022,
        "vehicle_plate": "BRA2A34",
        "services": [{"description": "Revisao", "price": 120.0}],
        "parts": [{"name": "Filtro", "price": 30.0, "quantity": 1}],
    }


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_service_order_api_sends_approval_email(api_context):
    response = await api_context["client"].post(
        "/service-orders",
        json=_create_service_order_payload(),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["service_order_id"]
    assert any(
        message["type"] == "approval_request"
        and message["approve_token"]
        and message["reject_token"]
        for message in api_context["email_sender"].sent
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_manual_approval_endpoint_updates_status(api_context):
    create_response = await api_context["client"].post(
        "/service-orders",
        json=_create_service_order_payload(),
    )
    service_order_id = create_response.json()["service_order_id"]

    response = await api_context["client"].post(
        f"/service-orders/{service_order_id}/approval",
        json={"approved": True},
    )

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "status": "IN_PROGRESS",
        "decision": "APPROVED",
    }


@pytest.mark.asyncio
@pytest.mark.integration
async def test_email_link_approval_endpoint_updates_status(api_context):
    create_response = await api_context["client"].post(
        "/service-orders",
        json=_create_service_order_payload(),
    )
    service_order_id = create_response.json()["service_order_id"]
    approval_message = next(
        message
        for message in api_context["email_sender"].sent
        if message["type"] == "approval_request"
    )

    response = await api_context["client"].get(
        f"/public/service-orders/{service_order_id}/approval",
        params={"token": approval_message["approve_token"]},
    )

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "status": "IN_PROGRESS",
        "decision": "APPROVED",
    }


@pytest.mark.asyncio
@pytest.mark.integration
async def test_email_link_approval_rejects_invalid_expired_and_reused_tokens(
    api_context,
):
    create_response = await api_context["client"].post(
        "/service-orders",
        json=_create_service_order_payload(),
    )
    service_order_id = create_response.json()["service_order_id"]
    approval_message = next(
        message
        for message in api_context["email_sender"].sent
        if message["type"] == "approval_request"
    )

    invalid_response = await api_context["client"].get(
        f"/public/service-orders/{service_order_id}/approval",
        params={"token": "unknown-token"},
    )
    assert invalid_response.status_code == 400

    expired_token = api_context["approval_token_service"].add_expired_token(
        uuid4(), approved=False
    )
    expired_response = await api_context["client"].get(
        f"/public/service-orders/{service_order_id}/approval",
        params={"token": expired_token},
    )
    assert expired_response.status_code == 410

    first_response = await api_context["client"].get(
        f"/public/service-orders/{service_order_id}/approval",
        params={"token": approval_message["approve_token"]},
    )
    reused_response = await api_context["client"].get(
        f"/public/service-orders/{service_order_id}/approval",
        params={"token": approval_message["approve_token"]},
    )

    assert first_response.status_code == 200
    assert reused_response.status_code == 409


@pytest.mark.asyncio
@pytest.mark.integration
async def test_email_link_approval_rejects_mismatched_token(api_context):
    first_create_response = await api_context["client"].post(
        "/service-orders",
        json=_create_service_order_payload("first@example.com"),
    )
    second_create_response = await api_context["client"].post(
        "/service-orders",
        json=_create_service_order_payload("second@example.com"),
    )
    first_service_order_id = first_create_response.json()["service_order_id"]
    second_service_order_id = second_create_response.json()["service_order_id"]
    first_message = next(
        message
        for message in api_context["email_sender"].sent
        if message["type"] == "approval_request"
        and message["service_order_id"] == first_service_order_id
    )

    response = await api_context["client"].get(
        f"/public/service-orders/{second_service_order_id}/approval",
        params={"token": first_message["approve_token"]},
    )

    assert response.status_code == 400


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_status_to_waiting_approval_api_sends_email(api_context):
    service_order_id = uuid4()
    customer_id = uuid4()
    await api_context["customer_repo"].save(
        Customer(
            id=customer_id,
            name="Maria",
            cpf_cnpj=None,
            email="maria@example.com",
            phone="11999999999",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    )
    await api_context["service_order_repo"].save(
        ServiceOrder(
            id=service_order_id,
            customer_id=customer_id,
            vehicle_id=uuid4(),
            status=ServiceOrderStatus.DIAGNOSIS,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    )

    response = await api_context["client"].patch(
        f"/service-orders/{service_order_id}/status",
        json={"status": "WAITING_APPROVAL"},
    )

    assert response.status_code == 200
    assert any(
        message["type"] == "approval_request" and message["to"] == "maria@example.com"
        for message in api_context["email_sender"].sent
    )
