from pydantic import BaseModel, EmailStr, Field


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


class CreateServiceOrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=255)
    customer_email: EmailStr
    customer_phone: str = Field(..., min_length=1, max_length=20)
    vehicle_brand: str = Field(..., min_length=1, max_length=100)
    vehicle_model: str = Field(..., min_length=1, max_length=100)
    vehicle_year: int = Field(..., ge=1900, le=2100)
    vehicle_plate: str = Field(..., min_length=1, max_length=20)
    services: list[ServiceItemRequest] = Field(..., min_items=1)
    parts: list[PartItemRequest] = Field(..., min_items=0)


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
