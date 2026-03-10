from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.customer import Customer
from src.domain.repositories.customer_repository import CustomerRepository
from src.infrastructure.database.models.customer_model import CustomerModel


class PostgresCustomerRepository(CustomerRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, customer: Customer) -> None:
        model = CustomerModel(
            id=customer.id,
            name=customer.name,
            email=customer.email,
            phone=customer.phone,
            created_at=customer.created_at,
            updated_at=customer.updated_at,
        )
        self.session.add(model)
        await self.session.commit()

    async def get_by_id(self, customer_id: UUID) -> Customer | None:
        query = select(CustomerModel).where(CustomerModel.id == customer_id)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return Customer(
            id=model.id,
            name=model.name,
            email=model.email,
            phone=model.phone,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_email(self, email: str) -> Customer | None:
        query = select(CustomerModel).where(CustomerModel.email == email)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return Customer(
            id=model.id,
            name=model.name,
            email=model.email,
            phone=model.phone,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
