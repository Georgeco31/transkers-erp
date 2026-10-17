from fastapi import APIRouter, HTTPException, Response
from sqlalchemy import select

from app.config import get_settings
from app.dependencies import CurrentUser, DbSession
from app.models import User
from app.schemas import LoginRequest
from app.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(payload: LoginRequest, response: Response, db: DbSession) -> dict:
    user = db.scalar(select(User).where(User.username == payload.username.strip()))
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Usuario o contraseña incorrectos.")
    settings = get_settings()
    response.set_cookie(
        "transker_session",
        create_access_token(user.id),
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )
    return {"id": user.id, "username": user.username, "role": user.role}


@router.post("/logout")
def logout(response: Response) -> dict[str, bool]:
    response.delete_cookie("transker_session", path="/")
    return {"ok": True}


@router.get("/me")
def me(user: CurrentUser) -> dict:
    return {"id": user.id, "username": user.username, "role": user.role}

