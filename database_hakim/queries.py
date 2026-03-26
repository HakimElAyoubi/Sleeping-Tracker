from typing import List, Optional
from .connection import get_connection
from .models import SleepRecord, HabitRecord, ReportRecord


def add_sleep_record(record: SleepRecord) -> int:

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sleep_records 
            (date, bedtime, wake_time, duration_hours,
            quality_rating, notes, mood)
            VALUES (?, ?, ?, ?, ?, ?, ?)""", 
            (
            record.date,record.bedtime, record.wake_time,
            record.duration_hours,record.quality_rating,
            record.notes,record.mood,
        ))
        record_id = cursor.lastrowid
        conn.commit()
        return record_id
    finally:
        conn.close()



def get_all_records() -> List[SleepRecord]:
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM sleep_records ORDER BY date DESC")
        rows = cursor.fetchall()

        return [SleepRecord.from_row(row) for row in rows]
    finally:
        conn.close()


def get_record_by_date(date: str) -> Optional[SleepRecord]:

    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM sleep_records WHERE date = ?", (date,))
        row = cursor.fetchone()

        return SleepRecord.from_row(row) if row else None
    finally:
        conn.close()



def update_sleep_record(record: SleepRecord) -> bool:

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




def delete_sleep_record(record_id: int) -> bool:
    """
if record was deleted, False if not found
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

def get_recent_records(limit: int = 7) -> List[SleepRecord]:

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
        
def date_exists(date: str) -> bool:
    """Check if a record exists for the given date."""
    return get_record_by_date(date) is not None



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

    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("DELETE FROM reports WHERE id = ?", (report_id,))

        deleted = cursor.rowcount > 0
        conn.commit()

        return deleted
    finally:
        conn.close()
