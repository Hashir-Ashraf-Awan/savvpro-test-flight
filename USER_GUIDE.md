# User Guide — FlightHub

## Using the Web UI

Open `http://localhost:3000` after starting both backend and frontend.

### Search Flights (default tab)

- Leave all filters blank and the full flight list loads automatically
- Filter by **From** (origin city), **To** (destination), or **Date**
- Click **Book** on any flight card to open the booking modal

### Booking a Flight (modal)

Fill in:
- **Passenger Full Name** — full name as on passport
- **Passport Number** — 6–9 uppercase alphanumeric (e.g. `AB123456`)
- **Seat** — row + letter, e.g. `12A`, `3B`, `20F`

Click **Confirm Booking**. A green toast shows your booking reference (e.g. `FH3A9C1D2E`). Keep this reference.

### View My Bookings

Go to the **My Bookings** tab. Search by:
- Passenger name (partial match supported)
- Booking reference (exact)

Each result shows flight details, seat, and status. You can cancel directly from here.

### Cancel a Booking

Go to the **Cancel** tab. Enter the booking reference and click **Cancel Booking**. The seat is released immediately.

---

## curl Examples

### List all flights
```bash
curl http://localhost:8000/flights
```

### Search flights
```bash
curl "http://localhost:8000/flights?origin=Dubai&destination=London"
curl "http://localhost:8000/flights?departure_date=2026-05-20"
```

### Book a flight
```bash
curl -X POST http://localhost:8000/bookings \
  -H "Content-Type: application/json" \
  -d '{
    "flight_id": 1,
    "passenger_name": "Ahmed Hassan",
    "passport_number": "AK123456",
    "seat": "12A"
  }'
```

### Find bookings
```bash
# By reference
curl "http://localhost:8000/bookings?reference=FH3A9C1D2E"

# By name
curl "http://localhost:8000/bookings?passenger_name=Ahmed"
```

### Cancel a booking
```bash
curl -X DELETE http://localhost:8000/bookings/FH3A9C1D2E
```

---

## Seat Format

Seats follow the pattern: **row number (1–20) + letter (A–F)**

Valid: `1A`, `12C`, `20F`  
Invalid: `0A`, `12G`, `A12`

## Error Codes

| Code | Meaning                          |
|------|----------------------------------|
| 400  | Missing required search params   |
| 404  | Flight or booking not found      |
| 409  | No seats / seat taken / already cancelled |
| 422  | Validation error (bad input format) |
