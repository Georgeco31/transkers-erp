from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import SessionLocal
from app.models import User
from app.security import hash_password


class AdminRotationError(RuntimeError):
    """Raised when administrator credentials cannot be rotated safely."""


def rotate_admin_credentials(db: Session, username: str, password: str) -> int:
    normalized_username = username.strip()
    if not 3 <= len(normalized_username) <= 80:
        raise AdminRotationError("El usuario debe tener entre 3 y 80 caracteres.")
    if len(password) < 12:
        raise AdminRotationError("La contraseña debe tener al menos 12 caracteres.")

    administrators = db.scalars(select(User).where(User.role == "admin").with_for_update()).all()
    if len(administrators) != 1:
        raise AdminRotationError("La rotación requiere exactamente un usuario administrador existente.")

    administrator = administrators[0]
    conflicting_user = db.scalar(
        select(User).where(User.username == normalized_username, User.id != administrator.id)
    )
    if conflicting_user:
        raise AdminRotationError("El nuevo nombre de usuario ya está en uso.")

    administrator.username = normalized_username
    administrator.password_hash = hash_password(password)
    administrator.is_active = True
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise AdminRotationError("No fue posible actualizar las credenciales del administrador.") from exc
    return administrator.id


def main() -> None:
    settings = get_settings()
    with SessionLocal() as db:
        rotate_admin_credentials(db, settings.admin_username, settings.admin_password)
    print("Credenciales del administrador actualizadas correctamente.")


if __name__ == "__main__":
    main()

