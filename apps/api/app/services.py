from calendar import monthrange
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session, joinedload

from app import models

ZERO = Decimal("0.00")


def money(value: Decimal | int | None) -> Decimal:
    return Decimal(value or 0).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def require_relations(db: Session, client_id: int, vehicle_id: int, driver_id: int) -> None:
    client = db.get(models.Client, client_id)
    vehicle = db.get(models.Vehicle, vehicle_id)
    driver = db.get(models.Driver, driver_id)
    if not client:
        raise HTTPException(422, "El cliente no existe.")
    if not vehicle:
        raise HTTPException(422, "El vehículo no existe.")
    if not driver:
        raise HTTPException(422, "El chofer no existe.")
    if not (client.is_active and vehicle.is_active and driver.is_active):
        raise HTTPException(422, "Cliente, vehículo y chofer deben estar activos.")


def validate_trip_status(trip: models.Trip) -> None:
    if trip.status == "completed" and (
        not trip.trip_date or not trip.client_id or not trip.vehicle_id or not trip.driver_id or trip.agreed_price <= 0
    ):
        raise HTTPException(422, "Un viaje completado requiere fecha, cliente, vehículo, chofer y precio mayor que cero.")


def trip_expense_total(db: Session, trip_id: int) -> Decimal:
    total = db.scalar(select(func.coalesce(func.sum(models.TripExpense.amount), 0)).where(models.TripExpense.trip_id == trip_id))
    return money(total)


def trip_allocated_total(db: Session, trip_id: int) -> Decimal:
    total = db.scalar(select(func.coalesce(func.sum(models.PaymentAllocation.amount), 0)).where(models.PaymentAllocation.trip_id == trip_id))
    return money(total)


def payment_allocated_total(db: Session, payment_id: int) -> Decimal:
    total = db.scalar(select(func.coalesce(func.sum(models.PaymentAllocation.amount), 0)).where(models.PaymentAllocation.payment_id == payment_id))
    return money(total)


def allocate_payment(db: Session, payment: models.ClientPayment) -> None:
    available = money(payment.amount - payment_allocated_total(db, payment.id))
    if available <= ZERO:
        return
    trips = db.scalars(
        select(models.Trip)
        .where(models.Trip.client_id == payment.client_id, models.Trip.status == "completed")
        .order_by(models.Trip.trip_date, models.Trip.id)
        .with_for_update()
    ).all()
    for trip in trips:
        pending = money(trip.agreed_price - trip_allocated_total(db, trip.id))
        allocation = min(available, pending)
        if allocation > ZERO:
            db.add(models.PaymentAllocation(payment_id=payment.id, trip_id=trip.id, amount=allocation))
            db.flush()
            available = money(available - allocation)
        if available <= ZERO:
            break


def add_manual_allocation(db: Session, payment: models.ClientPayment, trip: models.Trip, amount: Decimal) -> models.PaymentAllocation:
    if trip.client_id != payment.client_id:
        raise HTTPException(422, "El pago y el viaje deben pertenecer al mismo cliente.")
    if trip.status != "completed":
        raise HTTPException(422, "Solo se pueden aplicar pagos a viajes completados.")
    if money(amount) > money(payment.amount - payment_allocated_total(db, payment.id)):
        raise HTTPException(422, "La asignación supera el saldo disponible del pago.")
    if money(amount) > money(trip.agreed_price - trip_allocated_total(db, trip.id)):
        raise HTTPException(422, "La asignación supera el saldo pendiente del viaje.")
    existing = db.scalar(select(models.PaymentAllocation).where(
        models.PaymentAllocation.payment_id == payment.id,
        models.PaymentAllocation.trip_id == trip.id,
    ))
    if existing:
        existing.amount = money(existing.amount + amount)
        allocation = existing
    else:
        allocation = models.PaymentAllocation(payment_id=payment.id, trip_id=trip.id, amount=money(amount))
        db.add(allocation)
    db.flush()
    return allocation


def trip_dict(db: Session, trip: models.Trip) -> dict:
    expenses = trip_expense_total(db, trip.id)
    allocated = trip_allocated_total(db, trip.id)
    revenue = money(trip.agreed_price if trip.status == "completed" else ZERO)
    return {
        "id": trip.id,
        "code": trip.code,
        "trip_date": trip.trip_date,
        "client_id": trip.client_id,
        "client_name": trip.client.name,
        "vehicle_id": trip.vehicle_id,
        "vehicle_plate": trip.vehicle.plate,
        "driver_id": trip.driver_id,
        "driver_name": trip.driver.name,
        "origin": trip.origin,
        "destination": trip.destination,
        "description": trip.description,
        "agreed_price": money(trip.agreed_price),
        "status": trip.status,
        "notes": trip.notes,
        "expense_total": expenses,
        "margin": money(revenue - expenses) if trip.status != "cancelled" else ZERO,
        "allocated": allocated,
        "pending": money(max(ZERO, revenue - allocated)),
        "created_at": trip.created_at,
        "updated_at": trip.updated_at,
    }


def client_totals(db: Session, client_id: int) -> dict[str, Decimal | int]:
    trip_count, billed = db.execute(
        select(func.count(models.Trip.id), func.coalesce(func.sum(models.Trip.agreed_price), 0)).where(
            models.Trip.client_id == client_id, models.Trip.status == "completed"
        )
    ).one()
    paid = db.scalar(select(func.coalesce(func.sum(models.ClientPayment.amount), 0)).where(models.ClientPayment.client_id == client_id))
    allocated = db.scalar(
        select(func.coalesce(func.sum(models.PaymentAllocation.amount), 0))
        .join(models.ClientPayment)
        .where(models.ClientPayment.client_id == client_id)
    )
    return {
        "trip_count": trip_count,
        "billed": money(billed),
        "paid": money(paid),
        "allocated": money(allocated),
        "pending": money(max(ZERO, money(billed) - money(allocated))),
        "credit": money(max(ZERO, money(paid) - money(allocated))),
    }


def month_bounds(year: int, month: int) -> tuple[date, date]:
    if month < 1 or month > 12:
        raise HTTPException(422, "Mes inválido.")
    return date(year, month, 1), date(year, month, monthrange(year, month)[1])


def monthly_report(db: Session, year: int, month: int) -> dict:
    start, end = month_bounds(year, month)
    trip_filter = and_(models.Trip.status == "completed", models.Trip.trip_date.between(start, end))
    trip_count, income = db.execute(
        select(func.count(models.Trip.id), func.coalesce(func.sum(models.Trip.agreed_price), 0)).where(trip_filter)
    ).one()
    direct = db.scalar(
        select(func.coalesce(func.sum(models.TripExpense.amount), 0))
        .join(models.Trip)
        .where(trip_filter)
    )
    maintenance = db.scalar(select(func.coalesce(func.sum(models.VehicleExpense.amount), 0)).where(
        models.VehicleExpense.expense_type == "maintenance", models.VehicleExpense.expense_date.between(start, end)
    ))
    repairs = db.scalar(select(func.coalesce(func.sum(models.VehicleExpense.amount), 0)).where(
        models.VehicleExpense.expense_type == "repair", models.VehicleExpense.expense_date.between(start, end)
    ))
    collected = db.scalar(select(func.coalesce(func.sum(models.ClientPayment.amount), 0)).where(
        models.ClientPayment.payment_date.between(start, end)
    ))
    allocated = db.scalar(
        select(func.coalesce(func.sum(models.PaymentAllocation.amount), 0))
        .join(models.Trip)
        .where(trip_filter)
    )
    result = money(income) - money(direct) - money(maintenance) - money(repairs)
    return {
        "year": year,
        "month": month,
        "trip_count": trip_count,
        "income": money(income),
        "trip_expenses": money(direct),
        "maintenance": money(maintenance),
        "repairs": money(repairs),
        "operating_result": money(result),
        "collected": money(collected),
        "pending": money(max(ZERO, money(income) - money(allocated))),
        "definition": "Ingresos de viajes completados menos gastos directos de esos viajes, mantenimientos y reparaciones del período.",
    }


def dashboard(db: Session, year: int, month: int) -> dict:
    report = monthly_report(db, year, month)
    receivable = ZERO
    balances: list[dict] = []
    for client in db.scalars(select(models.Client).where(models.Client.is_active.is_(True))).all():
        totals = client_totals(db, client.id)
        if totals["pending"] > ZERO:
            receivable += totals["pending"]
            balances.append({"id": client.id, "name": client.name, "pending": totals["pending"]})
    recent = db.scalars(
        select(models.Trip).options(joinedload(models.Trip.client), joinedload(models.Trip.vehicle), joinedload(models.Trip.driver))
        .order_by(models.Trip.trip_date.desc(), models.Trip.id.desc()).limit(6)
    ).all()
    report["accounts_receivable"] = money(receivable)
    report["top_debtors"] = sorted(balances, key=lambda x: x["pending"], reverse=True)[:5]
    report["recent_trips"] = [trip_dict(db, item) for item in recent]
    return report
