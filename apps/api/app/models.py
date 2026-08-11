from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )


class User(TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint("role IN ('admin', 'operator')", name="ck_users_role"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="operator", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)


class Client(TimestampMixin, Base):
    __tablename__ = "clients"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(180), index=True)
    tax_id: Mapped[str | None] = mapped_column(String(50))
    phone: Mapped[str | None] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    trips: Mapped[list["Trip"]] = relationship(back_populates="client")
    payments: Mapped[list["ClientPayment"]] = relationship(back_populates="client")


class Driver(TimestampMixin, Base):
    __tablename__ = "drivers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(180), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    trips: Mapped[list["Trip"]] = relationship(back_populates="driver")


class Vehicle(TimestampMixin, Base):
    __tablename__ = "vehicles"
    id: Mapped[int] = mapped_column(primary_key=True)
    plate: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    brand: Mapped[str | None] = mapped_column(String(80))
    model: Mapped[str | None] = mapped_column(String(80))
    year: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    trips: Mapped[list["Trip"]] = relationship(back_populates="vehicle")
    expenses: Mapped[list["VehicleExpense"]] = relationship(back_populates="vehicle")


class TripExpenseCategory(Base):
    __tablename__ = "trip_expense_categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class Trip(TimestampMixin, Base):
    __tablename__ = "trips"
    __table_args__ = (
        CheckConstraint("agreed_price >= 0", name="ck_trips_price_nonnegative"),
        CheckConstraint("status IN ('draft', 'completed', 'cancelled')", name="ck_trips_status"),
        Index("ix_trips_client_date", "client_id", "trip_date"),
        Index("ix_trips_vehicle_date", "vehicle_id", "trip_date"),
        Index("ix_trips_driver_date", "driver_id", "trip_date"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    trip_date: Mapped[date] = mapped_column(Date, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="RESTRICT"), index=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id", ondelete="RESTRICT"), index=True)
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id", ondelete="RESTRICT"), index=True)
    origin: Mapped[str | None] = mapped_column(String(180))
    destination: Mapped[str | None] = mapped_column(String(180))
    description: Mapped[str | None] = mapped_column(Text)
    agreed_price: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"))
    status: Mapped[str] = mapped_column(String(20), default="draft", index=True)
    notes: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    client: Mapped[Client] = relationship(back_populates="trips")
    vehicle: Mapped[Vehicle] = relationship(back_populates="trips")
    driver: Mapped[Driver] = relationship(back_populates="trips")
    expenses: Mapped[list["TripExpense"]] = relationship(back_populates="trip")
    allocations: Mapped[list["PaymentAllocation"]] = relationship(back_populates="trip")


class TripExpense(TimestampMixin, Base):
    __tablename__ = "trip_expenses"
    __table_args__ = (CheckConstraint("amount > 0", name="ck_trip_expenses_amount_positive"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id", ondelete="RESTRICT"), index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("trip_expense_categories.id", ondelete="RESTRICT"), index=True)
    expense_date: Mapped[date] = mapped_column(Date, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    description: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    trip: Mapped[Trip] = relationship(back_populates="expenses")
    category: Mapped[TripExpenseCategory] = relationship()


class VehicleExpense(TimestampMixin, Base):
    __tablename__ = "vehicle_expenses"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_vehicle_expenses_amount_positive"),
        CheckConstraint("expense_type IN ('maintenance', 'repair')", name="ck_vehicle_expenses_type"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id", ondelete="RESTRICT"), index=True)
    expense_type: Mapped[str] = mapped_column(String(20), index=True)
    expense_date: Mapped[date] = mapped_column(Date, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    description: Mapped[str] = mapped_column(Text)
    odometer: Mapped[int | None] = mapped_column(Integer)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    vehicle: Mapped[Vehicle] = relationship(back_populates="expenses")


class ClientPayment(Base):
    __tablename__ = "client_payments"
    __table_args__ = (CheckConstraint("amount > 0", name="ck_client_payments_amount_positive"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="RESTRICT"), index=True)
    payment_date: Mapped[date] = mapped_column(Date, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    payment_method: Mapped[str | None] = mapped_column(String(80))
    reference: Mapped[str | None] = mapped_column(String(120))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    client: Mapped[Client] = relationship(back_populates="payments")
    allocations: Mapped[list["PaymentAllocation"]] = relationship(back_populates="payment")


class PaymentAllocation(Base):
    __tablename__ = "payment_allocations"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_payment_allocations_amount_positive"),
        UniqueConstraint("payment_id", "trip_id", name="uq_payment_allocation_payment_trip"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    payment_id: Mapped[int] = mapped_column(ForeignKey("client_payments.id", ondelete="RESTRICT"), index=True)
    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id", ondelete="RESTRICT"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    payment: Mapped[ClientPayment] = relationship(back_populates="allocations")
    trip: Mapped[Trip] = relationship(back_populates="allocations")

