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
    try:
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

        return record_id
    finally:
        conn.close()


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
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM sleep_records ORDER BY date DESC")
        rows = cursor.fetchall()

        return [SleepRecord.from_row(row) for row in rows]
    finally:
        conn.close()


def get_record_by_date(date: str) -> Optional[SleepRecord]:
    """
    Get a sleep record for a specific date.

    Args:
        date: Date string in YYYY-MM-DD format

    Returns:
        SleepRecord if found, None otherwise
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM sleep_records WHERE date = ?", (date,))
        row = cursor.fetchone()

        return SleepRecord.from_row(row) if row else None
    finally:
        conn.close()


def get_recent_records(limit: int = 7) -> List[SleepRecord]:
    """
    Get the most recent sleep records.

    Args:
        limit: Maximum number of records to return (default: 7)

    Returns:
        List of SleepRecord objects
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM sleep_records
            ORDER BY date DESC
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()

        return [SleepRecord.from_row(row) for row in rows]
    finally:
        conn.close()


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
    try:
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

        return updated
    finally:
        conn.close()


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
    try:
        cursor = conn.cursor()

        # Delete associated habits first (belt-and-suspenders with ON DELETE CASCADE)
        cursor.execute("DELETE FROM habits WHERE sleep_record_id = ?", (record_id,))
        cursor.execute("DELETE FROM sleep_records WHERE id = ?", (record_id,))

        deleted = cursor.rowcount > 0
        conn.commit()

        return deleted
    finally:
        conn.close()


# ============================================================================
# SLEEP RECORDS - UTILITIES
# ============================================================================

def get_record_count() -> int:
    """Get total number of sleep records."""
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM sleep_records")
        count = cursor.fetchone()[0]

        return count
    finally:
        conn.close()


def date_exists(date: str) -> bool:
    """Check if a record exists for the given date."""
    return get_record_by_date(date) is not None


# ============================================================================
# HABITS - CRUD
# ============================================================================

def insert_habit(record: HabitRecord) -> int:
    """Insert a habit record linked to a sleep record. Returns the new ID."""
    conn = get_connection()
    try:
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
        return habit_id
    finally:
        conn.close()


def get_habit_by_sleep_record_id(record_id: int) -> Optional[HabitRecord]:
    """Get the habit record for a specific sleep record."""
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM habits WHERE sleep_record_id = ?", (record_id,))
        row = cursor.fetchone()
        return HabitRecord.from_row(row) if row else None
    finally:
        conn.close()


def update_habit(sleep_record_id: int, record: HabitRecord) -> bool:
    """Update the habit record linked to a sleep record.

    Args:
        sleep_record_id: The sleep record this habit belongs to.
        record: HabitRecord with updated values.

    Returns:
        True if a row was updated, False otherwise.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE habits
            SET took_coffee = ?, exercised = ?, used_screen = ?
            WHERE sleep_record_id = ?
        """, (
            int(record.took_coffee),
            int(record.exercised),
            int(record.used_screen),
            sleep_record_id,
        ))

        updated = cursor.rowcount > 0
        conn.commit()
        return updated
    finally:
        conn.close()


def get_all_habits() -> List[HabitRecord]:
    """Get all habit records."""
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM habits")
        rows = cursor.fetchall()
        return [HabitRecord.from_row(row) for row in rows]
    finally:
        conn.close()


# ============================================================================
# REPORTS - CRUD
# ============================================================================

def insert_report(record: ReportRecord) -> int:
    """Insert a weekly report. Returns the new ID."""
    conn = get_connection()
    try:
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
        return report_id
    finally:
        conn.close()


def get_latest_report() -> Optional[ReportRecord]:
    """Get the most recently created report."""
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM reports ORDER BY created_at DESC LIMIT 1")
        row = cursor.fetchone()
        return ReportRecord.from_row(row) if row else None
    finally:
        conn.close()


def get_all_reports() -> List[ReportRecord]:
    """Get all reports ordered by date (newest first)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM reports ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [ReportRecord.from_row(row) for row in rows]
    finally:
        conn.close()


def delete_report(report_id: int) -> bool:
    """
    Delete a report by ID.

    Args:
        report_id: The database ID of the report to delete

    Returns:
        True if report was deleted, False if not found
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("DELETE FROM reports WHERE id = ?", (report_id,))

        deleted = cursor.rowcount > 0
        conn.commit()

        return deleted
    finally:
        conn.close()
