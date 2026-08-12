from sqlalchemy import select

from app.admin_credentials import rotate_admin_credentials
from app.database import SessionLocal
from app.models import Client, User
from app.security import verify_password


def test_rotate_existing_admin_without_changing_business_data(client):
    created = client.post("/api/v1/clients", json={"name": "Cliente conservado"})
    assert created.status_code == 201

    with SessionLocal() as db:
        administrator = db.scalar(select(User).where(User.role == "admin"))
        assert administrator is not None
        original_id = administrator.id
        original_hash = administrator.password_hash
        rotate_admin_credentials(db, "nuevo.admin", "Nueva-clave-segura-2026")

    with SessionLocal() as db:
        administrator = db.scalar(select(User).where(User.role == "admin"))
        assert administrator is not None
        assert administrator.id == original_id
        assert administrator.username == "nuevo.admin"
        assert administrator.password_hash != original_hash
        assert verify_password("Nueva-clave-segura-2026", administrator.password_hash)
        assert not verify_password("test-password", administrator.password_hash)
        assert db.scalar(select(Client).where(Client.name == "Cliente conservado")) is not None

