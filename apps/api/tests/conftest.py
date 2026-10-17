import os

os.environ["DATABASE_URL"] = "sqlite:///./test_transker.db"
os.environ["SECRET_KEY"] = "test-secret-key-with-more-than-thirty-two-characters"
os.environ["ADMIN_USERNAME"] = "admin"
os.environ["ADMIN_PASSWORD"] = "test-password"

import pytest
from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import TripExpenseCategory, User
from app.security import hash_password


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.add(User(username="admin", password_hash=hash_password("test-password"), role="admin"))
        for name in ["Chofer", "Viático", "Combustible", "Otros"]:
            db.add(TripExpenseCategory(name=name))
        db.commit()
    with TestClient(app) as test_client:
        response = test_client.post("/api/v1/auth/login", json={"username": "admin", "password": "test-password"})
        assert response.status_code == 200
        yield test_client


@pytest.fixture()
def base_records(client):
    company = client.post("/api/v1/clients", json={"name": "Cliente Base"}).json()
    driver = client.post("/api/v1/drivers", json={"name": "Chofer Base"}).json()
    vehicle = client.post("/api/v1/vehicles", json={"plate": "ABC-123", "brand": "Hino"}).json()
    return company, driver, vehicle

