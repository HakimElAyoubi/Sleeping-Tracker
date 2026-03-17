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
            mood INTEGER CHECK(mood >= 1 AND mood <= 5),
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Add mood column to existing tables that don't have it yet
    try:
        cursor.execute("ALTER TABLE sleep_records ADD COLUMN mood INTEGER CHECK(mood >= 1 AND mood <= 5)")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Create index for faster date lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sleep_records_date
        ON sleep_records(date)
    """)

    # Create habits table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sleep_record_id INTEGER NOT NULL,
            took_coffee BOOLEAN DEFAULT 0,
            exercised BOOLEAN DEFAULT 0,
            used_screen BOOLEAN DEFAULT 0,
            FOREIGN KEY (sleep_record_id) REFERENCES sleep_records(id)
        )
    """)

    # Create reports table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_date TEXT NOT NULL,
            week_start TEXT NOT NULL,
            week_end TEXT NOT NULL,
            sleep_debt REAL DEFAULT 0,
            average_mood REAL,
            average_sleep_time REAL,
            average_quality REAL,
            insights TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
