from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from app import models, schemas, services
from app.dependencies import AdminUser, CurrentUser, DbSession

router = APIRouter(tags=["expenses"])


def vehicle_expense_json(item: models.VehicleExpense) -> dict:
    return {
        "id": item.id,
        "vehicle_id": item.vehicle_id,
        "vehicle_plate": item.vehicle.plate,
        "expense_type": item.expense_type,
        "expense_date": item.expense_date,
        "amount": item.amount,
        "description": item.description,
        "odometer": item.odometer,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
    }


@router.get("/trip-expense-categories")
def list_categories(db: DbSession, _: CurrentUser, active: bool | None = None) -> list[dict]:
    stmt = select(models.TripExpenseCategory)
    if active is not None: stmt = stmt.where(models.TripExpenseCategory.is_active == active)
    return [{"id": x.id, "name": x.name, "is_active": x.is_active} for x in db.scalars(stmt.order_by(models.TripExpenseCategory.name)).all()]


@router.post("/trip-expense-categories", status_code=201)
def create_category(payload: schemas.CategoryInput, db: DbSession, _: AdminUser) -> dict:
    item = models.TripExpenseCategory(name=payload.name.strip(), is_active=payload.is_active)
    db.add(item)
    try: db.commit()
    except IntegrityError:
        db.rollback(); raise HTTPException(409, "Ya existe una categoría con ese nombre.")
    return {"id": item.id, "name": item.name, "is_active": item.is_active}


@router.get("/trip-expenses")
def list_trip_expenses(db: DbSession, _: CurrentUser, trip_id: int | None = None) -> list[dict]:
    stmt = select(models.TripExpense).options(joinedload(models.TripExpense.category), joinedload(models.TripExpense.trip))
    if trip_id: stmt = stmt.where(models.TripExpense.trip_id == trip_id)
    return [{"id": x.id, "trip_id": x.trip_id, "trip_code": x.trip.code, "category_id": x.category_id,
        "category_name": x.category.name, "expense_date": x.expense_date, "amount": x.amount,
        "description": x.description} for x in db.scalars(stmt.order_by(models.TripExpense.expense_date.desc())).all()]


@router.post("/trip-expenses", status_code=201)
def create_trip_expense(payload: schemas.TripExpenseInput, db: DbSession, user: CurrentUser) -> dict:
    trip, category = db.get(models.Trip, payload.trip_id), db.get(models.TripExpenseCategory, payload.category_id)
    if not trip: raise HTTPException(422, "El viaje no existe.")
    if not category or not category.is_active: raise HTTPException(422, "La categoría no existe o está inactiva.")
    if trip.status == "cancelled": raise HTTPException(422, "No se pueden registrar gastos en un viaje cancelado.")
    item = models.TripExpense(**payload.model_dump(), created_by=user.id)
    db.add(item); db.commit()
    return {"id": item.id, **payload.model_dump(), "category_name": category.name}


@router.put("/trip-expenses/{item_id}")
def update_trip_expense(item_id: int, payload: schemas.TripExpenseInput, db: DbSession, _: CurrentUser) -> dict:
    item = db.get(models.TripExpense, item_id)
    if not item: raise HTTPException(404, "Gasto no encontrado.")
    trip, category = db.get(models.Trip, payload.trip_id), db.get(models.TripExpenseCategory, payload.category_id)
    if not trip or trip.status == "cancelled": raise HTTPException(422, "El viaje no existe o está cancelado.")
    if not category: raise HTTPException(422, "La categoría no existe.")
    for key, value in payload.model_dump().items(): setattr(item, key, value)
    db.commit()
    return {"id": item.id, **payload.model_dump(), "category_name": category.name}


@router.get("/vehicle-expenses")
def list_vehicle_expenses(db: DbSession, _: CurrentUser, vehicle_id: int | None = None, expense_type: str | None = None) -> list[dict]:
    stmt = select(models.VehicleExpense).options(joinedload(models.VehicleExpense.vehicle))
    if vehicle_id: stmt = stmt.where(models.VehicleExpense.vehicle_id == vehicle_id)
    if expense_type: stmt = stmt.where(models.VehicleExpense.expense_type == expense_type)
    return [vehicle_expense_json(x) for x in db.scalars(
        stmt.order_by(models.VehicleExpense.expense_date.desc(), models.VehicleExpense.id.desc())
    ).all()]


@router.get("/vehicle-expenses/{item_id}")
def get_vehicle_expense(item_id: int, db: DbSession, _: CurrentUser) -> dict:
    item = db.scalar(
        select(models.VehicleExpense)
        .options(joinedload(models.VehicleExpense.vehicle))
        .where(models.VehicleExpense.id == item_id)
    )
    if not item:
        raise HTTPException(404, "Gasto vehicular no encontrado.")
    return vehicle_expense_json(item)


@router.post("/vehicle-expenses", status_code=201)
def create_vehicle_expense(payload: schemas.VehicleExpenseInput, db: DbSession, user: CurrentUser) -> dict:
    vehicle = db.get(models.Vehicle, payload.vehicle_id)
    if not vehicle or not vehicle.is_active: raise HTTPException(422, "El vehículo no existe o está inactivo.")
    item = models.VehicleExpense(**payload.model_dump(), created_by=user.id)
    db.add(item); db.commit()
    item.vehicle = vehicle
    return vehicle_expense_json(item)


@router.put("/vehicle-expenses/{item_id}")
def update_vehicle_expense(item_id: int, payload: schemas.VehicleExpenseInput, db: DbSession, _: CurrentUser) -> dict:
    item, vehicle = db.get(models.VehicleExpense, item_id), db.get(models.Vehicle, payload.vehicle_id)
    if not item: raise HTTPException(404, "Gasto vehicular no encontrado.")
    if not vehicle: raise HTTPException(422, "El vehículo no existe.")
    for key, value in payload.model_dump().items(): setattr(item, key, value)
    db.commit()
    item.vehicle = vehicle
    return vehicle_expense_json(item)
