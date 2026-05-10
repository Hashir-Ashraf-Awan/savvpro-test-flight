# ✈️ FlightHub — Flight Search & Booking System

> Full-Stack Developer Assessment — SavvPro | Built with FastAPI + Express

---

## Overview

FlightHub is a full-stack flight booking application built for a small travel agency. Staff can search available flights, book seats for passengers, view bookings by name or reference, and cancel them. There is no payment system — bookings are confirmed immediately upon submission.

---

## Tech Stack

| Layer    | Technology                                      |
|----------|-------------------------------------------------|
| Backend  | Python 3.10+, FastAPI, SQLite, Pydantic v2      |
| Frontend | Node.js 18+, Express 4, Vanilla JS / HTML / CSS |
| Tests    | pytest, FastAPI TestClient, httpx               |
| Database | SQLite (WAL mode, auto-initialized on startup)  |

---

## Project Structure

```
flighthub/
├── README.md
├── ARCHITECTURE.md
├── AI_USAGE.md
├── USER_GUIDE.md
├── .gitignore
├── backend/
│   ├── main.py            # FastAPI app, all endpoints
│   ├── database.py        # Schema init, seed data, connection helper
│   └── requirements.txt
├── frontend/
│   ├── server.js          # Express static server
│   ├── package.json
│   └── public/
│       └── index.html     # Single-page app, all UI logic
└── tests/
    └── test_flighthub.py  # 6 pytest tests
```

---

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/savvpro-test-flight.git
cd savvpro-test-flight
git checkout candidate-Hashir-Ashraf-Awan
```

### 2. Start the Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

- API base: `http://localhost:8000`
- Interactive docs: `http://localhost:8000/docs`

### 3. Start the Frontend

Open a **new terminal**:

```bash
cd frontend
npm install
node server.js
```

- Frontend: `http://localhost:3000`

### 4. Run Tests

```bash
pip install pytest httpx
pytest tests/ -v
```

---

## API Endpoints

| Method   | Endpoint                | Description                            |
|----------|-------------------------|----------------------------------------|
| `GET`    | `/flights`              | List all flights, optional filters     |
| `GET`    | `/flights/{id}`         | Get a single flight by ID              |
| `POST`   | `/bookings`             | Create a new booking                   |
| `GET`    | `/bookings`             | Find bookings by name or reference     |
| `DELETE` | `/bookings/{reference}` | Cancel a booking by reference          |

### Query Parameters — `GET /flights`

| Param            | Example      | Description                  |
|------------------|--------------|------------------------------|
| `origin`         | `Dubai`      | Filter by origin city        |
| `destination`    | `London`     | Filter by destination city   |
| `departure_date` | `2026-05-20` | Filter by date (YYYY-MM-DD)  |

### `POST /bookings` — Request Body

```json
{
  "flight_id": 1,
  "passenger_name": "Ahmed Hassan",
  "passport_number": "AK123456",
  "seat": "12A"
}
```

### HTTP Response Codes

| Code  | Meaning                                                          |
|-------|------------------------------------------------------------------|
| `200` | Success                                                          |
| `201` | Booking created successfully                                     |
| `400` | Missing required parameters                                      |
| `404` | Flight or booking not found                                      |
| `409` | No seats / seat taken / already cancelled / duplicate passport   |
| `422` | Validation error — bad input format                              |

---

## Business Rules

- **Overbooking** — hard rejected with `HTTP 409`. No waitlist.
- **Seat conflict** — same seat on same flight cannot be booked twice.
- **Duplicate passport** — same passport cannot book the same flight twice.
- **Cancellation** — seat count is restored immediately on cancel.
- **Booking reference** — format: `FH` + 8 hex chars e.g. `FH3A9C1D2E`

---

## Input Validation

| Field              | Rule                              | Valid Example  |
|--------------------|-----------------------------------|----------------|
| `passenger_name`   | Non-empty string                  | `Ahmed Hassan` |
| `passport_number`  | 6–9 uppercase alphanumeric chars  | `AK123456`     |
| `seat`             | Row 1–20 + letter A–F             | `12A`, `3B`    |
| `flight_id`        | Must exist in flights table       | `1`            |

---

## Seed Data

The database auto-initializes on first run with 15 flights:

| Route                  | Airline          |
|------------------------|------------------|
| Dubai → London         | Emirates         |
| London → Dubai         | Emirates         |
| Doha → New York        | Qatar Airways    |
| New York → Doha        | Qatar Airways    |
| Karachi → London       | PIA              |
| London → Karachi       | PIA              |
| Istanbul → Dubai       | Turkish Airlines |
| Dubai → Istanbul       | Turkish Airlines |
| Frankfurt → New York   | Lufthansa        |
| New York → Frankfurt   | Lufthansa        |
| London → New York      | British Airways  |
| New York → London      | British Airways  |
| Dubai → Karachi        | flydubai         |
| Sharjah → Karachi      | Air Arabia       |
| Karachi → Sharjah      | Air Arabia       |

---

## Assumptions

- No authentication — this is an internal staff tool only
- All prices are in USD
- SQLite database is created automatically on first run
- Database file (`.db`) is excluded from git via `.gitignore`
- No external services or paid APIs — runs entirely locally
- Seat format: row number (1–20) + letter (A–F), e.g. `12A`, `3B`, `20F`
- Passport: 6–9 uppercase alphanumeric characters only

---

## Author

**Hashir Ashraf Awan** — SavvPro Full-Stack Developer Assessment
