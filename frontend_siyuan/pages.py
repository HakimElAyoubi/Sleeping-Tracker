"""
Frontend Pages - Siyuan
=======================
Streamlit UI for the Sleep Tracker.

Usage:
    from frontend_siyuan.pages import render
    render()
"""

import streamlit as st
import json
import os
from datetime import datetime, date, timedelta
from pathlib import Path

from database_hakim import (
    init_database,
    add_sleep_record,
    get_all_records,
    get_recent_records,
    get_record_by_date,
    get_record_count,
    date_exists,
    insert_habit,
    get_all_habits,
    get_habit_by_sleep_record_id,
    insert_report,
    get_latest_report,
    get_all_reports,
    SleepRecord,
    HabitRecord,
    ReportRecord,
)

from analysis_yeraly import (
    calculate_duration,
    calculate_sleep_debt,
    get_streak,
    analyze_habit_correlations,
    generate_advice,
    generate_weekly_summary,
)

# Path to local settings/consent file
_SETTINGS_PATH = Path(__file__).parent.parent / "settings.json"


def _load_settings():
    """Load settings from local JSON file."""
    if _SETTINGS_PATH.exists():
        with open(_SETTINGS_PATH, "r") as f:
            return json.load(f)
    return {}


def _save_settings(settings):
    """Save settings to local JSON file."""
    with open(_SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2)


def _get_target_hours():
    """Get the user's target sleep hours from settings."""
    settings = _load_settings()
    return settings.get("target_hours", 8.0)


# ============================================================================
# Page: User Consent
# ============================================================================

def _page_consent():
    """Show consent screen on first launch."""
    st.header("Welcome to Sleep Tracker")
    st.write("Before we begin, please review our data practices.")

    st.subheader("What data we collect")
    st.markdown("""
    - **Sleep times**: Your bedtime and wake-up time each day
    - **Sleep quality**: A self-reported rating (1-5)
    - **Mood**: Your daily mood rating (1-5)
    - **Habits**: Whether you consumed caffeine, exercised, or used screens before bed
    - **Notes**: Any optional notes you add
    """)

    st.subheader("How your data is stored")
    st.markdown("""
    - All data is stored **locally on your device** in a SQLite database file.
    - **No data is sent to any server** or third party.
    - You can **delete all your data at any time** from the Settings page.
    """)

    if st.button("I understand and consent", type="primary"):
        settings = _load_settings()
        settings["consent_given"] = True
        _save_settings(settings)
        st.rerun()


# ============================================================================
# Page: Daily Check-in
# ============================================================================

def _page_checkin():
    st.header("Daily Sleep Check-in")

    today = date.today()
    if date_exists(today.strftime("%Y-%m-%d")):
        st.success("You've already logged your sleep for today!")
        st.info("Come back tomorrow for your next check-in.")
        return

    with st.form("checkin_form"):
        log_date = st.date_input("Date", value=today, max_value=today)

        col1, col2 = st.columns(2)
        with col1:
            bedtime = st.time_input(
                "Bedtime (last night)",
                value=datetime.strptime("23:00", "%H:%M").time(),
            )
        with col2:
            wake_time = st.time_input(
                "Wake-up time",
                value=datetime.strptime("07:00", "%H:%M").time(),
            )

        quality = st.slider(
            "Sleep quality (1 = very poor, 5 = excellent)",
            min_value=1, max_value=5, value=3,
        )

        mood = st.select_slider(
            "How is your mood today?",
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: {1: "1 - Very Bad", 2: "2 - Bad", 3: "3 - Okay", 4: "4 - Good", 5: "5 - Great"}[x],
            value=3,
        )

        st.markdown("**Daily Habits**")
        took_coffee = st.checkbox("Did you drink coffee/caffeine today?")
        exercised = st.checkbox("Did you exercise today?")
        used_screen = st.checkbox("Did you use screens within 1 hour of bed?")

        notes = st.text_area(
            "Notes (optional)",
            placeholder="e.g., Had coffee late, used phone in bed...",
        )

        submitted = st.form_submit_button("Log Sleep")

    if submitted:
        date_str = log_date.strftime("%Y-%m-%d")
        if date_exists(date_str):
            st.error("A record for this date already exists.")
            return

        bedtime_str = bedtime.strftime("%H:%M")
        wake_str = wake_time.strftime("%H:%M")

        if bedtime_str == wake_str:
            st.error("Bedtime and wake-up time cannot be the same.")
            return

        duration = calculate_duration(bedtime_str, wake_str)

        record = SleepRecord(
            date=date_str,
            bedtime=bedtime_str,
            wake_time=wake_str,
            duration_hours=duration,
            quality_rating=quality,
            notes=notes if notes else None,
            mood=mood,
        )

        try:
            record_id = add_sleep_record(record)
            # Insert linked habit record
            habit = HabitRecord(
                sleep_record_id=record_id,
                took_coffee=took_coffee,
                exercised=exercised,
                used_screen=used_screen,
            )
            insert_habit(habit)
            st.success(f"Sleep logged! Duration: {duration} hours")
        except Exception as e:
            st.error(f"Error saving record: {e}")


# ============================================================================
# Page: Dashboard
# ============================================================================

def _page_dashboard():
    st.header("Dashboard")

    all_records = get_all_records()
    if not all_records:
        st.info("No sleep records yet. Start by logging your first check-in!")
        return

    recent = get_recent_records(7)
    target = _get_target_hours()
    streak = get_streak(all_records)
    week_debt = calculate_sleep_debt(recent, target)
    avg_dur = sum(r.duration_hours for r in recent) / len(recent)
    qualities = [r.quality_rating for r in recent if r.quality_rating]
    avg_qual = sum(qualities) / len(qualities) if qualities else 0
    moods = [r.mood for r in recent if r.mood]
    avg_mood = sum(moods) / len(moods) if moods else 0

    # Key metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Streak", f"{streak} day{'s' if streak != 1 else ''}")
    col2.metric("Sleep Debt (7d)", f"{week_debt:+.1f} hrs")
    col3.metric("Avg Duration (7d)", f"{avg_dur:.1f} hrs")
    col4.metric("Avg Quality (7d)", f"{avg_qual:.1f} / 5")
    col5.metric("Avg Mood (7d)", f"{avg_mood:.1f} / 5")

    # Streak reward messages with emoji
    if streak >= 30:
        st.success("🔥 30-day streak! You're a sleep champion! 🏆")
    elif streak >= 14:
        st.success("🔥 2-week streak! Incredible consistency!")
    elif streak >= 7:
        st.success("🔥 7-day streak! Great week of tracking!")
    elif streak >= 3:
        st.info("🔥 3-day streak! Keep it going!")

    # Sleep debt indicator
    st.subheader("Sleep Debt Indicator")
    max_debt = target * 7
    debt_ratio = max(0.0, min(1.0, 1 - abs(week_debt) / max_debt))
    if week_debt > 0:
        st.progress(debt_ratio, text=f"Under-slept by {week_debt} hrs this week")
    else:
        st.progress(1.0, text="No sleep debt - well done!")

    # Trend line chart (last 14-30 days)
    st.subheader("Sleep Duration Trend")
    trend_records = get_recent_records(30)
    if trend_records:
        chart_data = {}
        for r in reversed(trend_records):
            chart_data[r.date] = r.duration_hours
        st.line_chart(chart_data)

    # Check-in heatmap (calendar view)
    st.subheader("Check-in Calendar (Last 28 Days)")
    today = date.today()
    logged_dates = {r.date for r in all_records}

    # Show 4 rows of 7 days
    for week in range(4):
        cols = st.columns(7)
        for day_idx in range(7):
            offset = (3 - week) * 7 + (6 - day_idx)
            d = today - timedelta(days=offset)
            d_str = d.strftime("%Y-%m-%d")
            label = d.strftime("%d")
            with cols[day_idx]:
                if d_str in logged_dates:
                    st.markdown(f"<div style='text-align:center;background:#4CAF50;color:white;border-radius:4px;padding:4px;margin:1px;font-size:12px'>{label}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='text-align:center;background:#eee;border-radius:4px;padding:4px;margin:1px;font-size:12px;color:#999'>{label}</div>", unsafe_allow_html=True)

    # Recent logs
    st.subheader("Recent Sleep Logs")
    table_data = []
    for r in recent:
        table_data.append({
            "Date": r.date,
            "Bedtime": r.bedtime,
            "Wake": r.wake_time,
            "Duration": f"{r.duration_hours:.1f} hrs",
            "Quality": f"{r.quality_rating}/5" if r.quality_rating else "-",
            "Mood": f"{r.mood}/5" if r.mood else "-",
        })
    st.table(table_data)


# ============================================================================
# Page: Weekly Report
# ============================================================================

def _page_report():
    st.header("Weekly Report")

    records = get_recent_records(7)
    if len(records) < 2:
        st.info("Need at least 2 days of data to generate a report.")
        return

    all_records = get_all_records()
    all_habits = get_all_habits()

    summary = generate_weekly_summary(records, all_habits)
    if not summary:
        st.warning("Could not generate summary.")
        return

    # Summary metrics
    st.subheader("Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Logs", len(records))
        st.metric("Best Night", f"{summary['best_day']['duration']:.1f} hrs ({summary['best_day']['date']})")
    with col2:
        st.metric("Avg Sleep", f"{summary['avg_duration']:.1f} hrs")
        st.metric("Avg Quality", f"{summary['avg_quality']:.1f} / 5")
    with col3:
        st.metric("Avg Mood", f"{summary['avg_mood']:.1f} / 5")
        st.metric("Sleep Debt", f"{summary['total_debt']:+.1f} hrs")

    # Duration bar chart
    st.subheader("Sleep Duration (Last 7 Days)")
    dur_chart = {r.date: r.duration_hours for r in reversed(records)}
    st.bar_chart(dur_chart)

    # Quality trend chart
    st.subheader("Sleep Quality Trend")
    qual_chart = {}
    for r in reversed(records):
        if r.quality_rating:
            qual_chart[r.date] = r.quality_rating
    if qual_chart:
        st.line_chart(qual_chart)

    # Habit correlation insights
    correlations = summary.get("habit_correlations", {})
    if correlations:
        st.subheader("Habit Insights")
        for habit_name, data in correlations.items():
            if data["sample_with"] > 0 and data["sample_without"] > 0:
                label = {"coffee": "Coffee/Caffeine", "exercise": "Exercise", "screen": "Screen before bed"}[habit_name]
                q_diff = data["quality_diff"]
                direction = "higher" if q_diff > 0 else "lower"
                if abs(q_diff) > 0.1:
                    st.write(f"**{label}**: Associated with {abs(q_diff):.1f} {direction} quality rating "
                             f"({data['sample_with']} days with, {data['sample_without']} days without)")

    # Tailored advice
    advice_list = summary.get("advice_list", [])
    if advice_list:
        st.subheader("Personalized Advice")
        for advice in advice_list:
            st.info(advice)

    # Sleep debt assessment
    debt = summary["total_debt"]
    st.subheader("Sleep Debt")
    if debt > 0:
        st.warning(f"You have a sleep debt of {debt} hours this week. Try to get more rest!")
    elif debt < 0:
        st.success(f"Great! You slept {abs(debt)} hours more than your target this week.")
    else:
        st.success("Perfect! You met your sleep target exactly.")

    # Save report button
    st.divider()
    if st.button("Save this report"):
        today_str = date.today().strftime("%Y-%m-%d")
        dates = sorted([r.date for r in records])
        report = ReportRecord(
            report_date=today_str,
            week_start=dates[0],
            week_end=dates[-1],
            sleep_debt=debt,
            average_mood=summary["avg_mood"],
            average_sleep_time=summary["avg_duration"],
            average_quality=summary["avg_quality"],
            insights="; ".join(advice_list) if advice_list else None,
        )
        try:
            insert_report(report)
            st.success("Report saved!")
        except Exception as e:
            st.error(f"Error saving report: {e}")

    # Show saved reports
    saved_reports = get_all_reports()
    if saved_reports:
        st.subheader("Saved Reports")
        for rpt in saved_reports[:5]:
            st.write(f"**{rpt.report_date}** (Week {rpt.week_start} to {rpt.week_end}) — "
                     f"Debt: {rpt.sleep_debt:+.1f}h, Avg Sleep: {rpt.average_sleep_time:.1f}h, "
                     f"Avg Quality: {rpt.average_quality:.1f}")


# ============================================================================
# Page: Settings
# ============================================================================

def _page_settings():
    st.header("Settings")

    settings = _load_settings()

    # Target sleep hours
    target = settings.get("target_hours", 8.0)
    new_target = st.number_input(
        "Target sleep hours per night",
        min_value=4.0, max_value=12.0, value=float(target), step=0.5,
    )

    # Auto-launch toggle
    auto_launch = settings.get("auto_launch", False)
    new_auto_launch = st.checkbox("Enable auto-launch on startup", value=auto_launch)

    if st.button("Save Settings", type="primary"):
        settings["target_hours"] = new_target
        settings["auto_launch"] = new_auto_launch
        _save_settings(settings)

        # Handle auto-launch changes
        if new_auto_launch != auto_launch:
            from system_yibo import enable_auto_launch, disable_auto_launch
            if new_auto_launch:
                msg = enable_auto_launch()
            else:
                msg = disable_auto_launch()
            st.info(msg)

        st.success("Settings saved!")

    st.divider()
    st.subheader("Data Management")
    st.warning("Deleting your data cannot be undone.")
    if st.button("Delete all my data"):
        from database_hakim.connection import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM habits")
        cursor.execute("DELETE FROM reports")
        cursor.execute("DELETE FROM sleep_records")
        conn.commit()
        conn.close()
        settings["consent_given"] = False
        _save_settings(settings)
        st.success("All data deleted. The app will reset on next load.")
        st.rerun()


# ============================================================================
# Main render function
# ============================================================================

def render():
    """Entry point - call this from app.py to render the full UI."""
    init_database()

    # Check consent
    settings = _load_settings()
    if not settings.get("consent_given", False) and get_record_count() == 0:
        _page_consent()
        return

    page = st.sidebar.radio(
        "Navigation",
        ["Daily Check-in", "Dashboard", "Weekly Report", "Settings"],
    )

    if page == "Daily Check-in":
        _page_checkin()
    elif page == "Dashboard":
        _page_dashboard()
    elif page == "Weekly Report":
        _page_report()
    elif page == "Settings":
        _page_settings()
