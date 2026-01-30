import sqlite3
from pathlib import Path
import pandas as pd
from monitoring.db import DB_PATH

def check_table(table_name: str, limit: int = 5):
    """Check table contents and number of rows"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Number of rows
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"Table '{table_name}' has {count} rows.\n")

    # Show latest rows
    df = pd.read_sql(f"SELECT * FROM {table_name} ORDER BY timestamp DESC LIMIT {limit}", conn)

    # Parse JSON columns if needed
    if table_name == "predictions" and "features" in df.columns:
        df["features"] = df["features"].apply(lambda x: x)
    elif table_name == "metrics":
        for col in ["mean_drift_vals", "median_drift_vals", "std_drift_vals"]:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: x)

    print(df)
    print("\n")
    conn.close()


if __name__ == "__main__":
    print("===== CHECKING DB CONTENTS =====\n")
    check_table("predictions")
    check_table("metrics")
