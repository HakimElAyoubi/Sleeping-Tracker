"""
Database Module - Hakim's Workspace
===================================
SQLite database for sleep tracking.

Quick Start:
    from database_hakim import init_database, add_sleep_record, get_all_records, SleepRecord

    # Initialize database (call once at app startup)
    init_database()

    # Add a record
    record = SleepRecord(
        date="2024-01-15",
        bedtime="23:00",
        wake_time="07:00",
        duration_hours=8.0,
        quality_rating=4,
        notes="Slept well"
    )
    record_id = add_sleep_record(record)

    # Get all records
    records = get_all_records()

Available Functions:
    - init_database()           : Initialize database tables (call at startup)
    - add_sleep_record(record)  : Add a new sleep record
    - get_all_records()         : Get all records
    - get_record_by_id(id)      : Get single record by ID
    - get_record_by_date(date)  : Get record for specific date
    - get_records_in_range(start, end) : Get records in date range
    - get_recent_records(limit) : Get most recent records
    - update_sleep_record(record) : Update existing record
    - delete_sleep_record(id)   : Delete record by ID
    - get_record_count()        : Get total record count
    - date_exists(date)         : Check if date has a record
    - insert_habit(record)      : Add a habit record
    - get_habits_by_date_range(start, end) : Get habits in date range
    - get_habit_by_sleep_record_id(id) : Get habit for a sleep record
    - get_all_habits()          : Get all habit records
    - insert_report(record)     : Save a weekly report
    - get_latest_report()       : Get most recent report
    - get_all_reports()         : Get all reports

Data Models:
    - SleepRecord: Dataclass representing a sleep entry
    - HabitRecord: Dataclass representing daily habits
    - ReportRecord: Dataclass representing a weekly report
"""

# Connection and initialization
from .connection import init_database, get_connection

# Data models
from .models import SleepRecord, HabitRecord, ReportRecord

# CRUD operations
from .queries import (
    add_sleep_record,
    get_all_records,
    get_record_by_id,
    get_record_by_date,
    get_records_in_range,
    get_recent_records,
    update_sleep_record,
    delete_sleep_record,
    get_record_count,
    date_exists,
    insert_habit,
    get_habits_by_date_range,
    get_habit_by_sleep_record_id,
    get_all_habits,
    insert_report,
    get_latest_report,
    get_all_reports,
)
