from abc import ABC, abstractmethod
from uuid import UUID

from ..entities import Customer


class CustomerRepository(ABC):

    @abstractmethod
    async def save(self, customer: Customer) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, customer_id: UUID) -> Customer | None:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Customer | None:
        pass
