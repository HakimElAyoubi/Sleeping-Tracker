
from dataclasses import dataclass
from typing import Optional
from datetime import date, time


@dataclass
class SleepRecord:
    """Represents a single sleep record."""
    date: str                      # Format: YYYY-MM-DD
    bedtime: str                   # Format: HH:MM (24-hour)
    wake_time: str                 # Format: HH:MM (24-hour)
    duration_hours: float          # Calculated sleep duration
    quality_rating: Optional[int]  # 1-5 scale (optional)
    notes: Optional[str] = None    # Optional notes
    mood: Optional[int] = None     # 1-5 scale (optional)
    id: Optional[int] = None       # Database ID (set after insert)

    def to_dict(self) -> dict:
        """Convert to dictionary for easy serialization."""
        return {
            "id": self.id,
            "date": self.date,
            "bedtime": self.bedtime,
            "wake_time": self.wake_time,
            "duration_hours": self.duration_hours,
            "quality_rating": self.quality_rating,
            "notes": self.notes,
            "mood": self.mood,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SleepRecord":
        """Create a SleepRecord from a dictionary."""
        return cls(
            id=data.get("id"),
            date=data["date"],
            bedtime=data["bedtime"],
            wake_time=data["wake_time"],
            duration_hours=data["duration_hours"],
            quality_rating=data.get("quality_rating"),
            notes=data.get("notes"),
            mood=data.get("mood"),
        )

    @classmethod
    def from_row(cls, row) -> "SleepRecord":
        """Create a SleepRecord from a database row."""
        keys = row.keys() if hasattr(row, "keys") else []
        return cls(
            id=row["id"],
            date=row["date"],
            bedtime=row["bedtime"],
            wake_time=row["wake_time"],
            duration_hours=row["duration_hours"],
            quality_rating=row["quality_rating"],
            notes=row["notes"],
            mood=row["mood"] if "mood" in keys else None,
        )


@dataclass
class HabitRecord:
    """Represents daily habit data linked to a sleep record."""
    sleep_record_id: int
    took_coffee: bool = False
    exercised: bool = False
    used_screen: bool = False
    id: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "sleep_record_id": self.sleep_record_id,
            "took_coffee": self.took_coffee,
            "exercised": self.exercised,
            "used_screen": self.used_screen,
        }

    @classmethod
    def from_row(cls, row) -> "HabitRecord":
        return cls(
            id=row["id"],
            sleep_record_id=row["sleep_record_id"],
            took_coffee=bool(row["took_coffee"]),
            exercised=bool(row["exercised"]),
            used_screen=bool(row["used_screen"]),
        )


@dataclass
class ReportRecord:
    """Represents a saved weekly report."""
    report_date: str
    week_start: str
    week_end: str
    sleep_debt: float = 0.0
    average_mood: Optional[float] = None
    average_sleep_time: Optional[float] = None
    average_quality: Optional[float] = None
    insights: Optional[str] = None
    created_at: Optional[str] = None
    id: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "report_date": self.report_date,
            "week_start": self.week_start,
            "week_end": self.week_end,
            "sleep_debt": self.sleep_debt,
            "average_mood": self.average_mood,
            "average_sleep_time": self.average_sleep_time,
            "average_quality": self.average_quality,
            "insights": self.insights,
            "created_at": self.created_at,
        }

    @classmethod
    def from_row(cls, row) -> "ReportRecord":
        return cls(
            id=row["id"],
            report_date=row["report_date"],
            week_start=row["week_start"],
            week_end=row["week_end"],
            sleep_debt=row["sleep_debt"],
            average_mood=row["average_mood"],
            average_sleep_time=row["average_sleep_time"],
            average_quality=row["average_quality"],
            insights=row["insights"],
            created_at=row["created_at"],
        )
