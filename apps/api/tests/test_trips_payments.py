from decimal import Decimal


def new_trip(client, records, *, price="1000.00", status="draft", trip_date="2026-08-05"):
    company, driver, vehicle = records
    return client.post("/api/v1/trips", json={
        "trip_date": trip_date, "client_id": company["id"], "vehicle_id": vehicle["id"],
        "driver_id": driver["id"], "agreed_price": price, "status": status,
    })


def test_trip_lifecycle_and_driver_vehicle_associations(client, base_records):
    response = new_trip(client, base_records)
    assert response.status_code == 201
    trip = response.json()
    assert trip["code"].startswith("TRK-2026-")
    completed = client.patch(f"/api/v1/trips/{trip['id']}/status", json={"status": "completed"})
    assert completed.status_code == 200
    assert completed.json()["margin"] == "1000.00"
    driver = client.get(f"/api/v1/drivers/{base_records[1]['id']}").json()
    vehicle = client.get(f"/api/v1/vehicles/{base_records[2]['id']}").json()
    assert len(driver["trips"]) == len(vehicle["trips"]) == 1


def test_cancelled_trip_has_no_revenue_or_receivable(client, base_records):
    trip = new_trip(client, base_records, status="cancelled").json()
    assert trip["margin"] == "0.00"
    assert trip["pending"] == "0.00"


def test_multiple_expenses_recalculate_margin(client, base_records):
    trip = new_trip(client, base_records, status="completed").json()
    categories = client.get("/api/v1/trip-expense-categories").json()
    for category, amount in zip(categories[:3], ["100.00", "50.00", "200.00"]):
        response = client.post("/api/v1/trip-expenses", json={
            "trip_id": trip["id"], "category_id": category["id"], "expense_date": "2026-08-05", "amount": amount,
        })
        assert response.status_code == 201
    detail = client.get(f"/api/v1/trips/{trip['id']}").json()
    assert detail["expense_total"] == "350.00"
    assert detail["margin"] == "650.00"


def test_partial_full_multi_trip_and_credit_payment(client, base_records):
    trip1 = new_trip(client, base_records, price="500.00", status="completed", trip_date="2026-08-01").json()
    trip2 = new_trip(client, base_records, price="700.00", status="completed", trip_date="2026-08-02").json()
    payment = client.post("/api/v1/payments", json={
        "client_id": base_records[0]["id"], "payment_date": "2026-08-10", "amount": "1300.00"
    }).json()
    assert payment["allocated"] == "1200.00"
    assert payment["unapplied"] == "100.00"
    assert client.get(f"/api/v1/trips/{trip1['id']}").json()["pending"] == "0.00"
    assert client.get(f"/api/v1/trips/{trip2['id']}").json()["pending"] == "0.00"
    totals = client.get(f"/api/v1/clients/{base_records[0]['id']}").json()
    assert totals["paid"] == "1300.00"
    assert totals["credit"] == "100.00"


def test_manual_allocation_prevents_overallocation(client, base_records):
    trip = new_trip(client, base_records, price="500.00", status="completed").json()
    payment = client.post("/api/v1/payments", json={
        "client_id": base_records[0]["id"], "payment_date": "2026-08-10", "amount": "300.00", "auto_allocate": False
    }).json()
    ok = client.post(f"/api/v1/payments/{payment['id']}/allocations", json={"trip_id": trip["id"], "amount": "200.00"})
    assert ok.status_code == 201
    too_much = client.post(f"/api/v1/payments/{payment['id']}/allocations", json={"trip_id": trip["id"], "amount": "101.00"})
    assert too_much.status_code == 422

