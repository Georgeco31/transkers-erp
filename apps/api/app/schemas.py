from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Money = Decimal


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=8, max_length=200)


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=8, max_length=200)
    role: Literal["admin", "operator"] = "operator"


class ClientInput(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    tax_id: str | None = Field(default=None, max_length=50)
    phone: str | None = Field(default=None, max_length=50)
    notes: str | None = None
    is_active: bool = True


class DriverInput(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    is_active: bool = True


class VehicleInput(BaseModel):
    plate: str = Field(min_length=2, max_length=30)
    brand: str | None = Field(default=None, max_length=80)
    model: str | None = Field(default=None, max_length=80)
    year: int | None = Field(default=None, ge=1900, le=2200)
    notes: str | None = None
    is_active: bool = True

    @field_validator("plate")
    @classmethod
    def normalize_plate(cls, value: str) -> str:
        return "".join(value.upper().split())


class TripInput(BaseModel):
    trip_date: date
    client_id: int
    vehicle_id: int
    driver_id: int
    origin: str | None = Field(default=None, max_length=180)
    destination: str | None = Field(default=None, max_length=180)
    description: str | None = None
    agreed_price: Money = Field(ge=Decimal("0.00"), decimal_places=2)
    status: Literal["draft", "completed", "cancelled"] = "draft"
    notes: str | None = None


class TripStatusInput(BaseModel):
    status: Literal["draft", "completed", "cancelled"]


class CategoryInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    is_active: bool = True


class TripExpenseInput(BaseModel):
    trip_id: int
    category_id: int
    expense_date: date
    amount: Money = Field(gt=Decimal("0.00"), decimal_places=2)
    description: str | None = None


class VehicleExpenseInput(BaseModel):
    vehicle_id: int
    expense_type: Literal["maintenance", "repair"]
    expense_date: date
    amount: Money = Field(gt=Decimal("0.00"), decimal_places=2)
    description: str = Field(min_length=1)
    odometer: int | None = Field(default=None, ge=0)


class PaymentInput(BaseModel):
    client_id: int
    payment_date: date
    amount: Money = Field(gt=Decimal("0.00"), decimal_places=2)
    payment_method: str | None = Field(default=None, max_length=80)
    reference: str | None = Field(default=None, max_length=120)
    notes: str | None = None
    auto_allocate: bool = True


class PaymentUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    payment_date: date
    amount: Money = Field(gt=Decimal("0.00"), decimal_places=2)
    payment_method: str | None = Field(default=None, max_length=80)
    reference: str | None = Field(default=None, max_length=120)
    notes: str | None = None


class AllocationInput(BaseModel):
    trip_id: int
    amount: Money = Field(gt=Decimal("0.00"), decimal_places=2)


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
