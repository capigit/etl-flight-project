"""Simple DB initialization script

Creates the `data` folder (if missing) and ensures the `flights` table exists.
"""
from pathlib import Path
import sqlite3
import os

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "data" / "flights.db"


def init_db(db_path: str = None):
    db_path = db_path or DB_PATH
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_file))
    cur = conn.cursor()

    # Create a minimal flights table if it does not exist
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS flights (
            icao24 TEXT,
            callsign TEXT,
            origin_country TEXT,
            time_position TEXT,
            last_contact TEXT,
            longitude REAL,
            latitude REAL,
            baro_altitude REAL,
            on_ground INTEGER,
            velocity REAL,
            true_track REAL,
            vertical_rate REAL,
            geo_altitude REAL,
            squawk TEXT,
            spi INTEGER,
            position_source INTEGER,
            altitude_feet REAL,
            processed_at TEXT
        )
        """
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Initialized DB at: {DB_PATH}")