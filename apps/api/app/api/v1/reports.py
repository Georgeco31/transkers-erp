from datetime import date

from fastapi import APIRouter
from sqlalchemy import func, select

from app import models, services
from app.dependencies import CurrentUser, DbSession

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/monthly")
def monthly(year: int, month: int, db: DbSession, _: CurrentUser) -> dict:
    return services.monthly_report(db, year, month)


@router.get("/clients")
def clients_report(db: DbSession, _: CurrentUser) -> list[dict]:
    result = []
    for client in db.scalars(select(models.Client).order_by(models.Client.name)).all():
        result.append({"client_id": client.id, "client_name": client.name} | services.client_totals(db, client.id))
    return result


@router.get("/vehicles")
def vehicles_report(db: DbSession, _: CurrentUser) -> list[dict]:
    result = []
    for vehicle in db.scalars(select(models.Vehicle).order_by(models.Vehicle.plate)).all():
        trips = db.scalars(select(models.Trip).where(models.Trip.vehicle_id == vehicle.id, models.Trip.status == "completed")).all()
        income = services.money(sum((x.agreed_price for x in trips), services.ZERO))
        direct = services.money(sum((services.trip_expense_total(db, x.id) for x in trips), services.ZERO))
        maintenance = services.money(db.scalar(select(func.coalesce(func.sum(models.VehicleExpense.amount), 0)).where(
            models.VehicleExpense.vehicle_id == vehicle.id, models.VehicleExpense.expense_type == "maintenance")))
        repairs = services.money(db.scalar(select(func.coalesce(func.sum(models.VehicleExpense.amount), 0)).where(
            models.VehicleExpense.vehicle_id == vehicle.id, models.VehicleExpense.expense_type == "repair")))
        result.append({"vehicle_id": vehicle.id, "plate": vehicle.plate, "trip_count": len(trips), "income": income,
            "direct_expenses": direct, "maintenance": maintenance, "repairs": repairs,
            "operating_result": services.money(income - direct - maintenance - repairs)})
    return result


@router.get("/receivables")
def receivables(db: DbSession, _: CurrentUser) -> list[dict]:
    today = date.today()
    result = []
    for client in db.scalars(select(models.Client).order_by(models.Client.name)).all():
        pending_trips = []
        for trip in db.scalars(select(models.Trip).where(
            models.Trip.client_id == client.id, models.Trip.status == "completed"
        ).order_by(models.Trip.trip_date)).all():
            pending = services.money(trip.agreed_price - services.trip_allocated_total(db, trip.id))
            if pending > services.ZERO:
                pending_trips.append({"trip_id": trip.id, "code": trip.code, "trip_date": trip.trip_date,
                                      "pending": pending, "age_days": max(0, (today - trip.trip_date).days)})
        if pending_trips:
            result.append({"client_id": client.id, "client_name": client.name,
                "pending_trip_count": len(pending_trips),
                "pending": services.money(sum((x["pending"] for x in pending_trips), services.ZERO)),
                "oldest_age_days": max(x["age_days"] for x in pending_trips), "trips": pending_trips})
    return sorted(result, key=lambda x: (x["oldest_age_days"], x["pending"]), reverse=True)


@router.get("/dashboard")
def dashboard(year: int, month: int, db: DbSession, _: CurrentUser) -> dict:
    return services.dashboard(db, year, month)

