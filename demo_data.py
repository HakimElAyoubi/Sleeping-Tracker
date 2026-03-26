"""
Demo Data
=========
Populates the database with sample data for demonstration purposes.
"""

import json
from pathlib import Path
from datetime import date, timedelta
from database_hakim import (
    init_database,
    add_sleep_record,
    insert_habit,
    get_record_count,
    SleepRecord,
    HabitRecord,
)

# Sample data for the last 14 days (starting from yesterday so user can log today)
DEMO_RECORDS = [
    # (days_ago, bedtime, wake_time, quality, mood, notes, coffee, exercise, screen)
    (1, "00:15", "07:00", 3, 3, "Stayed up a bit late", True, False, True),
    (2, "23:00", "06:45", 5, 5, "Great sleep", False, True, False),
    (3, "23:45", "07:30", 4, 4, None, False, False, False),
    (4, "01:00", "08:00", 2, 2, "Couldn't fall asleep", True, False, True),
    (5, "22:30", "06:30", 5, 5, "Early night, feeling great", False, True, False),
    (6, "23:15", "07:00", 4, 4, None, False, True, False),
    (7, "00:00", "07:30", 3, 3, "Weekend late night", True, False, True),
    (8, "23:30", "07:00", 4, 4, None, False, False, False),
    (9, "23:00", "06:45", 4, 5, "Morning workout planned", False, True, False),
    (10, "00:30", "07:15", 3, 3, "Movie night", False, False, True),
    (11, "23:15", "07:00", 4, 4, None, True, True, False),
    (12, "22:45", "06:30", 5, 5, "Best sleep this week", False, True, False),
    (13, "23:30", "07:15", 4, 4, None, False, False, False),
    (14, "23:00", "07:00", 4, 4, "Felt rested", False, True, False),
]


def calculate_duration(bedtime: str, wake_time: str) -> float:
    """Calculate sleep duration in hours."""
    bt_h, bt_m = map(int, bedtime.split(":"))
    wt_h, wt_m = map(int, wake_time.split(":"))

    bt_mins = bt_h * 60 + bt_m
    wt_mins = wt_h * 60 + wt_m

    if wt_mins < bt_mins:
        duration = (1440 - bt_mins) + wt_mins
    else:
        duration = wt_mins - bt_mins

    return round(duration / 60, 2)


def _has_consent():
    """Check if user has given consent."""
    settings_path = Path(__file__).parent / "settings.json"
    if settings_path.exists():
        with open(settings_path, "r") as f:
            settings = json.load(f)
            return settings.get("consent_given", False)
    return False


def populate_demo_data():
    """Insert demo data if database is empty and consent given."""
    init_database()

    # Only populate after user gives consent
    if not _has_consent():
        return

    if get_record_count() > 0:
        return  # Already has data

    today = date.today()

    for days_ago, bedtime, wake_time, quality, mood, notes, coffee, exercise, screen in DEMO_RECORDS:
        record_date = today - timedelta(days=days_ago)
        duration = calculate_duration(bedtime, wake_time)

        record = SleepRecord(
            date=record_date.strftime("%Y-%m-%d"),
            bedtime=bedtime,
            wake_time=wake_time,
            duration_hours=duration,
            quality_rating=quality,
            mood=mood,
            notes=notes,
        )

        try:
            record_id = add_sleep_record(record)

            habit = HabitRecord(
                sleep_record_id=record_id,
                took_coffee=coffee,
                exercised=exercise,
                used_screen=screen,
            )
            insert_habit(habit)
        except Exception:
            pass  # Skip if record already exists


if __name__ == "__main__":
    populate_demo_data()
    print("Demo data populated!")
