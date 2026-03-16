"""
Database Queries
================
CRUD operations for sleep records, habits, and reports.
Other modules should use these functions to interact with the database.
"""

from typing import List, Optional
from .connection import get_connection
from .models import SleepRecord, HabitRecord, ReportRecord


# ============================================================================
# SLEEP RECORDS - CREATE
# ============================================================================

def add_sleep_record(record: SleepRecord) -> int:
    """
    Add a new sleep record to the database.

    Args:
        record: SleepRecord object to insert

    Returns:
        The ID of the newly inserted record
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sleep_records (date, bedtime, wake_time, duration_hours, quality_rating, notes, mood)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        record.date,
        record.bedtime,
        record.wake_time,
        record.duration_hours,
        record.quality_rating,
        record.notes,
        record.mood,
    ))

    record_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return record_id


# ============================================================================
# SLEEP RECORDS - READ
# ============================================================================

def get_all_records() -> List[SleepRecord]:
    """
    Get all sleep records, ordered by date (newest first).

    Returns:
        List of SleepRecord objects
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM sleep_records ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()

    return [SleepRecord.from_row(row) for row in rows]


def get_record_by_id(record_id: int) -> Optional[SleepRecord]:
    """
    Get a single sleep record by ID.

    Args:
        record_id: The database ID of the record

    Returns:
        SleepRecord if found, None otherwise
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM sleep_records WHERE id = ?", (record_id,))
    row = cursor.fetchone()
    conn.close()

    return SleepRecord.from_row(row) if row else None


def get_record_by_date(date: str) -> Optional[SleepRecord]:
    """
    Get a sleep record for a specific date.

    Args:
        date: Date string in YYYY-MM-DD format

    Returns:
        SleepRecord if found, None otherwise
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM sleep_records WHERE date = ?", (date,))
    row = cursor.fetchone()
    conn.close()

    return SleepRecord.from_row(row) if row else None


def get_records_in_range(start_date: str, end_date: str) -> List[SleepRecord]:
    """
    Get all sleep records within a date range.

    Args:
        start_date: Start date (YYYY-MM-DD), inclusive
        end_date: End date (YYYY-MM-DD), inclusive

    Returns:
        List of SleepRecord objects
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM sleep_records
        WHERE date >= ? AND date <= ?
        ORDER BY date DESC
    """, (start_date, end_date))

    rows = cursor.fetchall()
    conn.close()

    return [SleepRecord.from_row(row) for row in rows]


def get_recent_records(limit: int = 7) -> List[SleepRecord]:
    """
    Get the most recent sleep records.

    Args:
        limit: Maximum number of records to return (default: 7)

    Returns:
        List of SleepRecord objects
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM sleep_records
        ORDER BY date DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [SleepRecord.from_row(row) for row in rows]


# ============================================================================
# SLEEP RECORDS - UPDATE
# ============================================================================

def update_sleep_record(record: SleepRecord) -> bool:
    """
    Update an existing sleep record.

    Args:
        record: SleepRecord with updated values (must have id set)

    Returns:
        True if record was updated, False if not found
    """
    if record.id is None:
        raise ValueError("Record must have an ID to update")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE sleep_records
        SET date = ?, bedtime = ?, wake_time = ?, duration_hours = ?,
            quality_rating = ?, notes = ?, mood = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (
        record.date,
        record.bedtime,
        record.wake_time,
        record.duration_hours,
        record.quality_rating,
        record.notes,
        record.mood,
        record.id
    ))

    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()

    return updated


# ============================================================================
# SLEEP RECORDS - DELETE
# ============================================================================

def delete_sleep_record(record_id: int) -> bool:
    """
    Delete a sleep record by ID.

    Args:
        record_id: The database ID of the record to delete

    Returns:
        True if record was deleted, False if not found
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM sleep_records WHERE id = ?", (record_id,))

    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()

    return deleted


# ============================================================================
# SLEEP RECORDS - UTILITIES
# ============================================================================

def get_record_count() -> int:
    """Get total number of sleep records."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM sleep_records")
    count = cursor.fetchone()[0]
    conn.close()

    return count


def date_exists(date: str) -> bool:
    """Check if a record exists for the given date."""
    return get_record_by_date(date) is not None


# ============================================================================
# HABITS - CRUD
# ============================================================================

def insert_habit(record: HabitRecord) -> int:
    """Insert a habit record linked to a sleep record. Returns the new ID."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO habits (sleep_record_id, took_coffee, exercised, used_screen)
        VALUES (?, ?, ?, ?)
    """, (
        record.sleep_record_id,
        int(record.took_coffee),
        int(record.exercised),
        int(record.used_screen),
    ))

    habit_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return habit_id


def get_habits_by_date_range(start_date: str, end_date: str) -> List[HabitRecord]:
    """Get all habit records for sleep records within a date range."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT h.* FROM habits h
        JOIN sleep_records sr ON h.sleep_record_id = sr.id
        WHERE sr.date >= ? AND sr.date <= ?
        ORDER BY sr.date DESC
    """, (start_date, end_date))

    rows = cursor.fetchall()
    conn.close()
    return [HabitRecord.from_row(row) for row in rows]


def get_habit_by_sleep_record_id(record_id: int) -> Optional[HabitRecord]:
    """Get the habit record for a specific sleep record."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM habits WHERE sleep_record_id = ?", (record_id,))
    row = cursor.fetchone()
    conn.close()
    return HabitRecord.from_row(row) if row else None


def get_all_habits() -> List[HabitRecord]:
    """Get all habit records."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM habits")
    rows = cursor.fetchall()
    conn.close()
    return [HabitRecord.from_row(row) for row in rows]


# ============================================================================
# REPORTS - CRUD
# ============================================================================

def insert_report(record: ReportRecord) -> int:
    """Insert a weekly report. Returns the new ID."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO reports (report_date, week_start, week_end, sleep_debt,
                           average_mood, average_sleep_time, average_quality, insights)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record.report_date,
        record.week_start,
        record.week_end,
        record.sleep_debt,
        record.average_mood,
        record.average_sleep_time,
        record.average_quality,
        record.insights,
    ))

    report_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return report_id


def get_latest_report() -> Optional[ReportRecord]:
    """Get the most recently created report."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM reports ORDER BY created_at DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return ReportRecord.from_row(row) if row else None


def get_all_reports() -> List[ReportRecord]:
    """Get all reports ordered by date (newest first)."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM reports ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [ReportRecord.from_row(row) for row in rows]
