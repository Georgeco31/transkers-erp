from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.security import decode_access_token

DbSession = Annotated[Session, Depends(get_db)]


def current_user(
    db: DbSession, transker_session: Annotated[str | None, Cookie()] = None
) -> User:
    user_id = decode_access_token(transker_session or "")
    user = db.get(User, user_id) if user_id else None
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión inválida o vencida.")
    return user


CurrentUser = Annotated[User, Depends(current_user)]


def admin_user(user: CurrentUser) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Se requiere permiso de administrador.")
    return user


AdminUser = Annotated[User, Depends(admin_user)]

