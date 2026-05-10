from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from typing import Optional
import uuid
import re
from database import init_db, get_db_connection
from datetime import date

app = FastAPI(title="FlightHub API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Pydantic Models ────────────────────────────────────────────────────────────

class BookingCreate(BaseModel):
    flight_id: int
    passenger_name: str
    passport_number: str
    seat: str

    @field_validator("passenger_name")
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Passenger name cannot be empty")
        return v.strip()

    @field_validator("passport_number")
    @classmethod
    def passport_valid(cls, v):
        if not re.match(r"^[A-Z0-9]{6,9}$", v.upper()):
            raise ValueError("Passport number must be 6-9 alphanumeric characters")
        return v.upper()

    @field_validator("seat")
    @classmethod
    def seat_valid(cls, v):
        if not re.match(r"^[1-9][0-9]?[A-F]$", v.upper()):
            raise ValueError("Seat must be in format like 12A, 3B, 20F")
        return v.upper()


# ─── Startup ────────────────────────────────────────────────────────────────────

@app.on_event("startup")
def startup():
    init_db()


# ─── Flights ─────────────────────────────────────────────────────────────────────

@app.get("/flights", summary="List and search flights")
def list_flights(
    origin: Optional[str] = Query(None),
    destination: Optional[str] = Query(None),
    departure_date: Optional[date] = Query(None),
):
    conn = get_db_connection()
    query = "SELECT * FROM flights WHERE seats_available > 0"
    params = []

    if origin:
        query += " AND LOWER(origin) = LOWER(?)"
        params.append(origin)
    if destination:
        query += " AND LOWER(destination) = LOWER(?)"
        params.append(destination)
    if departure_date:
        query += " AND DATE(departure_datetime) = ?"
        params.append(str(departure_date))

    rows = conn.execute(query, params).fetchall()
    conn.close()

    if not rows:
        return {"flights": [], "message": "No flights found matching your criteria"}

    return {"flights": [dict(r) for r in rows]}


@app.get("/flights/{flight_id}", summary="Get a single flight")
def get_flight(flight_id: int):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM flights WHERE id = ?", (flight_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Flight not found")
    return dict(row)


# ─── Bookings ────────────────────────────────────────────────────────────────────

@app.post("/bookings", status_code=201, summary="Create a booking")
def create_booking(data: BookingCreate):
    conn = get_db_connection()

    # Lock check: fetch flight
    flight = conn.execute(
        "SELECT * FROM flights WHERE id = ?", (data.flight_id,)
    ).fetchone()

    if not flight:
        conn.close()
        raise HTTPException(status_code=404, detail="Flight not found")

    # Overbooking rule: reject if no seats available
    if flight["seats_available"] <= 0:
        conn.close()
        raise HTTPException(
            status_code=409,
            detail="No seats available on this flight. Booking rejected.",
        )

    # Check seat not already taken on same flight
    existing = conn.execute(
        "SELECT id FROM bookings WHERE flight_id = ? AND seat = ? AND status = 'confirmed'",
        (data.flight_id, data.seat),
    ).fetchone()
    if existing:
        conn.close()
        raise HTTPException(
            status_code=409, detail=f"Seat {data.seat} is already taken on this flight"
        )

    reference = "FH" + uuid.uuid4().hex[:8].upper()

    conn.execute(
        """INSERT INTO bookings (reference, flight_id, passenger_name, passport_number, seat, status)
           VALUES (?, ?, ?, ?, ?, 'confirmed')""",
        (reference, data.flight_id, data.passenger_name, data.passport_number, data.seat),
    )
    conn.execute(
        "UPDATE flights SET seats_available = seats_available - 1 WHERE id = ?",
        (data.flight_id,),
    )
    conn.commit()
    conn.close()

    return {
        "booking_reference": reference,
        "message": "Booking confirmed",
        "passenger_name": data.passenger_name,
        "seat": data.seat,
        "flight_id": data.flight_id,
        "status": "confirmed",
    }


@app.get("/bookings", summary="Find bookings by name or reference")
def find_bookings(
    passenger_name: Optional[str] = Query(None),
    reference: Optional[str] = Query(None),
):
    if not passenger_name and not reference:
        raise HTTPException(
            status_code=400, detail="Provide passenger_name or reference to search"
        )

    conn = get_db_connection()
    query = """
        SELECT b.*, f.origin, f.destination, f.departure_datetime, f.duration_minutes,
               f.price_per_seat, f.airline
        FROM bookings b
        JOIN flights f ON b.flight_id = f.id
        WHERE 1=1
    """
    params = []

    if reference:
        query += " AND UPPER(b.reference) = UPPER(?)"
        params.append(reference)
    if passenger_name:
        query += " AND LOWER(b.passenger_name) LIKE LOWER(?)"
        params.append(f"%{passenger_name}%")

    rows = conn.execute(query, params).fetchall()
    conn.close()

    if not rows:
        return {"bookings": [], "message": "No bookings found"}

    return {"bookings": [dict(r) for r in rows]}


@app.delete("/bookings/{reference}", summary="Cancel a booking")
def cancel_booking(reference: str):
    conn = get_db_connection()

    booking = conn.execute(
        "SELECT * FROM bookings WHERE UPPER(reference) = UPPER(?)", (reference,)
    ).fetchone()

    if not booking:
        conn.close()
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking["status"] == "cancelled":
        conn.close()
        raise HTTPException(status_code=409, detail="Booking is already cancelled")

    conn.execute(
        "UPDATE bookings SET status = 'cancelled' WHERE reference = ?",
        (booking["reference"],),
    )
    conn.execute(
        "UPDATE flights SET seats_available = seats_available + 1 WHERE id = ?",
        (booking["flight_id"],),
    )
    conn.commit()
    conn.close()

    return {"message": "Booking cancelled successfully", "reference": booking["reference"]}
