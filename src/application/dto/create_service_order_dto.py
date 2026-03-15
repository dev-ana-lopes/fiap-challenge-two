from dataclasses import dataclass


@dataclass
class CreateServiceOrderDTO:
    customer_name: str
    customer_cpf_cnpj: str | None
    customer_email: str
    customer_phone: str
    vehicle_brand: str
    vehicle_model: str
    vehicle_year: int
    vehicle_plate: str
    services: list[dict] | None
    parts: list[dict] | None
    service_ids: list[str] | None = None
    part_refs: list[dict] | None = None
