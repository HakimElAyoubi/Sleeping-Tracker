"""
Data Models
============
Data structures for sleep tracking.
These can be used by other modules for type hints and data validation.
"""

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
            "notes": self.notes
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
            notes=data.get("notes")
        )

    @classmethod
    def from_row(cls, row) -> "SleepRecord":
        """Create a SleepRecord from a database row."""
        return cls(
            id=row["id"],
            date=row["date"],
            bedtime=row["bedtime"],
            wake_time=row["wake_time"],
            duration_hours=row["duration_hours"],
            quality_rating=row["quality_rating"],
            notes=row["notes"]
        )
