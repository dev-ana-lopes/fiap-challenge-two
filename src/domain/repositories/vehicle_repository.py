from abc import ABC, abstractmethod
from uuid import UUID

from ..entities import Vehicle


class VehicleRepository(ABC):

    @abstractmethod
    async def save(self, vehicle: Vehicle) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, vehicle_id: UUID) -> Vehicle | None:
        pass

    @abstractmethod
    async def get_by_plate(self, plate: str) -> Vehicle | None:
        pass
