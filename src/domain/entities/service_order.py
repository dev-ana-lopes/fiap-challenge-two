from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from ..errors import InvalidServiceOrderTransitionError
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
    started_at: datetime | None = None
    finished_at: datetime | None = None
    service_items: list[ServiceItem] = field(default_factory=list)
    part_items: list[PartItem] = field(default_factory=list)

    _ALLOWED_TRANSITIONS = {
        ServiceOrderStatus.RECEIVED: {
            ServiceOrderStatus.DIAGNOSIS,
            ServiceOrderStatus.WAITING_APPROVAL,
            ServiceOrderStatus.CANCELLED,
        },
        ServiceOrderStatus.DIAGNOSIS: {
            ServiceOrderStatus.WAITING_APPROVAL,
            ServiceOrderStatus.IN_PROGRESS,
            ServiceOrderStatus.CANCELLED,
        },
        ServiceOrderStatus.WAITING_APPROVAL: {
            ServiceOrderStatus.IN_PROGRESS,
            ServiceOrderStatus.CANCELLED,
        },
        ServiceOrderStatus.IN_PROGRESS: {
            ServiceOrderStatus.FINISHED,
            ServiceOrderStatus.CANCELLED,
        },
        ServiceOrderStatus.FINISHED: {
            ServiceOrderStatus.DELIVERED,
        },
        ServiceOrderStatus.DELIVERED: set(),
        ServiceOrderStatus.CANCELLED: set(),
    }

    @property
    def budget_total(self) -> float:
        services_total = sum(item.price for item in self.service_items)
        parts_total = sum(item.price * item.quantity for item in self.part_items)
        return services_total + parts_total

    def can_transition_to(self, target_status: ServiceOrderStatus) -> bool:
        if target_status == self.status:
            return True
        return target_status in self._ALLOWED_TRANSITIONS[self.status]

    def transition_to(self, target_status: ServiceOrderStatus) -> None:
        if not self.can_transition_to(target_status):
            raise InvalidServiceOrderTransitionError(self.status, target_status)
        self.status = target_status

    def apply_budget_decision(self, approved: bool) -> ServiceOrderStatus:
        target_status = (
            ServiceOrderStatus.IN_PROGRESS if approved else ServiceOrderStatus.CANCELLED
        )
        self.transition_to(target_status)
        return target_status
