"""
Sleep Pattern Detection
=======================
Detects patterns and trends in sleep data.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime


def detect_consistency(sleep_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze consistency of sleep schedule.

    Args:
        sleep_records: List of sleep records with bedtime and wake_time

    Returns:
        Dictionary with consistency metrics
    """
    if len(sleep_records) < 2:
        return {
            "bedtime_variance": 0.0,
            "waketime_variance": 0.0,
            "is_consistent": True,
            "recommendation": "Need more data for analysis"
        }

    bedtimes_minutes = []
    waketimes_minutes = []

    for record in sleep_records:
        bedtime = record.get("bedtime") if isinstance(record, dict) else record.bedtime
        wake_time = record.get("wake_time") if isinstance(record, dict) else record.wake_time

        if bedtime and wake_time:
            bt_parts = bedtime.split(":")
            wt_parts = wake_time.split(":")

            bt_minutes = int(bt_parts[0]) * 60 + int(bt_parts[1])
            wt_minutes = int(wt_parts[0]) * 60 + int(wt_parts[1])

            # Handle times after midnight for bedtime
            if bt_minutes < 360:  # Before 6 AM, assume it's actually late night
                bt_minutes += 1440

            bedtimes_minutes.append(bt_minutes)
            waketimes_minutes.append(wt_minutes)

    if not bedtimes_minutes:
        return {
            "bedtime_variance": 0.0,
            "waketime_variance": 0.0,
            "is_consistent": True,
            "recommendation": "No valid time data"
        }

    # Calculate variance (standard deviation in minutes)
    def variance(values):
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        return (sum((x - mean) ** 2 for x in values) / len(values)) ** 0.5

    bt_var = variance(bedtimes_minutes)
    wt_var = variance(waketimes_minutes)

    # Consistent if variance is less than 60 minutes
    is_consistent = bt_var < 60 and wt_var < 60

    if is_consistent:
        recommendation = "Great! Your sleep schedule is consistent."
    elif bt_var >= 60 and wt_var >= 60:
        recommendation = "Try to maintain more regular bedtime and wake times."
    elif bt_var >= 60:
        recommendation = "Try to go to bed at the same time each night."
    else:
        recommendation = "Try to wake up at the same time each day."

    return {
        "bedtime_variance": round(bt_var, 1),
        "waketime_variance": round(wt_var, 1),
        "is_consistent": is_consistent,
        "recommendation": recommendation
    }


def detect_trend(sleep_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Detect if sleep duration is improving, declining, or stable.

    Args:
        sleep_records: List of sleep records ordered by date (oldest first)

    Returns:
        Dictionary with trend information
    """
    if len(sleep_records) < 3:
        return {
            "trend": "insufficient_data",
            "slope": 0.0,
            "description": "Need at least 3 records for trend analysis"
        }

    durations = []
    for record in sleep_records:
        duration = record.get("duration_hours", 0) if isinstance(record, dict) else record.duration_hours
        durations.append(duration)

    # Simple linear regression slope
    n = len(durations)
    x_mean = (n - 1) / 2
    y_mean = sum(durations) / n

    numerator = sum((i - x_mean) * (durations[i] - y_mean) for i in range(n))
    denominator = sum((i - x_mean) ** 2 for i in range(n))

    slope = numerator / denominator if denominator != 0 else 0

    # Interpret slope (hours per day change)
    if slope > 0.05:
        trend = "improving"
        description = "Your sleep duration is increasing over time."
    elif slope < -0.05:
        trend = "declining"
        description = "Your sleep duration is decreasing over time."
    else:
        trend = "stable"
        description = "Your sleep duration is relatively stable."

    return {
        "trend": trend,
        "slope": round(slope, 3),
        "description": description
    }


def identify_best_worst_days(sleep_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Identify days with best and worst sleep.

    Args:
        sleep_records: List of sleep records

    Returns:
        Dictionary with best/worst day information
    """
    if not sleep_records:
        return {"best_day": None, "worst_day": None}

    def get_score(record):
        duration = record.get("duration_hours", 0) if isinstance(record, dict) else record.duration_hours
        quality = record.get("quality_rating") if isinstance(record, dict) else record.quality_rating
        # Combine duration and quality (quality is optional)
        if quality:
            return duration * 0.7 + quality * 0.6
        return duration

    sorted_records = sorted(sleep_records, key=get_score, reverse=True)

    best = sorted_records[0]
    worst = sorted_records[-1]

    return {
        "best_day": {
            "date": best.get("date") if isinstance(best, dict) else best.date,
            "duration": best.get("duration_hours") if isinstance(best, dict) else best.duration_hours,
            "quality": best.get("quality_rating") if isinstance(best, dict) else best.quality_rating
        },
        "worst_day": {
            "date": worst.get("date") if isinstance(worst, dict) else worst.date,
            "duration": worst.get("duration_hours") if isinstance(worst, dict) else worst.duration_hours,
            "quality": worst.get("quality_rating") if isinstance(worst, dict) else worst.quality_rating
        }
    }
