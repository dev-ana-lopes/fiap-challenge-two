from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.services import ApprovalTokenService, EmailSender
from ...infrastructure.config.settings import Settings, get_settings
from ...infrastructure.database.repositories.catalog_service_repository import (
    PostgresCatalogServiceRepository,
)
from ...infrastructure.database.repositories.customer_repository import (
    PostgresCustomerRepository,
)
from ...infrastructure.database.repositories.inventory_part_repository import (
    PostgresInventoryPartRepository,
)
from ...infrastructure.database.repositories.part_item_repository import (
    PostgresPartItemRepository,
)
from ...infrastructure.database.repositories.service_item_repository import (
    PostgresServiceItemRepository,
)
from ...infrastructure.database.repositories.service_order_repository import (
    PostgresServiceOrderRepository,
)
from ...infrastructure.database.repositories.user_repository import (
    PostgresUserRepository,
)
from ...infrastructure.database.repositories.vehicle_repository import (
    PostgresVehicleRepository,
)
from ...infrastructure.database.session import DatabaseSession
from ...infrastructure.email.approval_token_service import JwtApprovalTokenService
from ...infrastructure.email.jwt_service import JwtService
from ...infrastructure.email.password_hasher import PasswordHasher
from ...infrastructure.email.smtp_client import SmtpEmailSender

database_session: DatabaseSession | None = None


def init_database(settings: Settings) -> None:
    global database_session
    database_session = DatabaseSession(settings)


async def get_session(
    settings: Settings = Depends(get_settings),
) -> AsyncSession:
    if database_session is None:
        init_database(settings)
    async for session in database_session.get_session():
        yield session


async def get_customer_repository(
    session: AsyncSession = Depends(get_session),
) -> PostgresCustomerRepository:
    return PostgresCustomerRepository(session)


async def get_catalog_service_repository(
    session: AsyncSession = Depends(get_session),
) -> PostgresCatalogServiceRepository:
    return PostgresCatalogServiceRepository(session)


async def get_inventory_part_repository(
    session: AsyncSession = Depends(get_session),
) -> PostgresInventoryPartRepository:
    return PostgresInventoryPartRepository(session)


async def get_vehicle_repository(
    session: AsyncSession = Depends(get_session),
) -> PostgresVehicleRepository:
    return PostgresVehicleRepository(session)


async def get_service_order_repository(
    session: AsyncSession = Depends(get_session),
) -> PostgresServiceOrderRepository:
    return PostgresServiceOrderRepository(session)


async def get_service_item_repository(
    session: AsyncSession = Depends(get_session),
) -> PostgresServiceItemRepository:
    return PostgresServiceItemRepository(session)


async def get_part_item_repository(
    session: AsyncSession = Depends(get_session),
) -> PostgresPartItemRepository:
    return PostgresPartItemRepository(session)


async def get_user_repository(
    session: AsyncSession = Depends(get_session),
) -> PostgresUserRepository:
    return PostgresUserRepository(session)


def get_email_sender(
    settings: Settings = Depends(get_settings),
) -> EmailSender:
    return SmtpEmailSender(settings)


def get_approval_token_service(
    settings: Settings = Depends(get_settings),
) -> ApprovalTokenService:
    return JwtApprovalTokenService(settings)


def get_jwt_service(
    settings: Settings = Depends(get_settings),
) -> JwtService:
    return JwtService(settings)


def get_password_hasher() -> PasswordHasher:
    return PasswordHasher()
