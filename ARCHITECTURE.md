# Architecture — FlightHub

## Data Model

### `flights`

| Column             | Type    | Notes                                  |
|--------------------|---------|----------------------------------------|
| id                 | INTEGER | Primary key, autoincrement             |
| airline            | TEXT    | Carrier name                           |
| flight_number      | TEXT    | Unique (e.g. EK-501)                   |
| origin             | TEXT    | City name                              |
| destination        | TEXT    | City name                              |
| departure_datetime | TEXT    | ISO 8601 string                        |
| duration_minutes   | INTEGER | Flight duration                        |
| price_per_seat     | REAL    | USD                                    |
| seats_available    | INTEGER | Decremented on booking, restored on cancel. CHECK ≥ 0 |
| total_seats        | INTEGER | Immutable capacity reference           |

### `bookings`

| Column          | Type    | Notes                              |
|-----------------|---------|------------------------------------|
| id              | INTEGER | Primary key                        |
| reference       | TEXT    | Unique — "FH" + 8 hex chars (e.g. FH3A9C1D2E) |
| flight_id       | INTEGER | FK → flights.id                    |
| passenger_name  | TEXT    |                                    |
| passport_number | TEXT    | Uppercased, 6–9 alphanumeric       |
| seat            | TEXT    | Uppercased, e.g. 12A               |
| status          | TEXT    | 'confirmed' or 'cancelled'         |
| created_at      | TEXT    | UTC datetime, auto-set             |

---

## API Design

| Method | Path               | Description                              |
|--------|--------------------|------------------------------------------|
| GET    | /flights           | List/search flights (query: origin, destination, departure_date) |
| GET    | /flights/{id}      | Get single flight                        |
| POST   | /bookings          | Create a booking                         |
| GET    | /bookings          | Find bookings by name or reference       |
| DELETE | /bookings/{ref}    | Cancel a booking by reference            |

All responses return JSON. Errors follow `{"detail": "..."}` convention.

---

## Ambiguity Resolutions

### 1. Overbooking Rule

**Decision: Hard reject.**

When `seats_available = 0`, any new booking returns `HTTP 409 Conflict` with the message _"No seats available on this flight. Booking rejected."_

**Reasoning:** For a travel agency tool, silent overbooking is dangerous — it would mean issuing confirmed tickets for seats that don't exist. A hard reject forces the agent to offer the passenger an alternative flight. Waitlist functionality was out of scope.

### 2. UI Priority

**Decision: Flight cards are the primary UI element.**

The "Flights" tab loads all available flights immediately on page load. Each card shows the essential decision-making information: route, departure time, duration, seats remaining, and price. A "Book" button on each card opens a modal — minimising navigation steps to complete a booking.

The tab order (Flights → Book → My Bookings → Cancel) mirrors the natural workflow of a travel agent.

---

## Architecture Decisions

- **SQLite with WAL mode** — sufficient for a single-instance internal tool; WAL improves concurrent read performance.
- **CORS wildcard** — acceptable for a local-only internal tool.
- **No ORM** — raw `sqlite3` keeps dependencies minimal and the schema transparent.
- **Pydantic v2 validators** — field-level validation for passport format and seat format before any DB interaction.
- **Booking reference format** — `FH` prefix + 8 random hex chars gives ~4 billion unique references, unambiguous at a glance.
