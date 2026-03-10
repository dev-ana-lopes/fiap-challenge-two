from .customer_repository import PostgresCustomerRepository
from .part_item_repository import PostgresPartItemRepository
from .service_item_repository import PostgresServiceItemRepository
from .service_order_repository import PostgresServiceOrderRepository
from .user_repository import PostgresUserRepository
from .vehicle_repository import PostgresVehicleRepository

__all__ = [
    "PostgresCustomerRepository",
    "PostgresPartItemRepository",
    "PostgresServiceItemRepository",
    "PostgresServiceOrderRepository",
    "PostgresUserRepository",
    "PostgresVehicleRepository",
]
