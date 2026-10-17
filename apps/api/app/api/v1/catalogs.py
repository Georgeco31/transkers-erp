from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError

from app import models, schemas, services
from app.dependencies import CurrentUser, DbSession

router = APIRouter(tags=["catalogs"])


def client_json(item: models.Client) -> dict:
    return {"id": item.id, "name": item.name, "tax_id": item.tax_id, "phone": item.phone, "notes": item.notes,
            "is_active": item.is_active, "created_at": item.created_at, "updated_at": item.updated_at}


def driver_json(item: models.Driver) -> dict:
    return {"id": item.id, "name": item.name, "is_active": item.is_active,
            "created_at": item.created_at, "updated_at": item.updated_at}


def vehicle_json(item: models.Vehicle) -> dict:
    return {"id": item.id, "plate": item.plate, "brand": item.brand, "model": item.model, "year": item.year,
            "notes": item.notes, "is_active": item.is_active, "created_at": item.created_at, "updated_at": item.updated_at}


@router.get("/clients")
def clients(db: DbSession, _: CurrentUser, search: str = "", active: bool | None = None) -> list[dict]:
    stmt = select(models.Client)
    if search:
        stmt = stmt.where(or_(models.Client.name.ilike(f"%{search}%"), models.Client.tax_id.ilike(f"%{search}%")))
    if active is not None:
        stmt = stmt.where(models.Client.is_active == active)
    return [client_json(x) | services.client_totals(db, x.id) for x in db.scalars(stmt.order_by(models.Client.name)).all()]


@router.post("/clients", status_code=201)
def create_client(payload: schemas.ClientInput, db: DbSession, _: CurrentUser) -> dict:
    item = models.Client(**payload.model_dump())
    item.name = item.name.strip()
    db.add(item); db.commit(); db.refresh(item)
    return client_json(item)


@router.get("/clients/{item_id}")
def get_client(item_id: int, db: DbSession, _: CurrentUser) -> dict:
    item = db.get(models.Client, item_id)
    if not item: raise HTTPException(404, "Cliente no encontrado.")
    trips = db.scalars(select(models.Trip).where(models.Trip.client_id == item_id).order_by(models.Trip.trip_date.desc())).all()
    payments = db.scalars(select(models.ClientPayment).where(models.ClientPayment.client_id == item_id).order_by(models.ClientPayment.payment_date.desc())).all()
    return client_json(item) | services.client_totals(db, item.id) | {
        "trips": [services.trip_dict(db, x) for x in trips],
        "payments": [{"id": p.id, "payment_date": p.payment_date, "amount": p.amount,
                      "allocated": services.payment_allocated_total(db, p.id), "reference": p.reference} for p in payments],
    }


@router.put("/clients/{item_id}")
def update_client(item_id: int, payload: schemas.ClientInput, db: DbSession, _: CurrentUser) -> dict:
    item = db.get(models.Client, item_id)
    if not item: raise HTTPException(404, "Cliente no encontrado.")
    for key, value in payload.model_dump().items(): setattr(item, key, value.strip() if key == "name" else value)
    db.commit(); return client_json(item)


@router.get("/drivers")
def drivers(db: DbSession, _: CurrentUser, search: str = "", active: bool | None = None) -> list[dict]:
    stmt = select(models.Driver)
    if search: stmt = stmt.where(models.Driver.name.ilike(f"%{search}%"))
    if active is not None: stmt = stmt.where(models.Driver.is_active == active)
    return [driver_json(x) for x in db.scalars(stmt.order_by(models.Driver.name)).all()]


@router.post("/drivers", status_code=201)
def create_driver(payload: schemas.DriverInput, db: DbSession, _: CurrentUser) -> dict:
    item = models.Driver(name=payload.name.strip(), is_active=payload.is_active)
    db.add(item); db.commit(); return driver_json(item)


@router.get("/drivers/{item_id}")
def get_driver(item_id: int, db: DbSession, _: CurrentUser) -> dict:
    item = db.get(models.Driver, item_id)
    if not item: raise HTTPException(404, "Chofer no encontrado.")
    trips = db.scalars(select(models.Trip).where(models.Trip.driver_id == item_id).order_by(models.Trip.trip_date.desc())).all()
    return driver_json(item) | {"trips": [services.trip_dict(db, x) for x in trips]}


@router.put("/drivers/{item_id}")
def update_driver(item_id: int, payload: schemas.DriverInput, db: DbSession, _: CurrentUser) -> dict:
    item = db.get(models.Driver, item_id)
    if not item: raise HTTPException(404, "Chofer no encontrado.")
    item.name, item.is_active = payload.name.strip(), payload.is_active
    db.commit(); return driver_json(item)


@router.get("/vehicles")
def vehicles(db: DbSession, _: CurrentUser, search: str = "", active: bool | None = None) -> list[dict]:
    stmt = select(models.Vehicle)
    if search: stmt = stmt.where(or_(models.Vehicle.plate.ilike(f"%{search}%"), models.Vehicle.brand.ilike(f"%{search}%"), models.Vehicle.model.ilike(f"%{search}%")))
    if active is not None: stmt = stmt.where(models.Vehicle.is_active == active)
    return [vehicle_json(x) for x in db.scalars(stmt.order_by(models.Vehicle.plate)).all()]


@router.post("/vehicles", status_code=201)
def create_vehicle(payload: schemas.VehicleInput, db: DbSession, _: CurrentUser) -> dict:
    item = models.Vehicle(**payload.model_dump())
    db.add(item)
    try: db.commit()
    except IntegrityError:
        db.rollback(); raise HTTPException(409, "Ya existe un vehículo con esa placa.")
    return vehicle_json(item)


@router.get("/vehicles/{item_id}")
def get_vehicle(item_id: int, db: DbSession, _: CurrentUser) -> dict:
    item = db.get(models.Vehicle, item_id)
    if not item: raise HTTPException(404, "Vehículo no encontrado.")
    trips = db.scalars(select(models.Trip).where(models.Trip.vehicle_id == item_id).order_by(models.Trip.trip_date.desc())).all()
    expenses = db.scalars(select(models.VehicleExpense).where(models.VehicleExpense.vehicle_id == item_id).order_by(models.VehicleExpense.expense_date.desc())).all()
    completed = [x for x in trips if x.status == "completed"]
    income = services.money(sum((x.agreed_price for x in completed), services.ZERO))
    direct = services.money(sum((services.trip_expense_total(db, x.id) for x in completed), services.ZERO))
    maintenance = services.money(sum((x.amount for x in expenses if x.expense_type == "maintenance"), services.ZERO))
    repairs = services.money(sum((x.amount for x in expenses if x.expense_type == "repair"), services.ZERO))
    return vehicle_json(item) | {"trip_count": len(completed), "income": income, "direct_expenses": direct,
        "maintenance": maintenance, "repairs": repairs, "operating_result": services.money(income-direct-maintenance-repairs),
        "trips": [services.trip_dict(db, x) for x in trips],
        "expenses": [{"id": x.id, "expense_type": x.expense_type, "expense_date": x.expense_date,
                      "amount": x.amount, "description": x.description, "odometer": x.odometer} for x in expenses]}


@router.put("/vehicles/{item_id}")
def update_vehicle(item_id: int, payload: schemas.VehicleInput, db: DbSession, _: CurrentUser) -> dict:
    item = db.get(models.Vehicle, item_id)
    if not item: raise HTTPException(404, "Vehículo no encontrado.")
    for key, value in payload.model_dump().items(): setattr(item, key, value)
    try: db.commit()
    except IntegrityError:
        db.rollback(); raise HTTPException(409, "Ya existe un vehículo con esa placa.")
    return vehicle_json(item)

