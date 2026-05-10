# AI Usage Log — FlightHub

**Tool used:** Claude (Sonnet 4) via claude.ai  
**Assessment:** SavvPro Full-Stack Developer Assessment — FlightHub

---

## Overview

AI was used actively throughout this build as a coding agent — not as a copy-paste machine. Every generated output was reviewed, tested, and in several cases corrected before being committed.

---

## Key Prompts & AI Direction

### Prompt 1 — Schema & API design
> "Design a SQLite schema for a flight booking system. Flights need origin, destination, departure datetime, duration, price, and seat tracking. Bookings need a unique reference, passenger info, and status. Give me raw sqlite3 Python — no ORM."

**What AI got right:** Clean schema with appropriate constraints (`CHECK(seats_available >= 0)`, `CHECK(status IN (...))`). WAL mode suggestion was good.

**What AI got wrong:** Initial version used `datetime` Python type in the Pydantic model for `departure_date` query param — this broke FastAPI's query coercion. Fixed by switching to `date` type and importing from `datetime`.

**My correction:** Changed `from datetime import datetime` → `from datetime import date` in the query param annotation.

---

### Prompt 2 — Overbooking logic
> "Implement the booking POST endpoint. Handle overbooking with a hard reject — return 409 if seats_available is 0. Also check that the same seat isn't already taken on the same flight."

**What AI got right:** Both checks were correctly placed before any INSERT. The seat conflict check joined on `status = 'confirmed'` which was correct — cancelled seats should be reclaimable.

**What AI got wrong:** AI initially didn't include the `PRAGMA journal_mode=WAL` in `get_db_connection`, only in `init_db`. This means WAL wasn't active for connections opened after init.

**My correction:** Moved the PRAGMA into `get_db_connection()` so every connection benefits.

---

### Prompt 3 — Frontend UI
> "Build a single-page Express frontend for FlightHub. Aviation aesthetic — dark, clean, prioritise the flight cards. Each card shows route, time, duration, seats, price. Book button opens a modal. Tabs: Flights, Book, My Bookings, Cancel."

**What AI got right:** The modal overlay, tab system, and toast notification system were clean and functional on first generation.

**What AI got wrong:** The `renderFlight` function stringified the flight object with `JSON.stringify(f)` and embedded it in an `onclick` attribute — this broke when airline names contained apostrophes (e.g. "Air Arabia's" would have broken the HTML attribute). Also, the initial `fetch` error handling only caught network errors, not HTTP error responses.

**My correction:**
1. Used `.replace(/"/g, '&quot;')` on the stringified JSON to safely embed in HTML attributes.
2. Added `if (!res.ok)` checks after every fetch call to handle 4xx/5xx responses properly.

---

### Prompt 4 — Tests
> "Write pytest tests for FlightHub. Must include: list flights, search by origin, create booking, overbooking rejection (business rule test), cancellation restores seat count. Use a temp SQLite file so tests don't touch the real DB."

**What AI got right:** The fixture pattern using `tempfile.NamedTemporaryFile` was correct. The overbooking test correctly inserted a 1-seat flight directly via sqlite3 to isolate the test.

**What AI got wrong:** AI used `autouse=True` on the fixture but set `scope="module"` — this caused the DB to be torn down between test files if more were added. Changed to `scope="session"`.

**My correction:** Changed `scope="module"` → `scope="session"` on the `setup_db` fixture.

---

## Reflection

AI significantly accelerated the boilerplate (DB init, Pydantic models, Express server scaffolding, CSS layout). The time saved on setup allowed more focus on correctness of business logic and edge cases.

The AI's biggest weakness in this project was **cross-cutting concerns** — things that span multiple files or layers (e.g. WAL mode needing to be in every connection, not just init). These required careful review of every generated output in context, not in isolation.

**Ratio: ~60% AI-generated, 40% human-directed corrections and additions.**
