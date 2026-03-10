from dataclasses import dataclass


@dataclass
class VehicleData:
    brand: str
    model: str
    year: int
    plate: str
