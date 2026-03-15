from __future__ import annotations

import pytest
from datetime import datetime
from uuid import uuid4

from src.application.use_cases.vehicle_use_cases import (
    CreateVehicleUseCase,
    UpdateVehicleUseCase,
)
from src.domain.entities import Customer, Vehicle
from src.domain.repositories import CustomerRepository, VehicleRepository


class MockCustomerRepository(CustomerRepository):
    def __init__(self):
        self.customers: dict = {}

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
        self.vehicles: dict = {}

    async def save(self, vehicle: Vehicle) -> None:
        self.vehicles[vehicle.id] = vehicle

    async def update(self, vehicle: Vehicle) -> None:
        self.vehicles[vehicle.id] = vehicle

    async def delete(self, vehicle_id) -> bool:
        return self.vehicles.pop(vehicle_id, None) is not None

    async def get_by_id(self, vehicle_id) -> Vehicle | None:
        return self.vehicles.get(vehicle_id)

    async def get_by_plate(self, plate: str) -> Vehicle | None:
        for vehicle in self.vehicles.values():
            if vehicle.plate == plate:
                return vehicle
        return None

    async def list(self) -> list[Vehicle]:
        return list(self.vehicles.values())

    async def list_by_customer_id(self, customer_id) -> list[Vehicle]:
        return [v for v in self.vehicles.values() if v.customer_id == customer_id]


def _make_customer(customer_id):
    now = datetime.utcnow()
    return Customer(
        id=customer_id,
        name="Jane",
        cpf_cnpj=None,
        email="jane@example.com",
        phone="123",
        created_at=now,
        updated_at=now,
    )


def _make_vehicle(vehicle_id, customer_id, plate="BRA2A34"):
    now = datetime.utcnow()
    return Vehicle(
        id=vehicle_id,
        customer_id=customer_id,
        brand="Toyota",
        model="Corolla",
        year=2020,
        plate=plate,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_create_vehicle_customer_not_found_raises_lookup_error():
    customer_repo = MockCustomerRepository()
    vehicle_repo = MockVehicleRepository()
    use_case = CreateVehicleUseCase(vehicle_repo, customer_repo)

    with pytest.raises(LookupError):
        await use_case.execute(
            uuid4(),
            "Toyota",
            "Corolla",
            2020,
            "BRA2A34",
        )


@pytest.mark.asyncio
async def test_create_vehicle_duplicate_plate_raises_value_error():
    customer_repo = MockCustomerRepository()
    vehicle_repo = MockVehicleRepository()
    customer_id = uuid4()
    await customer_repo.save(_make_customer(customer_id))

    existing_vehicle = _make_vehicle(uuid4(), customer_id, plate="BRA2A34")
    await vehicle_repo.save(existing_vehicle)

    use_case = CreateVehicleUseCase(vehicle_repo, customer_repo)
    with pytest.raises(ValueError):
        await use_case.execute(
            customer_id,
            "Toyota",
            "Corolla",
            2020,
            "BRA2A34",
        )


@pytest.mark.asyncio
async def test_update_vehicle_customer_not_found_raises_lookup_error():
    customer_repo = MockCustomerRepository()
    vehicle_repo = MockVehicleRepository()

    existing_customer_id = uuid4()
    await customer_repo.save(_make_customer(existing_customer_id))

    vehicle_id = uuid4()
    await vehicle_repo.save(_make_vehicle(vehicle_id, existing_customer_id, plate="BRA2A34"))

    use_case = UpdateVehicleUseCase(vehicle_repo, customer_repo)
    with pytest.raises(LookupError):
        await use_case.execute(
            vehicle_id,
            uuid4(),
            "Toyota",
            "Corolla",
            2020,
            "BRA2A34",
        )


@pytest.mark.asyncio
async def test_update_vehicle_duplicate_plate_raises_value_error():
    customer_repo = MockCustomerRepository()
    vehicle_repo = MockVehicleRepository()

    customer_id = uuid4()
    await customer_repo.save(_make_customer(customer_id))

    vehicle_1 = _make_vehicle(uuid4(), customer_id, plate="BRA2A34")
    vehicle_2 = _make_vehicle(uuid4(), customer_id, plate="BRA2B34")
    await vehicle_repo.save(vehicle_1)
    await vehicle_repo.save(vehicle_2)

    use_case = UpdateVehicleUseCase(vehicle_repo, customer_repo)
    with pytest.raises(ValueError):
        await use_case.execute(
            vehicle_2.id,
            customer_id,
            "Toyota",
            "Corolla",
            2020,
            "BRA2A34",
        )
