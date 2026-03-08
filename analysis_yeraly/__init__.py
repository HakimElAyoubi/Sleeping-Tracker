"""
Analysis Module - Yeraly's Workspace
====================================
Sleep analysis algorithms, pattern detection, and report generation.

Quick Start:
    from analysis_yeraly import (
        calculate_duration,
        calculate_weekly_debt,
        detect_consistency,
        generate_weekly_report
    )

    # Calculate sleep duration
    hours = calculate_duration("23:00", "07:00")  # Returns 8.0

    # Analyze sleep debt
    records = [{"duration_hours": 7}, {"duration_hours": 6}, {"duration_hours": 8}]
    debt = calculate_weekly_debt(records)

    # Generate full report
    report = generate_weekly_report(records)

Available Functions:

Sleep Debt:
    - calculate_daily_debt(actual, recommended)
    - calculate_total_debt(records, recommended)
    - calculate_weekly_debt(records, recommended)
    - get_debt_status(total_debt)

Patterns:
    - detect_consistency(records)
    - detect_trend(records)
    - identify_best_worst_days(records)

Reports:
    - generate_weekly_report(records, recommended)
    - generate_summary_stats(records)
    - format_report_text(report)

Utilities:
    - calculate_duration(bedtime, wake_time)
    - calculate_sleep_quality_score(duration, quality, consistency)
    - categorize_sleep_duration(hours)
    - get_sleep_recommendation(avg_hours, avg_quality)
"""

# Core algorithms
from .algorithms import (
    calculate_duration,
    calculate_sleep_quality_score,
    categorize_sleep_duration,
    get_sleep_recommendation,
)

# Sleep debt calculations
from .sleep_debt import (
    calculate_daily_debt,
    calculate_total_debt,
    calculate_weekly_debt,
    get_debt_status,
    DEFAULT_RECOMMENDED_HOURS,
)

# Pattern detection
from .patterns import (
    detect_consistency,
    detect_trend,
    identify_best_worst_days,
)

# Report generation
from .reports import (
    generate_weekly_report,
    generate_summary_stats,
    format_report_text,
)
