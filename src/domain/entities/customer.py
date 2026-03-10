from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Customer:
    id: UUID
    name: str
    email: str
    phone: str
    created_at: datetime
    updated_at: datetime
