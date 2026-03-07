# API Contract - Frontend Requirements

This document defines the Python function interfaces that the frontend (`frontend_siyuan`) expects from the backend modules. Share this with your teammates so they can implement the required functions.

---

## 1. Database Module (`database_hakim`)

### Already Implemented

These functions exist and the frontend currently uses them:

```python
from database_hakim import (
    init_database,
    add_sleep_record,
    get_all_records,
    get_recent_records,
    get_record_by_date,
    date_exists,
    SleepRecord,
)
```

| Function | Signature | Returns | Status |
|---|---|---|---|
| `init_database()` | `() -> None` | Creates tables if not exist | Done |
| `add_sleep_record(record)` | `(SleepRecord) -> int` | New record ID | Done |
| `get_all_records()` | `() -> List[SleepRecord]` | All records (newest first) | Done |
| `get_recent_records(limit)` | `(int) -> List[SleepRecord]` | Last N records | Done |
| `get_record_by_date(date)` | `(str "YYYY-MM-DD") -> Optional[SleepRecord]` | Record or None | Done |
| `date_exists(date)` | `(str "YYYY-MM-DD") -> bool` | True if record exists | Done |

#### `SleepRecord` dataclass (current)

```python
@dataclass
class SleepRecord:
    date: str                      # "YYYY-MM-DD"
    bedtime: str                   # "HH:MM" (24h)
    wake_time: str                 # "HH:MM" (24h)
    duration_hours: float
    quality_rating: Optional[int]  # 1-5
    notes: Optional[str] = None
    id: Optional[int] = None
```

### Requested Additions

The project report specifies a **habits** table. The frontend needs a way to store daily habits alongside sleep data. Hakim, please consider adding:

#### Option A: Extend `SleepRecord` with habit fields

```python
@dataclass
class SleepRecord:
    # ... existing fields ...
    had_caffeine: Optional[bool] = None
    had_exercise: Optional[bool] = None
    screen_time_minutes: Optional[int] = None  # screen time before bed
```

#### Option B: Separate `HabitRecord` model + CRUD

```python
@dataclass
class HabitRecord:
    date: str            # "YYYY-MM-DD"
    had_caffeine: bool
    had_exercise: bool
    screen_time_minutes: int  # minutes of screen before bed
    id: Optional[int] = None

def add_habit_record(record: HabitRecord) -> int: ...
def get_habit_by_date(date: str) -> Optional[HabitRecord]: ...
```

**Frontend preference:** Option A is simpler for us. Either works.

---

## 2. Analysis Module (`analysis_yeraly`)

The frontend needs the following functions. Currently none are implemented, so the frontend uses temporary local helpers. Once Yeraly implements these, the frontend will switch to importing them.

### Required Functions

```python
# analysis_yeraly/algorithms.py

def calculate_sleep_debt(records: list, target_hours: float = 8.0) -> float:
    """
    Calculate cumulative sleep debt.

    Args:
        records: List of SleepRecord objects.
        target_hours: Ideal sleep per night (default 8.0).

    Returns:
        Total debt in hours (positive = under-slept, negative = over-slept).
    """

def get_streak_count(records: list) -> int:
    """
    Count consecutive days with a check-in, ending at today.

    Args:
        records: List of SleepRecord objects (any order).

    Returns:
        Number of consecutive days (0 if no record today).
    """

def get_weekly_summary(records: list) -> dict:
    """
    Generate a weekly summary from the last 7 days of records.

    Args:
        records: List of SleepRecord objects for the week.

    Returns:
        Dictionary with keys:
        {
            "total_logs": int,
            "avg_duration": float,
            "avg_quality": float,
            "best_night": float,
            "worst_night": float,
            "sleep_debt": float,
            "streak": int,
        }
    """
```

---

## 3. System Module (`system_yibo`)

The frontend does not currently depend on `system_yibo`. However, Yibo will need to:

1. Update `app.py` at the project root to call the frontend:

```python
# app.py
from frontend_siyuan.pages import render
render()
```

2. Ensure `init_database()` is called once at startup (the frontend currently handles this, but it could be moved to system-level initialization).

---

## 4. How to Run (for teammates)

```bash
# From project root
pip install -r frontend_siyuan/requirements.txt
streamlit run app.py
```

The frontend entry point is `frontend_siyuan.pages.render()`.
