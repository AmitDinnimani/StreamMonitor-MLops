# scripts/clean_db.py
import sqlite3
from pathlib import Path

# Path to your DB
DB_PATH = Path(__file__).resolve().parent.parent / "monitoring" / "monitoring.db"

def clean_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Delete all rows in predictions and metrics
    cursor.execute("DELETE FROM predictions")
    cursor.execute("DELETE FROM metrics")

    # Optionally reset AUTOINCREMENT counters
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='predictions'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='metrics'")

    conn.commit()
    conn.close()
    print("✅ Tables cleaned successfully!")

if __name__ == "__main__":
    clean_tables()
