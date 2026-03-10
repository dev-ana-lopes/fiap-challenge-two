from dataclasses import dataclass


@dataclass
class CreateServiceOrderDTO:
    customer_name: str
    customer_email: str
    customer_phone: str
    vehicle_brand: str
    vehicle_model: str
    vehicle_year: int
    vehicle_plate: str
    services: list[dict]
    parts: list[dict]
