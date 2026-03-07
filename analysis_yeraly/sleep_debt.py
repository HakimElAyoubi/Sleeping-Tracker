"""
Sleep Debt Calculator
=====================
Calculates accumulated sleep debt based on recommended sleep hours.
"""

from typing import List, Dict, Any

# Default recommended sleep hours per night
DEFAULT_RECOMMENDED_HOURS = 8.0


def calculate_daily_debt(actual_hours: float, recommended_hours: float = DEFAULT_RECOMMENDED_HOURS) -> float:
    """
    Calculate sleep debt for a single night.

    Args:
        actual_hours: Hours actually slept
        recommended_hours: Target hours (default: 8)

    Returns:
        Sleep debt (positive = debt, negative = surplus)
    """
    return recommended_hours - actual_hours


def calculate_total_debt(sleep_records: List[Dict[str, Any]], recommended_hours: float = DEFAULT_RECOMMENDED_HOURS) -> float:
    """
    Calculate total accumulated sleep debt from a list of records.

    Args:
        sleep_records: List of records with 'duration_hours' field
        recommended_hours: Target hours per night

    Returns:
        Total sleep debt in hours
    """
    total_debt = 0.0
    for record in sleep_records:
        duration = record.get("duration_hours", 0) if isinstance(record, dict) else record.duration_hours
        total_debt += calculate_daily_debt(duration, recommended_hours)
    return total_debt


def calculate_weekly_debt(sleep_records: List[Dict[str, Any]], recommended_hours: float = DEFAULT_RECOMMENDED_HOURS) -> Dict[str, float]:
    """
    Calculate sleep debt summary for a week of records.

    Args:
        sleep_records: List of sleep records (should be ~7 days)
        recommended_hours: Target hours per night

    Returns:
        Dictionary with debt statistics
    """
    if not sleep_records:
        return {
            "total_debt": 0.0,
            "average_daily_debt": 0.0,
            "days_with_debt": 0,
            "days_with_surplus": 0,
            "total_sleep": 0.0,
            "average_sleep": 0.0
        }

    debts = []
    total_sleep = 0.0

    for record in sleep_records:
        duration = record.get("duration_hours", 0) if isinstance(record, dict) else record.duration_hours
        total_sleep += duration
        debts.append(calculate_daily_debt(duration, recommended_hours))

    total_debt = sum(debts)
    days_with_debt = sum(1 for d in debts if d > 0)
    days_with_surplus = sum(1 for d in debts if d < 0)

    return {
        "total_debt": round(total_debt, 2),
        "average_daily_debt": round(total_debt / len(debts), 2),
        "days_with_debt": days_with_debt,
        "days_with_surplus": days_with_surplus,
        "total_sleep": round(total_sleep, 2),
        "average_sleep": round(total_sleep / len(sleep_records), 2)
    }


def get_debt_status(total_debt: float) -> str:
    """
    Get a human-readable status based on sleep debt.

    Args:
        total_debt: Total accumulated sleep debt in hours

    Returns:
        Status string describing the debt level
    """
    if total_debt <= -3:
        return "Excellent - Sleep surplus"
    elif total_debt <= 0:
        return "Good - No sleep debt"
    elif total_debt <= 5:
        return "Mild - Small sleep debt"
    elif total_debt <= 10:
        return "Moderate - Consider catching up"
    else:
        return "Severe - Significant sleep debt"
