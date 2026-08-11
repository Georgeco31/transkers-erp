from datetime import date

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app import models, schemas, services
from app.dependencies import CurrentUser, DbSession

router = APIRouter(prefix="/trips", tags=["trips"])


def get_trip_or_404(db: DbSession, trip_id: int) -> models.Trip:
    trip = db.scalar(
        select(models.Trip)
        .options(joinedload(models.Trip.client), joinedload(models.Trip.vehicle), joinedload(models.Trip.driver))
        .where(models.Trip.id == trip_id)
    )
    if not trip:
        raise HTTPException(404, "Viaje no encontrado.")
    return trip


@router.get("")
def list_trips(
    db: DbSession,
    _: CurrentUser,
    date_from: date | None = None,
    date_to: date | None = None,
    client_id: int | None = None,
    vehicle_id: int | None = None,
    driver_id: int | None = None,
    status: str | None = None,
) -> list[dict]:
    stmt = select(models.Trip).options(
        joinedload(models.Trip.client), joinedload(models.Trip.vehicle), joinedload(models.Trip.driver)
    )
    if date_from: stmt = stmt.where(models.Trip.trip_date >= date_from)
    if date_to: stmt = stmt.where(models.Trip.trip_date <= date_to)
    if client_id: stmt = stmt.where(models.Trip.client_id == client_id)
    if vehicle_id: stmt = stmt.where(models.Trip.vehicle_id == vehicle_id)
    if driver_id: stmt = stmt.where(models.Trip.driver_id == driver_id)
    if status: stmt = stmt.where(models.Trip.status == status)
    trips = db.scalars(stmt.order_by(models.Trip.trip_date.desc(), models.Trip.id.desc())).all()
    return [services.trip_dict(db, trip) for trip in trips]


@router.post("", status_code=201)
def create_trip(payload: schemas.TripInput, db: DbSession, user: CurrentUser) -> dict:
    services.require_relations(db, payload.client_id, payload.vehicle_id, payload.driver_id)
    data = payload.model_dump()
    trip = models.Trip(code="PENDING", created_by=user.id, **data)
    services.validate_trip_status(trip)
    db.add(trip); db.flush()
    trip.code = f"TRK-{trip.trip_date.year}-{trip.id:06d}"
    db.commit()
    return services.trip_dict(db, get_trip_or_404(db, trip.id))


@router.get("/{trip_id}")
def get_trip(trip_id: int, db: DbSession, _: CurrentUser) -> dict:
    trip = get_trip_or_404(db, trip_id)
    result = services.trip_dict(db, trip)
    expenses = db.scalars(
        select(models.TripExpense).options(joinedload(models.TripExpense.category))
        .where(models.TripExpense.trip_id == trip_id).order_by(models.TripExpense.expense_date, models.TripExpense.id)
    ).all()
    result["expenses"] = [
        {"id": x.id, "expense_date": x.expense_date, "amount": x.amount, "description": x.description,
         "category_id": x.category_id, "category_name": x.category.name} for x in expenses
    ]
    return result


@router.put("/{trip_id}")
def update_trip(trip_id: int, payload: schemas.TripInput, db: DbSession, _: CurrentUser) -> dict:
    trip = get_trip_or_404(db, trip_id)
    if services.trip_allocated_total(db, trip.id) > payload.agreed_price:
        raise HTTPException(422, "El precio no puede quedar por debajo del monto ya cobrado.")
    services.require_relations(db, payload.client_id, payload.vehicle_id, payload.driver_id)
    if services.trip_allocated_total(db, trip.id) > 0 and payload.client_id != trip.client_id:
        raise HTTPException(422, "No se puede cambiar el cliente de un viaje con pagos asignados.")
    for key, value in payload.model_dump().items(): setattr(trip, key, value)
    services.validate_trip_status(trip)
    db.commit()
    return services.trip_dict(db, get_trip_or_404(db, trip.id))


@router.patch("/{trip_id}/status")
def update_status(trip_id: int, payload: schemas.TripStatusInput, db: DbSession, _: CurrentUser) -> dict:
    trip = get_trip_or_404(db, trip_id)
    if payload.status == "cancelled" and services.trip_allocated_total(db, trip.id) > 0:
        raise HTTPException(422, "No se puede cancelar un viaje que tiene pagos asignados.")
    trip.status = payload.status
    services.validate_trip_status(trip)
    db.commit()
    return services.trip_dict(db, trip)

