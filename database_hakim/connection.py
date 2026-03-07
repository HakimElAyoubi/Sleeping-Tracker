"""
Database Connection Handler
===========================
Manages SQLite database connection and initialization.
"""

import sqlite3
import os
from pathlib import Path

# Default database path (in project root)
DEFAULT_DB_PATH = Path(__file__).parent.parent / "sleep_tracker.db"


def get_connection(db_path: str = None) -> sqlite3.Connection:
    """
    Get a database connection.

    Args:
        db_path: Optional custom database path. Uses default if not provided.

    Returns:
        sqlite3.Connection object
    """
    path = db_path or DEFAULT_DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn


def init_database(db_path: str = None) -> None:
    """
    Initialize the database with required tables.
    Call this once at application startup.

    Args:
        db_path: Optional custom database path.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()

    # Create sleep_records table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sleep_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL UNIQUE,
            bedtime TEXT NOT NULL,
            wake_time TEXT NOT NULL,
            duration_hours REAL NOT NULL,
            quality_rating INTEGER CHECK(quality_rating >= 1 AND quality_rating <= 5),
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create index for faster date lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sleep_records_date
        ON sleep_records(date)
    """)

    conn.commit()
    conn.close()
