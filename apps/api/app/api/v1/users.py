from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.dependencies import AdminUser, DbSession
from app.models import User
from app.schemas import UserCreate
from app.security import hash_password

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
def list_users(_: AdminUser, db: DbSession) -> list[dict]:
    return [
        {"id": u.id, "username": u.username, "role": u.role, "is_active": u.is_active, "created_at": u.created_at}
        for u in db.scalars(select(User).order_by(User.username)).all()
    ]


@router.post("", status_code=201)
def create_user(payload: UserCreate, _: AdminUser, db: DbSession) -> dict:
    username = payload.username.strip()
    if db.scalar(select(User).where(User.username == username)):
        raise HTTPException(409, "Ya existe un usuario con ese nombre.")
    user = User(username=username, password_hash=hash_password(payload.password), role=payload.role)
    db.add(user)
    db.commit()
    return {"id": user.id, "username": user.username, "role": user.role, "is_active": user.is_active}

