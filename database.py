import sqlite3

DB_NAME = "data.db"

def init_db():
    """Initializes the SQLite database and creates the necessary tables."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create weather table per user requirement
    # Schema: id, location, min_temp, max_temp, description
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
    conn.close()
    print(f"Database {DB_NAME} initialized.")

def save_forecasts(forecast_list):
    """
    Saves a list of forecast dictionaries to the database.
    Each dict should have: location, date, weather, max_temp, min_temp
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    inserted_count = 0
    
    for item in forecast_list:
        try:
            # Upsert logic to prevent duplicates for same location+date
            # Mapping item keys to table columns:
            # item['region'] -> location
            # item['min_temp'] -> min_temp
            # item['max_temp'] -> max_temp
            # item['weather'] -> description
            # item['date'] -> forecast_date (Created extra column to keep track of date)
            
            cursor.execute('''
                INSERT INTO weather (location, min_temp, max_temp, description, forecast_date)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(location, forecast_date) DO UPDATE SET
                    min_temp=excluded.min_temp,
                    max_temp=excluded.max_temp,
                    description=excluded.description
            ''', (
                item['region'],
                item['min_temp'],
                item['max_temp'],
                item['weather'],
                item['date']
            ))
            inserted_count += 1
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            
    conn.commit()
    conn.close()
    print(f"Processed {inserted_count} records.")

if __name__ == "__main__":
    init_db()
