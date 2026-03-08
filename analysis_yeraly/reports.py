"""
Report Generation
=================
Generate sleep analysis reports and summaries.
"""

from typing import List, Dict, Any
from .sleep_debt import calculate_weekly_debt, get_debt_status
from .patterns import detect_consistency, detect_trend, identify_best_worst_days


def generate_weekly_report(sleep_records: List[Dict[str, Any]], recommended_hours: float = 8.0) -> Dict[str, Any]:
    """
    Generate a comprehensive weekly sleep report.

    Args:
        sleep_records: List of sleep records for the week
        recommended_hours: Target sleep hours per night

    Returns:
        Dictionary containing full weekly analysis
    """
    if not sleep_records:
        return {
            "summary": "No sleep data available for this period.",
            "debt": None,
            "consistency": None,
            "trend": None,
            "highlights": None
        }

    # Calculate all metrics
    debt_stats = calculate_weekly_debt(sleep_records, recommended_hours)
    consistency = detect_consistency(sleep_records)
    trend = detect_trend(sleep_records)
    highlights = identify_best_worst_days(sleep_records)

    # Generate summary text
    summary_parts = []

    summary_parts.append(f"Analyzed {len(sleep_records)} nights of sleep.")
    summary_parts.append(f"Average sleep: {debt_stats['average_sleep']} hours/night.")
    summary_parts.append(f"Sleep debt status: {get_debt_status(debt_stats['total_debt'])}")

    if consistency["is_consistent"]:
        summary_parts.append("Your sleep schedule is consistent.")
    else:
        summary_parts.append(consistency["recommendation"])

    return {
        "summary": " ".join(summary_parts),
        "debt": debt_stats,
        "consistency": consistency,
        "trend": trend,
        "highlights": highlights,
        "record_count": len(sleep_records)
    }


def generate_summary_stats(sleep_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate quick summary statistics.

    Args:
        sleep_records: List of sleep records

    Returns:
        Dictionary with summary statistics
    """
    if not sleep_records:
        return {
            "total_records": 0,
            "average_duration": 0.0,
            "min_duration": 0.0,
            "max_duration": 0.0,
            "average_quality": None
        }

    durations = []
    qualities = []

    for record in sleep_records:
        duration = record.get("duration_hours", 0) if isinstance(record, dict) else record.duration_hours
        quality = record.get("quality_rating") if isinstance(record, dict) else record.quality_rating

        durations.append(duration)
        if quality is not None:
            qualities.append(quality)

    avg_quality = round(sum(qualities) / len(qualities), 1) if qualities else None

    return {
        "total_records": len(sleep_records),
        "average_duration": round(sum(durations) / len(durations), 2),
        "min_duration": round(min(durations), 2),
        "max_duration": round(max(durations), 2),
        "average_quality": avg_quality
    }


def format_report_text(report: Dict[str, Any]) -> str:
    """
    Format a report dictionary as readable text.

    Args:
        report: Report dictionary from generate_weekly_report

    Returns:
        Formatted text string
    """
    if not report.get("debt"):
        return report.get("summary", "No data available.")

    lines = [
        "=" * 40,
        "WEEKLY SLEEP REPORT",
        "=" * 40,
        "",
        report["summary"],
        "",
        "--- Sleep Debt ---",
        f"Total debt: {report['debt']['total_debt']} hours",
        f"Average daily debt: {report['debt']['average_daily_debt']} hours",
        f"Days under target: {report['debt']['days_with_debt']}",
        f"Days over target: {report['debt']['days_with_surplus']}",
        "",
        "--- Consistency ---",
        f"Bedtime variance: {report['consistency']['bedtime_variance']} minutes",
        f"Wake time variance: {report['consistency']['waketime_variance']} minutes",
        f"Status: {'Consistent' if report['consistency']['is_consistent'] else 'Inconsistent'}",
        "",
        "--- Trend ---",
        f"Direction: {report['trend']['trend']}",
        report['trend']['description'],
        "",
        "=" * 40
    ]

    return "\n".join(lines)
