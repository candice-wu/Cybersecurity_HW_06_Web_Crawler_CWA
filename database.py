import sqlite3
from typing import List, Dict, Any, Optional

DB_NAME = "data.db"

def get_db_connection() -> sqlite3.Connection:
    """Establishes a connection to the SQLite database."""
    return sqlite3.connect(DB_NAME)

def init_db() -> None:
    """Initializes the SQLite database and creates the necessary tables."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Create weather table per user requirement
            # Schema: id, location, min_temp, max_temp, description, forecast_date
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS weather (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    location TEXT,
                    min_temp REAL,
                    max_temp REAL,
                    description TEXT,
                    forecast_date TEXT,
                    UNIQUE(location, forecast_date)
                )
            ''')
            conn.commit()
            print(f"Database {DB_NAME} initialized.")
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")

def save_forecasts(forecast_list: List[Dict[str, Any]]) -> None:
    """
    Saves a list of forecast dictionaries to the database.
    Each dict should have: location, date, weather, max_temp, min_temp
    """
    if not forecast_list:
        print("No forecasts to save.")
        return

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            inserted_count = 0
            
            for item in forecast_list:
                try:
                    # Upsert logic to prevent duplicates for same location+date
                    cursor.execute('''
                        INSERT INTO weather (location, min_temp, max_temp, description, forecast_date)
                        VALUES (?, ?, ?, ?, ?)
                        ON CONFLICT(location, forecast_date) DO UPDATE SET
                            min_temp=excluded.min_temp,
                            max_temp=excluded.max_temp,
                            description=excluded.description
                    ''', (
                        item.get('region'),
                        item.get('min_temp'),
                        item.get('max_temp'),
                        item.get('weather'),
                        item.get('date')
                    ))
                    inserted_count += 1
                except sqlite3.Error as row_error:
                    print(f"Error saving row {item}: {row_error}")
            
            conn.commit()
            print(f"Processed {inserted_count} records.")
            
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")

if __name__ == "__main__":
    init_db()
