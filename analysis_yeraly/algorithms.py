"""
Analysis Algorithms - Yeraly
============================
Sleep analysis, habit correlations, advice generation, and report summaries.
"""

from datetime import date, timedelta


def calculate_duration(bedtime_str, wake_time_str):
    """Calculate sleep duration in hours, handling overnight sleep."""
    bed_h, bed_m = map(int, bedtime_str.split(":"))
    wake_h, wake_m = map(int, wake_time_str.split(":"))
    bed_total = bed_h * 60 + bed_m
    wake_total = wake_h * 60 + wake_m
    if wake_total <= bed_total:
        diff = (24 * 60 - bed_total) + wake_total
    else:
        diff = wake_total - bed_total
    return round(diff / 60, 2)


def calculate_sleep_debt(records, target_hours=8.0):
    """Cumulative sleep debt (positive = under-slept)."""
    return round(sum(target_hours - r.duration_hours for r in records), 1)


def get_streak(records):
    """Count consecutive check-in days ending at today."""
    if not records:
        return 0
    dates = sorted({r.date for r in records}, reverse=True)
    streak = 0
    expected = date.today()
    for d in dates:
        if d == expected.strftime("%Y-%m-%d"):
            streak += 1
            expected -= timedelta(days=1)
        else:
            break
    return streak


def analyze_habit_correlations(sleep_records, habits):
    """
    For each habit (coffee, exercise, screen), compare average sleep quality
    and duration on days WITH the habit vs days WITHOUT.

    Args:
        sleep_records: list of SleepRecord objects (must have .id, .quality_rating, .duration_hours)
        habits: list of HabitRecord objects (must have .sleep_record_id, .took_coffee, .exercised, .used_screen)

    Returns:
        dict mapping habit name to quality_diff, duration_diff, sample_with, sample_without
    """
    if not sleep_records or not habits:
        return {}

    # Build a map from sleep_record_id -> (quality, duration)
    record_map = {}
    for r in sleep_records:
        if r.id is not None:
            record_map[r.id] = (r.quality_rating, r.duration_hours)

    # Build a map from sleep_record_id -> habit
    habit_map = {}
    for h in habits:
        habit_map[h.sleep_record_id] = h

    result = {}
    for habit_name, habit_attr in [("coffee", "took_coffee"), ("exercise", "exercised"), ("screen", "used_screen")]:
        with_quality, with_duration = [], []
        without_quality, without_duration = [], []

        for rec_id, (quality, duration) in record_map.items():
            habit = habit_map.get(rec_id)
            if habit is None:
                continue
            if getattr(habit, habit_attr):
                if quality is not None:
                    with_quality.append(quality)
                with_duration.append(duration)
            else:
                if quality is not None:
                    without_quality.append(quality)
                without_duration.append(duration)

        avg_q_with = sum(with_quality) / len(with_quality) if with_quality else 0
        avg_q_without = sum(without_quality) / len(without_quality) if without_quality else 0
        avg_d_with = sum(with_duration) / len(with_duration) if with_duration else 0
        avg_d_without = sum(without_duration) / len(without_duration) if without_duration else 0

        result[habit_name] = {
            "quality_diff": round(avg_q_with - avg_q_without, 2) if with_quality and without_quality else 0,
            "duration_diff": round(avg_d_with - avg_d_without, 2) if with_duration and without_duration else 0,
            "sample_with": len(with_duration),
            "sample_without": len(without_duration),
        }

    return result


def generate_advice(sleep_records, habits, sleep_debt):
    """
    Return a list of advice strings based on detected patterns.
    Returns empty list if insufficient data (< 3 records).
    """
    if len(sleep_records) < 3:
        return []

    advice = []

    # Sleep debt advice
    if sleep_debt > 5:
        advice.append("You've accumulated significant sleep debt. Try sleeping 30 minutes earlier this week.")
    elif sleep_debt > 2:
        advice.append("You have some sleep debt building up. Consider an earlier bedtime tonight.")

    # Habit correlations
    correlations = analyze_habit_correlations(sleep_records, habits)

    if correlations.get("coffee", {}).get("quality_diff", 0) < -0.3:
        diff = abs(correlations["coffee"]["quality_diff"])
        advice.append(f"On days you drink coffee, your sleep quality drops by {diff:.1f}. Consider reducing caffeine.")

    if correlations.get("exercise", {}).get("quality_diff", 0) > 0.3:
        diff = correlations["exercise"]["quality_diff"]
        advice.append(f"Great news! Exercise seems to improve your sleep quality by {diff:.1f}.")

    if correlations.get("screen", {}).get("quality_diff", 0) < -0.3:
        advice.append("Screen time before bed appears to reduce your sleep quality.")

    # Average quality advice
    qualities = [r.quality_rating for r in sleep_records if r.quality_rating]
    if qualities:
        avg_quality = sum(qualities) / len(qualities)
        if avg_quality < 3:
            advice.append("Your average sleep quality is below average. Try to maintain a consistent bedtime.")

    # Streak advice
    streak = get_streak(sleep_records)
    if streak > 7:
        advice.append("Amazing streak! Keep up the consistent tracking.")

    return advice


def generate_weekly_summary(sleep_records, habits):
    """
    Return a dict with summary statistics for the weekly report.
    Expects the last 7 days of records.

    Returns dict with: avg_duration, avg_quality, avg_mood, total_debt,
    best_day, worst_day, habit_correlations, advice_list.
    """
    if not sleep_records:
        return None

    durations = [r.duration_hours for r in sleep_records]
    qualities = [r.quality_rating for r in sleep_records if r.quality_rating]
    moods = [r.mood for r in sleep_records if r.mood]

    avg_duration = sum(durations) / len(durations)
    avg_quality = sum(qualities) / len(qualities) if qualities else 0
    avg_mood = sum(moods) / len(moods) if moods else 0

    total_debt = calculate_sleep_debt(sleep_records)

    # Best and worst day by duration
    best_record = max(sleep_records, key=lambda r: r.duration_hours)
    worst_record = min(sleep_records, key=lambda r: r.duration_hours)

    correlations = analyze_habit_correlations(sleep_records, habits)
    advice_list = generate_advice(sleep_records, habits, total_debt)

    return {
        "avg_duration": round(avg_duration, 1),
        "avg_quality": round(avg_quality, 1),
        "avg_mood": round(avg_mood, 1),
        "total_debt": total_debt,
        "best_day": {"date": best_record.date, "duration": best_record.duration_hours},
        "worst_day": {"date": worst_record.date, "duration": worst_record.duration_hours},
        "habit_correlations": correlations,
        "advice_list": advice_list,
    }
