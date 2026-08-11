def test_mandatory_business_acceptance_scenario(client):
    company = client.post("/api/v1/clients", json={"name": "Grupo Prueba"}).json()
    driver = client.post("/api/v1/drivers", json={"name": "Carlos Prueba"}).json()
    vehicle = client.post("/api/v1/vehicles", json={"plate": "TRK-001"}).json()
    categories = {x["name"]: x["id"] for x in client.get("/api/v1/trip-expense-categories").json()}

    trips = []
    for day, price, costs in [
        ("2026-08-03", "500.00", [("Chofer", "70.00"), ("Viático", "30.00"), ("Combustible", "100.00")]),
        ("2026-08-04", "700.00", [("Chofer", "80.00"), ("Viático", "40.00"), ("Combustible", "150.00")]),
    ]:
        trip = client.post("/api/v1/trips", json={"trip_date": day, "client_id": company["id"],
            "vehicle_id": vehicle["id"], "driver_id": driver["id"], "agreed_price": price, "status": "completed"}).json()
        trips.append(trip)
        for category, amount in costs:
            assert client.post("/api/v1/trip-expenses", json={"trip_id": trip["id"], "category_id": categories[category],
                "expense_date": day, "amount": amount}).status_code == 201

    assert client.get(f"/api/v1/trips/{trips[0]['id']}").json()["margin"] == "300.00"
    assert client.get(f"/api/v1/trips/{trips[1]['id']}").json()["margin"] == "430.00"
    for kind, amount in [("maintenance", "100.00"), ("repair", "50.00")]:
        assert client.post("/api/v1/vehicle-expenses", json={"vehicle_id": vehicle["id"], "expense_type": kind,
            "expense_date": "2026-08-10", "amount": amount, "description": kind}).status_code == 201
    payment = client.post("/api/v1/payments", json={"client_id": company["id"], "payment_date": "2026-08-11", "amount": "800.00"})
    assert payment.status_code == 201

    monthly = client.get("/api/v1/reports/monthly?year=2026&month=8").json()
    assert monthly["trip_count"] == 2
    assert monthly["income"] == "1200.00"
    assert monthly["trip_expenses"] == "470.00"
    assert monthly["maintenance"] == "100.00"
    assert monthly["repairs"] == "50.00"
    assert monthly["operating_result"] == "580.00"
    assert monthly["collected"] == "800.00"
    assert monthly["pending"] == "400.00"

    dashboard = client.get("/api/v1/reports/dashboard?year=2026&month=8").json()
    assert dashboard["operating_result"] == "580.00"
    assert dashboard["accounts_receivable"] == "400.00"
    client_detail = client.get(f"/api/v1/clients/{company['id']}").json()
    assert client_detail["trip_count"] == 2
    assert client_detail["pending"] == "400.00"
    vehicle_report = next(x for x in client.get("/api/v1/reports/vehicles").json() if x["vehicle_id"] == vehicle["id"])
    assert vehicle_report["trip_count"] == 2
    assert vehicle_report["operating_result"] == "580.00"
