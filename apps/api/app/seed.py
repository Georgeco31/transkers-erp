from sqlalchemy import select

from app.config import get_settings
from app.database import SessionLocal
from app.models import TripExpenseCategory, User
from app.security import hash_password

CATEGORIES = ["Chofer", "Viático", "Combustible", "Peaje", "Carga", "Descarga", "Hospedaje", "Parqueadero", "Otros"]


def seed() -> None:
    settings = get_settings()
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.username == settings.admin_username))
        if not user:
            db.add(User(username=settings.admin_username, password_hash=hash_password(settings.admin_password), role="admin"))
        existing = set(db.scalars(select(TripExpenseCategory.name)).all())
        for name in CATEGORIES:
            if name not in existing:
                db.add(TripExpenseCategory(name=name))
        db.commit()


if __name__ == "__main__":
    seed()

