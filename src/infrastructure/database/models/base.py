from sqlalchemy.orm import declarative_base

from .customer_model import CustomerModel
from .part_item_model import PartItemModel
from .service_item_model import ServiceItemModel
from .service_order_model import ServiceOrderModel
from .user_model import UserModel
from .vehicle_model import VehicleModel

Base = declarative_base()

Base.registry.configure()

__all__ = [
    "Base",
    "CustomerModel",
    "VehicleModel",
    "ServiceOrderModel",
    "ServiceItemModel",
    "PartItemModel",
    "UserModel",
]
