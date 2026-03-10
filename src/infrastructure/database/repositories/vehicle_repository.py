from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.vehicle import Vehicle
from src.domain.repositories.vehicle_repository import VehicleRepository

from ..models.vehicle_model import VehicleModel


class PostgresVehicleRepository(VehicleRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, vehicle: Vehicle) -> None:
        model = VehicleModel(
            id=vehicle.id,
            customer_id=vehicle.customer_id,
            brand=vehicle.brand,
            model=vehicle.model,
            year=vehicle.year,
            plate=vehicle.plate,
            created_at=vehicle.created_at,
            updated_at=vehicle.updated_at,
        )
        self.session.add(model)
        await self.session.commit()

    async def get_by_id(self, vehicle_id: UUID) -> Vehicle | None:
        query = select(VehicleModel).where(VehicleModel.id == vehicle_id)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return Vehicle(
            id=model.id,
            customer_id=model.customer_id,
            brand=model.brand,
            model=model.model,
            year=model.year,
            plate=model.plate,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_plate(self, plate: str) -> Vehicle | None:
        query = select(VehicleModel).where(VehicleModel.plate == plate)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return Vehicle(
            id=model.id,
            customer_id=model.customer_id,
            brand=model.brand,
            model=model.model,
            year=model.year,
            plate=model.plate,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
