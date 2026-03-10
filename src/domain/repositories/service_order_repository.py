from abc import ABC, abstractmethod
from uuid import UUID

from ..entities import ServiceOrder
from ..enums import ServiceOrderStatus


class ServiceOrderRepository(ABC):

    @abstractmethod
    async def save(self, service_order: ServiceOrder) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, service_order_id: UUID) -> ServiceOrder | None:
        pass

    @abstractmethod
    async def update_status(
        self, service_order_id: UUID, status: ServiceOrderStatus
    ) -> None:
        pass

    @abstractmethod
    async def list_active(self) -> list[ServiceOrder]:
        pass
