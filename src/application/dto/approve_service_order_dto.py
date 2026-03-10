from dataclasses import dataclass


@dataclass
class ApproveServiceOrderDTO:
    service_order_id: str
    approved: bool
