from dataclasses import dataclass


@dataclass
class UpdateServiceOrderStatusDTO:
    service_order_id: str
    status: str
