from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from ..enums import ServiceOrderStatus
from .part_item import PartItem
from .service_item import ServiceItem


@dataclass
class ServiceOrder:
    id: UUID
    customer_id: UUID
    vehicle_id: UUID
    status: ServiceOrderStatus
    created_at: datetime
    updated_at: datetime
    service_items: list[ServiceItem] = field(default_factory=list)
    part_items: list[PartItem] = field(default_factory=list)
