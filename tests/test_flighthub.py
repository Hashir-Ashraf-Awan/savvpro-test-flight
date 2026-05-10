"""
FlightHub Test Suite
Tests: flight listing, search, booking creation, overbooking rule, cancellation
Run: pytest tests/ -v
"""

import pytest
import os
import sys
import tempfile

# Point to backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

# Use a temp DB for tests
os.environ["FLIGHTHUB_TEST"] = "1"

from fastapi.testclient import TestClient

# Patch DB path before importing app
import database

_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
database.DB_PATH = _tmp.name

from main import app

client = TestClient(app)


@pytest.fixture(autouse=True, scope="session")
def setup_db():
    database.init_db()
    yield
    os.unlink(_tmp.name)


# ── 1: GET /flights returns all seeded flights ─────────────────────────────────
def test_list_all_flights():
    res = client.get("/flights")
    assert res.status_code == 200
    data = res.json()
    assert "flights" in data
    assert len(data["flights"]) >= 1
    f = data["flights"][0]
    for key in ("origin", "destination", "departure_datetime", "price_per_seat", "seats_available"):
        assert key in f


# ── 2: Search filters work correctly ──────────────────────────────────────────
def test_flight_search_by_origin():
    res = client.get("/flights", params={"origin": "Dubai"})
    assert res.status_code == 200
    flights = res.json()["flights"]
    assert all(f["origin"].lower() == "dubai" for f in flights)


# ── 3: Booking creation succeeds with valid data ───────────────────────────────
def test_create_booking_success():
    flights = client.get("/flights", params={"origin": "Dubai"}).json()["flights"]
    assert flights, "Need at least one Dubai flight"
    fid = flights[0]["id"]

    res = client.post("/bookings", json={
        "flight_id": fid,
        "passenger_name": "Hashir Ahmed",
        "passport_number": "AB123456",
        "seat": "12A",
    })
    assert res.status_code == 201
    data = res.json()
    assert data["booking_reference"].startswith("FH")
    assert data["status"] == "confirmed"


# ── 4 (Business Rule): Overbooking is rejected ────────────────────────────────
def test_overbooking_rejected():
    """
    Create a flight with 1 seat. Book it. Then attempt a second booking — must get 409.
    """
    import sqlite3
    conn = sqlite3.connect(database.DB_PATH)
    conn.execute("""
        INSERT INTO flights (airline, flight_number, origin, destination,
            departure_datetime, duration_minutes, price_per_seat, seats_available, total_seats)
        VALUES ('TestAir', 'TX-999', 'TestCity', 'Nowhere', '2026-06-01 10:00', 60, 50.0, 1, 1)
    """)
    conn.commit()
    fid = conn.execute("SELECT id FROM flights WHERE flight_number='TX-999'").fetchone()[0]
    conn.close()

    # First booking — should succeed
    r1 = client.post("/bookings", json={
        "flight_id": fid,
        "passenger_name": "First Passenger",
        "passport_number": "FP111111",
        "seat": "1A",
    })
    assert r1.status_code == 201

    # Second booking — must be rejected (no seats)
    r2 = client.post("/bookings", json={
        "flight_id": fid,
        "passenger_name": "Second Passenger",
        "passport_number": "SP222222",
        "seat": "1B",
    })
    assert r2.status_code == 409
    assert "No seats available" in r2.json()["detail"]


# ── 5: Cancellation restores seat count ───────────────────────────────────────
def test_cancel_booking_restores_seat():
    flights = client.get("/flights", params={"origin": "Doha"}).json()["flights"]
    assert flights, "Need at least one Doha flight"
    fid    = flights[0]["id"]
    before = flights[0]["seats_available"]

    book = client.post("/bookings", json={
        "flight_id": fid,
        "passenger_name": "Cancel Test",
        "passport_number": "CT654321",
        "seat": "5F",
    })
    assert book.status_code == 201
    ref = book.json()["booking_reference"]

    # Seats should have decreased by 1
    after_book = client.get(f"/flights/{fid}").json()["seats_available"]
    assert after_book == before - 1

    # Cancel
    cancel = client.delete(f"/bookings/{ref}")
    assert cancel.status_code == 200

    # Seats should be restored
    after_cancel = client.get(f"/flights/{fid}").json()["seats_available"]
    assert after_cancel == before


def test_booking_unknown_flight_returns_404():
    res = client.post("/bookings", json={
        "flight_id": 99999,
        "passenger_name": "Ghost User",
        "passport_number": "GH999999",
        "seat": "1A",
    })
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_duplicate_passport_rejected():
    flights = client.get("/flights").json()["flights"]
    fid = flights[0]["id"]

    client.post("/bookings", json={
        "flight_id": fid,
        "passenger_name": "Repeat Flyer",
        "passport_number": "RP000001",
        "seat": "8C",
    })

    r2 = client.post("/bookings", json={
        "flight_id": fid,
        "passenger_name": "Repeat Flyer",
        "passport_number": "RP000001",
        "seat": "8D",
    })
    assert r2.status_code == 409