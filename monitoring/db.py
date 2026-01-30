import sqlite3
from pathlib import Path
from datetime import datetime,timezone
import json

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "monitoring" / "monitoring.db"
DB_PATH.parent.mkdir(exist_ok=True)

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL,
        features TEXT,
        prediction REAL,
        request_id TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            median_value REAL,            
            mean_value REAL,              
            std_value REAL,               
            drift_score REAL,             
            mean_ratio REAL,
            median_ratio REAL,
            std_ratio REAL,
            alert INTEGER,                
            mean_drift_vals TEXT,         
            median_drift_vals TEXT,       
            std_drift_vals TEXT           
        )
    """)

    conn.commit()
    conn.close()

def add_metric( median_value: float,mean_value: float,std_value: float,drift_score: float,
                mean_ratio: float,median_ratio: float,std_ratio: float,alert: int,
                mean_drift_vals: list,median_drift_vals: list,std_drift_vals: list ):
    conn = get_connection()
    cursor = conn.cursor()

    timestamp = datetime.now(timezone.utc).timestamp()
    cursor.execute("""
        INSERT INTO metrics (
            timestamp, 
            median_value, 
            mean_value, 
            std_value, 
            drift_score, 
            mean_ratio, 
            median_ratio, 
            std_ratio, 
            alert,
            mean_drift_vals,
            median_drift_vals,
            std_drift_vals
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        timestamp,
        median_value,
        mean_value,
        std_value,
        drift_score,
        mean_ratio,
        median_ratio,
        std_ratio,
        alert,
        json.dumps(mean_drift_vals),
        json.dumps(median_drift_vals),
        json.dumps(std_drift_vals)
    ))

    conn.commit()
    conn.close()
    print("Metric added successfully!")

def add_prediction(features: dict, prediction: float, request_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    timestamp = datetime.now(timezone.utc).timestamp()
    features_json = json.dumps(features)       

    cursor.execute("""
        INSERT INTO predictions (timestamp, features, prediction, request_id)
        VALUES (?, ?, ?, ?)
    """, (timestamp, features_json, prediction, request_id))
    
    conn.commit()
    print("Prediction added successfully!")