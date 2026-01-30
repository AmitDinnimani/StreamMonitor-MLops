import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).parent / "monitoring.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT NOT NULL,
            prediction REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            median REAL,
            drift_score REAL,
            alert INTEGER,
            timestamp TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def add_prediction(request_id: str, prediction: float, timestamp: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO predictions (request_id, prediction, timestamp) VALUES (?, ?, ?)",
            (request_id, prediction, timestamp)
        )
        conn.commit()


def add_metrics(median: float, drift_score: float, alert: int, timestamp: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO metrics (median, drift_score, alert, timestamp) VALUES (?, ?, ?, ?)",
            (median, drift_score, alert, timestamp)
        )
        conn.commit()
