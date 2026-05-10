# ✈️ FlightHub — Flight Search & Booking System

A full-stack flight booking application built with **FastAPI** (backend) and **Express + HTML** (frontend).

---

## Tech Stack

| Layer    | Technology                        |
|----------|-----------------------------------|
| Backend  | Python 3.10+, FastAPI, SQLite     |
| Frontend | Node.js, Express, Vanilla JS/HTML |
| Tests    | pytest, FastAPI TestClient        |

---

## Quick Start

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API docs available at: `http://localhost:8000/docs`

### 2. Frontend

```bash
cd frontend
npm install
node server.js
```

Open: `http://localhost:3000`

### 3. Tests

```bash
pip install pytest httpx
pytest tests/ -v
```

---

## Assumptions

- SQLite database is created automatically on first run with seed data (15 flights)
- No authentication — this is an internal staff tool
- All prices are in USD
- Seat format: row number (1–20) + letter A–F, e.g. `12A`, `3B`
- Passport numbers must be 6–9 uppercase alphanumeric characters

---

## Environment

No environment variables required. Everything runs locally out of the box.
