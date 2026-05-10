import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "flighthub.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_db_connection()

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS flights (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            airline           TEXT NOT NULL,
            flight_number     TEXT NOT NULL UNIQUE,
            origin            TEXT NOT NULL,
            destination       TEXT NOT NULL,
            departure_datetime TEXT NOT NULL,
            duration_minutes  INTEGER NOT NULL,
            price_per_seat    REAL NOT NULL,
            seats_available   INTEGER NOT NULL CHECK(seats_available >= 0),
            total_seats       INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS bookings (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            reference        TEXT NOT NULL UNIQUE,
            flight_id        INTEGER NOT NULL REFERENCES flights(id),
            passenger_name   TEXT NOT NULL,
            passport_number  TEXT NOT NULL,
            seat             TEXT NOT NULL,
            status           TEXT NOT NULL DEFAULT 'confirmed' CHECK(status IN ('confirmed','cancelled')),
            created_at       TEXT NOT NULL DEFAULT (datetime('now'))
        );
    """)

    # Seed flights if empty
    count = conn.execute("SELECT COUNT(*) FROM flights").fetchone()[0]
    if count == 0:
        flights = [
            ("Emirates", "EK-501", "Dubai", "London", "2026-05-20 08:00", 420, 450.00, 180, 180),
            ("Emirates", "EK-502", "London", "Dubai", "2026-05-21 14:00", 420, 420.00, 175, 180),
            ("Qatar Airways", "QR-101", "Doha", "New York", "2026-05-20 23:00", 840, 720.00, 200, 200),
            ("Qatar Airways", "QR-102", "New York", "Doha", "2026-05-22 10:00", 810, 695.00, 198, 200),
            ("PIA", "PK-200", "Karachi", "London", "2026-05-20 02:00", 480, 310.00, 150, 160),
            ("PIA", "PK-201", "London", "Karachi", "2026-05-23 18:00", 490, 300.00, 145, 160),
            ("Turkish Airlines", "TK-780", "Istanbul", "Dubai", "2026-05-21 06:30", 195, 220.00, 140, 140),
            ("Turkish Airlines", "TK-781", "Dubai", "Istanbul", "2026-05-22 09:15", 200, 215.00, 135, 140),
            ("Lufthansa", "LH-400", "Frankfurt", "New York", "2026-05-20 11:00", 510, 650.00, 250, 260),
            ("Lufthansa", "LH-401", "New York", "Frankfurt", "2026-05-21 19:00", 480, 630.00, 255, 260),
            ("Air Arabia", "G9-310", "Sharjah", "Karachi", "2026-05-20 15:45", 150, 120.00, 100, 120),
            ("Air Arabia", "G9-311", "Karachi", "Sharjah", "2026-05-21 22:00", 155, 115.00, 98, 120),
            ("British Airways", "BA-105", "London", "New York", "2026-05-22 09:00", 440, 580.00, 220, 240),
            ("British Airways", "BA-106", "New York", "London", "2026-05-23 14:30", 430, 560.00, 215, 240),
            ("flydubai", "FZ-640", "Dubai", "Karachi", "2026-05-20 07:00", 140, 95.00, 80, 90),
        ]
        conn.executemany(
            """INSERT INTO flights (airline, flight_number, origin, destination,
               departure_datetime, duration_minutes, price_per_seat, seats_available, total_seats)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            flights,
        )

    conn.commit()
    conn.close()
