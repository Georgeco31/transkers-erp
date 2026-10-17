from decimal import Decimal

import pytest

from app import services


def create_trip(client, records, price: str, trip_date: str):
    company, driver, vehicle = records
    response = client.post("/api/v1/trips", json={
        "trip_date": trip_date,
        "client_id": company["id"],
        "vehicle_id": vehicle["id"],
        "driver_id": driver["id"],
        "agreed_price": price,
        "status": "completed",
    })
    assert response.status_code == 201
    return response.json()


def test_vehicle_expense_edit_moves_period_and_preserves_identity(client, base_records):
    vehicle = base_records[2]
    created = client.post("/api/v1/vehicle-expenses", json={
        "vehicle_id": vehicle["id"],
        "expense_type": "repair",
        "expense_date": "2026-09-15",
        "amount": "500.00",
        "description": "Reparación inicial",
        "odometer": 120000,
    }).json()
    original_id = created["id"]
    original_created_at = created["created_at"]
    assert client.get("/api/v1/reports/monthly?year=2026&month=9").json()["repairs"] == "500.00"

    response = client.put(f"/api/v1/vehicle-expenses/{original_id}", json={
        "vehicle_id": vehicle["id"],
        "expense_type": "repair",
        "expense_date": "2026-10-15",
        "amount": "500.00",
        "description": "Reparación corregida",
        "odometer": 120100,
    })
    assert response.status_code == 200
    updated = response.json()
    assert updated["id"] == original_id
    assert updated["created_at"].rstrip("Z") == original_created_at.rstrip("Z")
    assert updated["updated_at"]
    assert client.get("/api/v1/reports/monthly?year=2026&month=9").json()["repairs"] == "0.00"
    october = client.get("/api/v1/reports/monthly?year=2026&month=10").json()
    assert october["repairs"] == "500.00"
    assert october["operating_result"] == "-500.00"
    assert len(client.get("/api/v1/vehicle-expenses").json()) == 1


def test_vehicle_expense_edit_changes_amount_without_duplication(client, base_records):
    vehicle = base_records[2]
    expense = client.post("/api/v1/vehicle-expenses", json={
        "vehicle_id": vehicle["id"],
        "expense_type": "maintenance",
        "expense_date": "2026-10-10",
        "amount": "100.00",
        "description": "Aceite",
    }).json()
    response = client.put(f"/api/v1/vehicle-expenses/{expense['id']}", json={
        "vehicle_id": vehicle["id"],
        "expense_type": "maintenance",
        "expense_date": "2026-10-10",
        "amount": "150.00",
        "description": "Aceite y filtros",
        "odometer": None,
    })
    assert response.status_code == 200
    assert response.json()["amount"] == "150.00"
    assert client.get("/api/v1/reports/monthly?year=2026&month=10").json()["maintenance"] == "150.00"
    assert [x["id"] for x in client.get("/api/v1/vehicle-expenses").json()] == [expense["id"]]


def test_payment_date_edit_moves_collection_period_not_receivable(client, base_records):
    create_trip(client, base_records, "1200.00", "2026-09-01")
    payment = client.post("/api/v1/payments", json={
        "client_id": base_records[0]["id"],
        "payment_date": "2026-09-30",
        "amount": "800.00",
    }).json()
    before = client.get(f"/api/v1/clients/{base_records[0]['id']}").json()
    assert client.get("/api/v1/reports/monthly?year=2026&month=9").json()["collected"] == "800.00"

    response = client.put(f"/api/v1/payments/{payment['id']}", json={
        "payment_date": "2026-10-02",
        "amount": "800.00",
        "payment_method": "Transferencia",
        "reference": "REF-001",
        "notes": "Fecha corregida",
    })
    assert response.status_code == 200
    updated = response.json()
    assert updated["id"] == payment["id"]
    assert updated["created_at"].rstrip("Z") == payment["created_at"].rstrip("Z")
    assert updated["payment_method"] == "Transferencia"
    assert updated["reference"] == "REF-001"
    assert updated["notes"] == "Fecha corregida"
    assert client.get("/api/v1/reports/monthly?year=2026&month=9").json()["collected"] == "0.00"
    assert client.get("/api/v1/reports/monthly?year=2026&month=10").json()["collected"] == "800.00"
    after = client.get(f"/api/v1/clients/{base_records[0]['id']}").json()
    assert after["pending"] == before["pending"] == "400.00"
    assert len(after["payments"]) == 1

    forbidden_client_change = client.put(f"/api/v1/payments/{payment['id']}", json={
        "client_id": base_records[0]["id"],
        "payment_date": "2026-10-02",
        "amount": "800.00",
        "payment_method": None,
        "reference": None,
        "notes": None,
    })
    assert forbidden_client_change.status_code == 422


@pytest.mark.parametrize(
    ("new_amount", "expected_allocations", "pending", "credit"),
    [
        ("600.00", ["500.00", "100.00"], "600.00", "0.00"),
        ("1000.00", ["500.00", "500.00"], "200.00", "0.00"),
        ("1300.00", ["500.00", "700.00"], "0.00", "100.00"),
    ],
)
def test_payment_amount_edit_reallocates_fifo(
    client, base_records, new_amount, expected_allocations, pending, credit
):
    trip1 = create_trip(client, base_records, "500.00", "2026-10-01")
    trip2 = create_trip(client, base_records, "700.00", "2026-10-02")
    payment = client.post("/api/v1/payments", json={
        "client_id": base_records[0]["id"],
        "payment_date": "2026-10-03",
        "amount": "800.00",
    }).json()

    response = client.put(f"/api/v1/payments/{payment['id']}", json={
        "payment_date": "2026-10-03",
        "amount": new_amount,
        "payment_method": "Efectivo",
        "reference": None,
        "notes": None,
    })
    assert response.status_code == 200
    updated = response.json()
    detail = client.get(f"/api/v1/payments/{payment['id']}").json()
    assert updated["id"] == payment["id"]
    assert updated["amount"] == new_amount
    assert [x["trip_id"] for x in detail["allocations"]] == [trip1["id"], trip2["id"]]
    assert [x["amount"] for x in detail["allocations"]] == expected_allocations
    assert sum(Decimal(x["amount"]) for x in detail["allocations"]) <= Decimal(new_amount)
    assert Decimal(client.get(f"/api/v1/trips/{trip1['id']}").json()["allocated"]) <= Decimal(trip1["agreed_price"])
    assert Decimal(client.get(f"/api/v1/trips/{trip2['id']}").json()["allocated"]) <= Decimal(trip2["agreed_price"])
    totals = client.get(f"/api/v1/clients/{base_records[0]['id']}").json()
    assert totals["pending"] == pending
    assert totals["credit"] == credit
    assert updated["unapplied"] == credit
    assert len(client.get("/api/v1/payments").json()) == 1


def test_payment_edit_rolls_back_amount_and_allocations_on_failure(client, base_records, monkeypatch):
    create_trip(client, base_records, "500.00", "2026-10-01")
    create_trip(client, base_records, "700.00", "2026-10-02")
    payment = client.post("/api/v1/payments", json={
        "client_id": base_records[0]["id"],
        "payment_date": "2026-10-03",
        "amount": "800.00",
    }).json()
    before = client.get(f"/api/v1/payments/{payment['id']}").json()
    original = services.reallocate_payment

    def fail_after_reallocation(db, item):
        original(db, item)
        raise RuntimeError("forced rollback")

    monkeypatch.setattr(services, "reallocate_payment", fail_after_reallocation)
    with pytest.raises(RuntimeError, match="forced rollback"):
        client.put(f"/api/v1/payments/{payment['id']}", json={
            "payment_date": "2026-10-04",
            "amount": "600.00",
            "payment_method": None,
            "reference": None,
            "notes": None,
        })
    monkeypatch.setattr(services, "reallocate_payment", original)

    after = client.get(f"/api/v1/payments/{payment['id']}").json()
    assert after["amount"] == before["amount"] == "800.00"
    assert after["payment_date"] == before["payment_date"] == "2026-10-03"
    assert [(x["trip_id"], x["amount"]) for x in after["allocations"]] == [
        (x["trip_id"], x["amount"]) for x in before["allocations"]
    ]
