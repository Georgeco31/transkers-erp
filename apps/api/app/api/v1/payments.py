from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app import models, schemas, services
from app.dependencies import CurrentUser, DbSession

router = APIRouter(prefix="/payments", tags=["payments"])


def payment_json(db: DbSession, payment: models.ClientPayment) -> dict:
    allocated = services.payment_allocated_total(db, payment.id)
    return {"id": payment.id, "client_id": payment.client_id, "client_name": payment.client.name,
        "payment_date": payment.payment_date, "amount": payment.amount, "allocated": allocated,
        "unapplied": services.money(payment.amount - allocated), "payment_method": payment.payment_method,
        "reference": payment.reference, "notes": payment.notes, "created_at": payment.created_at}


@router.get("")
def list_payments(db: DbSession, _: CurrentUser, client_id: int | None = None) -> list[dict]:
    stmt = select(models.ClientPayment).options(joinedload(models.ClientPayment.client))
    if client_id: stmt = stmt.where(models.ClientPayment.client_id == client_id)
    payments = db.scalars(stmt.order_by(models.ClientPayment.payment_date.desc(), models.ClientPayment.id.desc())).all()
    return [payment_json(db, p) for p in payments]


@router.post("", status_code=201)
def create_payment(payload: schemas.PaymentInput, db: DbSession, user: CurrentUser) -> dict:
    client = db.get(models.Client, payload.client_id)
    if not client or not client.is_active: raise HTTPException(422, "El cliente no existe o está inactivo.")
    data = payload.model_dump(exclude={"auto_allocate"})
    payment = models.ClientPayment(**data, created_by=user.id)
    db.add(payment); db.flush()
    if payload.auto_allocate: services.allocate_payment(db, payment)
    db.commit()
    payment.client = client
    return payment_json(db, payment)


@router.get("/{payment_id}")
def get_payment(payment_id: int, db: DbSession, _: CurrentUser) -> dict:
    payment = db.scalar(select(models.ClientPayment).options(joinedload(models.ClientPayment.client)).where(models.ClientPayment.id == payment_id))
    if not payment: raise HTTPException(404, "Pago no encontrado.")
    result = payment_json(db, payment)
    allocations = db.scalars(select(models.PaymentAllocation).options(joinedload(models.PaymentAllocation.trip)).where(models.PaymentAllocation.payment_id == payment_id)).all()
    result["allocations"] = [{"id": x.id, "trip_id": x.trip_id, "trip_code": x.trip.code, "amount": x.amount} for x in allocations]
    return result


@router.post("/{payment_id}/allocations", status_code=201)
def create_allocation(payment_id: int, payload: schemas.AllocationInput, db: DbSession, _: CurrentUser) -> dict:
    payment, trip = db.get(models.ClientPayment, payment_id), db.get(models.Trip, payload.trip_id)
    if not payment: raise HTTPException(404, "Pago no encontrado.")
    if not trip: raise HTTPException(404, "Viaje no encontrado.")
    allocation = services.add_manual_allocation(db, payment, trip, payload.amount)
    db.commit()
    return {"id": allocation.id, "payment_id": payment.id, "trip_id": trip.id, "amount": allocation.amount}

