from pydantic import BaseModel, EmailStr, Field, field_validator

from ...domain.validation import (
    is_valid_br_plate,
    is_valid_cpf_cnpj,
    normalize_digits,
    normalize_plate,
)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=255)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=255)


class RegisterResponse(BaseModel):
    user_id: str


class ServiceItemRequest(BaseModel):
    description: str = Field(..., min_length=1, max_length=500)
    price: float = Field(..., gt=0)


class PartItemRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    price: float = Field(..., gt=0)
    quantity: int = Field(..., ge=1)


class PartRefRequest(BaseModel):
    part_id: str
    quantity: int = Field(..., ge=1)


class CreateServiceOrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=255)
    customer_cpf_cnpj: str | None = None
    customer_email: EmailStr
    customer_phone: str = Field(..., min_length=1, max_length=20)
    vehicle_brand: str = Field(..., min_length=1, max_length=100)
    vehicle_model: str = Field(..., min_length=1, max_length=100)
    vehicle_year: int = Field(..., ge=1900, le=2100)
    vehicle_plate: str = Field(..., min_length=1, max_length=20)
    services: list[ServiceItemRequest] | None = None
    parts: list[PartItemRequest] | None = None
    service_ids: list[str] | None = None
    part_refs: list[PartRefRequest] | None = None

    @field_validator("customer_cpf_cnpj")
    @classmethod
    def validate_cpf_cnpj(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if not is_valid_cpf_cnpj(v):
            raise ValueError("Invalid CPF/CNPJ")
        return normalize_digits(v)

    @field_validator("vehicle_plate")
    @classmethod
    def validate_plate(cls, v: str) -> str:
        if not is_valid_br_plate(v):
            raise ValueError("Invalid vehicle plate")
        return normalize_plate(v)

    @field_validator("service_ids")
    @classmethod
    def validate_service_ids(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return None
        if len(v) < 1:
            raise ValueError("service_ids must have at least 1 item")
        return v


class CreateServiceOrderResponse(BaseModel):
    service_order_id: str


class ServiceOrderStatusResponse(BaseModel):
    status: str


class ApproveServiceOrderRequest(BaseModel):
    approved: bool


class UpdateServiceOrderStatusRequest(BaseModel):
    status: str


class ServiceItemResponse(BaseModel):
    id: str
    description: str
    price: float


class PartItemResponse(BaseModel):
    id: str
    name: str
    price: float
    quantity: int


class ServiceOrderResponse(BaseModel):
    id: str
    customer_id: str
    vehicle_id: str
    status: str
    created_at: str
    service_items: list[ServiceItemResponse]
    part_items: list[PartItemResponse]

