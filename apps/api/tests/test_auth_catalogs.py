def test_login_rejects_bad_credentials(client):
    response = client.post("/api/v1/auth/login", json={"username": "admin", "password": "incorrecta"})
    assert response.status_code == 401


def test_protected_route_requires_cookie(client):
    client.cookies.clear()
    assert client.get("/api/v1/clients").status_code == 401


def test_client_create_edit_and_deactivate(client):
    created = client.post("/api/v1/clients", json={"name": "Acme", "phone": "123"})
    assert created.status_code == 201
    item = created.json()
    updated = client.put(f"/api/v1/clients/{item['id']}", json={"name": "Acme Logística", "is_active": False})
    assert updated.status_code == 200
    assert updated.json()["name"] == "Acme Logística"
    assert updated.json()["is_active"] is False


def test_driver_allows_duplicate_names_and_edit(client):
    first = client.post("/api/v1/drivers", json={"name": "Carlos"})
    second = client.post("/api/v1/drivers", json={"name": "Carlos"})
    assert first.status_code == second.status_code == 201
    changed = client.put(f"/api/v1/drivers/{first.json()['id']}", json={"name": "Carlos A.", "is_active": False})
    assert changed.json()["name"] == "Carlos A."


def test_vehicle_plate_is_normalized_unique_and_editable(client):
    first = client.post("/api/v1/vehicles", json={"plate": "abc 123"})
    assert first.json()["plate"] == "ABC123"
    duplicate = client.post("/api/v1/vehicles", json={"plate": "ABC123"})
    assert duplicate.status_code == 409
    changed = client.put(f"/api/v1/vehicles/{first.json()['id']}", json={"plate": "ABC123", "brand": "Hino", "is_active": True})
    assert changed.json()["brand"] == "Hino"

