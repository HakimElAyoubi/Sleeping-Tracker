"""
Core Analysis Algorithms
========================
Utility functions for sleep calculations.
"""

from datetime import datetime, timedelta
from typing import Tuple


def calculate_duration(bedtime: str, wake_time: str) -> float:
    """
    Calculate sleep duration from bedtime and wake time.

    Args:
        bedtime: Bedtime in HH:MM format (24-hour)
        wake_time: Wake time in HH:MM format (24-hour)

    Returns:
        Duration in hours (float)
    """
    bt_parts = bedtime.split(":")
    wt_parts = wake_time.split(":")

    bt_hour, bt_min = int(bt_parts[0]), int(bt_parts[1])
    wt_hour, wt_min = int(wt_parts[0]), int(wt_parts[1])

    # Create time deltas
    bedtime_minutes = bt_hour * 60 + bt_min
    waketime_minutes = wt_hour * 60 + wt_min

    # Handle overnight sleep (bedtime after midnight handling)
    if waketime_minutes < bedtime_minutes:
        # Crossed midnight
        duration_minutes = (1440 - bedtime_minutes) + waketime_minutes
    else:
        duration_minutes = waketime_minutes - bedtime_minutes

    return round(duration_minutes / 60, 2)


def calculate_sleep_quality_score(
    duration_hours: float,
    quality_rating: int = None,
    consistency_bonus: bool = False
) -> float:
    """
    Calculate an overall sleep quality score (0-100).

    Args:
        duration_hours: Hours slept
        quality_rating: Self-reported quality 1-5 (optional)
        consistency_bonus: Add bonus for consistent schedule

    Returns:
        Score from 0 to 100
    """
    score = 0.0

    # Duration score (0-50 points)
    # Optimal is 7-9 hours
    if 7 <= duration_hours <= 9:
        score += 50
    elif 6 <= duration_hours < 7:
        score += 40
    elif 9 < duration_hours <= 10:
        score += 40
    elif 5 <= duration_hours < 6:
        score += 25
    elif duration_hours > 10:
        score += 30
    else:
        score += max(0, duration_hours * 5)

    # Quality rating score (0-40 points)
    if quality_rating is not None:
        score += quality_rating * 8

    # Consistency bonus (0-10 points)
    if consistency_bonus:
        score += 10

    return min(100, round(score, 1))


def categorize_sleep_duration(duration_hours: float) -> str:
    """
    Categorize sleep duration.

    Args:
        duration_hours: Hours slept

    Returns:
        Category string
    """
    if duration_hours < 4:
        return "Very Short"
    elif duration_hours < 6:
        return "Short"
    elif duration_hours < 7:
        return "Slightly Short"
    elif duration_hours <= 9:
        return "Optimal"
    elif duration_hours <= 10:
        return "Slightly Long"
    else:
        return "Long"


def get_sleep_recommendation(average_hours: float, average_quality: float = None) -> str:
    """
    Get personalized sleep recommendation.

    Args:
        average_hours: Average sleep duration
        average_quality: Average quality rating (1-5)

    Returns:
        Recommendation string
    """
    recommendations = []

    if average_hours < 7:
        recommendations.append("Try to get at least 7 hours of sleep per night.")
    elif average_hours > 9:
        recommendations.append("You may be oversleeping. Aim for 7-9 hours.")

    if average_quality is not None:
        if average_quality < 3:
            recommendations.append("Your sleep quality is low. Consider improving sleep hygiene.")
        elif average_quality >= 4:
            recommendations.append("Great sleep quality! Keep up the good habits.")

    if not recommendations:
        recommendations.append("Your sleep patterns look healthy. Maintain your current routine.")

    return " ".join(recommendations)
