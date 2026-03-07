"""
Frontend Pages - Siyuan
=======================
Streamlit UI for the Sleep Tracker.

Usage:
    from frontend_siyuan.pages import render
    render()
"""

import streamlit as st
from datetime import datetime, date, timedelta

from database_hakim import (
    init_database,
    add_sleep_record,
    get_all_records,
    get_recent_records,
    get_record_by_date,
    date_exists,
    SleepRecord,
)


# ============================================================================
# Temporary helpers (replace with analysis_yeraly when ready)
# ============================================================================

def _calculate_duration(bedtime_str, wake_time_str):
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


def _calculate_sleep_debt(records, target_hours=8.0):
    """Cumulative sleep debt (positive = under-slept)."""
    return round(sum(target_hours - r.duration_hours for r in records), 1)


def _get_streak(records):
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
        duration = _calculate_duration(bedtime_str, wake_str)

        record = SleepRecord(
            date=date_str,
            bedtime=bedtime_str,
            wake_time=wake_str,
            duration_hours=duration,
            quality_rating=quality,
            notes=notes if notes else None,
        )

        try:
            add_sleep_record(record)
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
    streak = _get_streak(all_records)
    week_debt = _calculate_sleep_debt(recent)
    avg_dur = sum(r.duration_hours for r in recent) / len(recent)
    qualities = [r.quality_rating for r in recent if r.quality_rating]
    avg_qual = sum(qualities) / len(qualities) if qualities else 0

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Streak", f"{streak} day{'s' if streak != 1 else ''}")
    col2.metric("Sleep Debt (7d)", f"{week_debt:+.1f} hrs")
    col3.metric("Avg Duration (7d)", f"{avg_dur:.1f} hrs")
    col4.metric("Avg Quality (7d)", f"{avg_qual:.1f} / 5")

    # Streak reward messages
    if streak >= 30:
        st.success("30-day streak! You're a sleep champion!")
    elif streak >= 14:
        st.success("2-week streak! Incredible consistency!")
    elif streak >= 7:
        st.success("7-day streak! Great week of tracking!")
    elif streak >= 3:
        st.info("3-day streak! Keep it going!")

    # Sleep debt indicator
    st.subheader("Sleep Debt Indicator")
    max_debt = 8.0 * 7
    debt_ratio = max(0.0, min(1.0, 1 - abs(week_debt) / max_debt))
    if week_debt > 0:
        st.progress(debt_ratio, text=f"Under-slept by {week_debt} hrs this week")
    else:
        st.progress(1.0, text="No sleep debt - well done!")

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
    durations = [r.duration_hours for r in records]
    qualities = [r.quality_rating for r in records if r.quality_rating]

    st.subheader("Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Logs", len(records))
        st.metric("Best Night", f"{max(durations):.1f} hrs")
        st.metric("Worst Night", f"{min(durations):.1f} hrs")
    with col2:
        st.metric("Average Sleep", f"{sum(durations) / len(durations):.1f} hrs")
        if qualities:
            st.metric("Average Quality", f"{sum(qualities) / len(qualities):.1f} / 5")
        st.metric("Current Streak", f"{_get_streak(all_records)} days")

    # Duration bar chart
    st.subheader("Sleep Duration (Last 7 Days)")
    chart_data = {r.date: r.duration_hours for r in reversed(records)}
    st.bar_chart(chart_data)

    # Sleep debt assessment
    debt = _calculate_sleep_debt(records)
    st.subheader("Sleep Debt")
    if debt > 0:
        st.warning(f"You have a sleep debt of {debt} hours this week. Try to get more rest!")
    elif debt < 0:
        st.success(f"Great! You slept {abs(debt)} hours more than your target this week.")
    else:
        st.success("Perfect! You met your sleep target exactly.")


# ============================================================================
# Main render function
# ============================================================================

def render():
    """Entry point - call this from app.py to render the full UI."""
    init_database()

    page = st.sidebar.radio(
        "Navigation",
        ["Daily Check-in", "Dashboard", "Weekly Report"],
    )

    if page == "Daily Check-in":
        _page_checkin()
    elif page == "Dashboard":
        _page_dashboard()
    elif page == "Weekly Report":
        _page_report()
