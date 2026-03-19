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
import csv
import io
import pandas as pd
from datetime import datetime, date, timedelta
from pathlib import Path

from database_hakim import (
    init_database,
    add_sleep_record,
    get_all_records,
    get_recent_records,
    get_record_count,
    date_exists,
    insert_habit,
    update_habit,
    get_habit_by_sleep_record_id,
    get_all_habits,
    insert_report,
    get_all_reports,
    delete_report,
    delete_sleep_record,
    update_sleep_record,
    SleepRecord,
    HabitRecord,
    ReportRecord,
)

from analysis_yeraly import (
    calculate_duration,
    calculate_sleep_debt,
    get_streak,
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
    settings = _load_settings()
    allow_past_day_logging = settings.get("allow_past_day_logging", False)

    if date_exists(today.strftime("%Y-%m-%d")) and not allow_past_day_logging:
        st.success("You've already logged your sleep for today!")
        st.info("Come back tomorrow for your next check-in.")
        return

    if allow_past_day_logging:
        st.info("Past-day logging is enabled in Settings.")

    with st.form("checkin_form"):
        if allow_past_day_logging:
            log_date = st.date_input("Date", value=today, max_value=today)
        else:
            log_date = st.date_input("Date", value=today, min_value=today, max_value=today)

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
            "Notes": r.notes if r.notes else "-",
            "ID": r.id,
        })
    
    df_logs = pd.DataFrame(table_data)
    st.table(df_logs)
    
    st.divider()
    st.write("**Actions:**")
    
    # Action buttons for each log
    col1, col2 = st.columns(2)
    with col1:
        selected_action = st.radio("Select action:", ["Edit", "Delete"], key="sleep_log_action")
        selected_log_idx = st.selectbox("Select log:", 
                                        range(len(recent)), 
                                        format_func=lambda i: f"{recent[i].date} ({recent[i].duration_hours:.1f}h)",
                                        key="sleep_log_select")
    
    selected_log = recent[selected_log_idx]
    
    # Clear delete confirmation state when switching to Edit action
    if selected_action == "Edit":
        st.session_state[f"confirm_delete_log_{selected_log.id}"] = False
    
    # Clear edit form when switching to Delete action
    if selected_action == "Delete":
        st.session_state[f"edit_log_{selected_log.id}"] = False
    
    with col2:
        st.write("")
        st.write("")
        
        if selected_action == "Edit":
            if st.button("✏️ Edit Log", key=f"edit_action_{selected_log.id}"):
                st.session_state[f"edit_log_{selected_log.id}"] = True
        else:  # Delete action
            if st.button("🗑️ Delete Log", key=f"delete_log_action_{selected_log.id}"):
                st.session_state[f"confirm_delete_log_{selected_log.id}"] = True
    
    # Show edit form if pending
    if st.session_state.get(f"edit_log_{selected_log.id}", False):
        st.divider()
        st.subheader("Edit Sleep Log")
        
        # Load existing habit data for this sleep record
        existing_habit = get_habit_by_sleep_record_id(selected_log.id)
        
        with st.form(f"edit_form_{selected_log.id}"):
            col_edit1, col_edit2 = st.columns(2)
            with col_edit1:
                edit_date = st.date_input("Date", value=datetime.strptime(selected_log.date, "%Y-%m-%d").date(), key=f"edit_date_{selected_log.id}")
                edit_bedtime = st.time_input("Bedtime", value=datetime.strptime(selected_log.bedtime, "%H:%M").time(), key=f"edit_bedtime_{selected_log.id}")
                edit_wake_time = st.time_input("Wake Time", value=datetime.strptime(selected_log.wake_time, "%H:%M").time(), key=f"edit_wake_{selected_log.id}")
            
            with col_edit2:
                edit_quality = st.slider("Quality", 1, 5, value=selected_log.quality_rating if selected_log.quality_rating else 3, key=f"edit_quality_{selected_log.id}")
                edit_mood = st.slider("Mood", 1, 5, value=selected_log.mood if selected_log.mood else 3, key=f"edit_mood_{selected_log.id}")
                edit_notes = st.text_area("Notes", value=selected_log.notes if selected_log.notes else "", key=f"edit_notes_{selected_log.id}")
            
            st.markdown("**Daily Habits**")
            edit_coffee = st.checkbox("Did you drink coffee/caffeine today?", value=existing_habit.took_coffee if existing_habit else False, key=f"edit_coffee_{selected_log.id}")
            edit_exercise = st.checkbox("Did you exercise today?", value=existing_habit.exercised if existing_habit else False, key=f"edit_exercise_{selected_log.id}")
            edit_screen = st.checkbox("Did you use screens within 1 hour of bed?", value=existing_habit.used_screen if existing_habit else False, key=f"edit_screen_{selected_log.id}")
            
            col_form_btn1, col_form_btn2 = st.columns(2)
            with col_form_btn1:
                submit_edit = st.form_submit_button("✓ Save Changes")
            with col_form_btn2:
                cancel_edit = st.form_submit_button("✗ Cancel")
            
            if submit_edit:
                try:
                    bedtime_str = edit_bedtime.strftime("%H:%M")
                    wake_time_str = edit_wake_time.strftime("%H:%M")
                    duration = calculate_duration(bedtime_str, wake_time_str)
                    
                    updated_record = SleepRecord(
                        id=selected_log.id,
                        date=edit_date.strftime("%Y-%m-%d"),
                        bedtime=bedtime_str,
                        wake_time=wake_time_str,
                        duration_hours=duration,
                        quality_rating=edit_quality,
                        notes=edit_notes,
                        mood=edit_mood
                    )
                    
                    if update_sleep_record(updated_record):
                        # Update linked habit record
                        updated_habit = HabitRecord(
                            sleep_record_id=selected_log.id,
                            took_coffee=edit_coffee,
                            exercised=edit_exercise,
                            used_screen=edit_screen,
                        )
                        update_habit(selected_log.id, updated_habit)
                        st.session_state[f"edit_log_{selected_log.id}"] = False
                        st.success("Log updated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update log.")
                except Exception as e:
                    st.error(f"Error updating log: {e}")
            
            if cancel_edit:
                st.session_state[f"edit_log_{selected_log.id}"] = False
                st.rerun()
    
    # Show delete confirmation if pending
    if st.session_state.get(f"confirm_delete_log_{selected_log.id}", False):
        st.warning(f"⚠️ Are you sure you want to delete the log for {selected_log.date}?")
        col_confirm1, col_confirm2 = st.columns(2)
        with col_confirm1:
            if st.button("✓ Confirm Delete", key=f"confirm_yes_log_{selected_log.id}"):
                try:
                    delete_sleep_record(selected_log.id)
                    # Clean up all stale session state keys for sleep logs
                    stale_keys = [k for k in st.session_state if k.startswith("confirm_delete_log_") or k.startswith("edit_log_")]
                    for k in stale_keys:
                        del st.session_state[k]
                    st.success("Log deleted successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error deleting log: {e}")
        with col_confirm2:
            if st.button("✗ Cancel", key=f"confirm_no_log_{selected_log.id}"):
                st.session_state[f"confirm_delete_log_{selected_log.id}"] = False
                st.rerun()


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
        
        # Create table data
        table_data = []
        for rpt in saved_reports[:5]:
            table_data.append({
                "Report Date": rpt.report_date,
                "Week Start": rpt.week_start,
                "Week End": rpt.week_end,
                "Sleep Debt (h)": f"{rpt.sleep_debt:+.1f}",
                "Avg Sleep (h)": f"{rpt.average_sleep_time:.1f}",
                "Avg Quality": f"{rpt.average_quality:.1f}",
                "Avg Mood": f"{rpt.average_mood:.1f}" if rpt.average_mood else "-",
                "ID": rpt.id,
            })
        
        df = pd.DataFrame(table_data)
        st.table(df)
        
        st.divider()
        st.write("**Actions:**")
        
        # Action buttons for each report
        col1, col2 = st.columns(2)
        with col1:
            selected_action = st.radio("Select action:", ["Export", "Delete"], key="report_action")
            selected_report_idx = st.selectbox("Select report:", 
                                               range(len(saved_reports[:5])), 
                                               format_func=lambda i: f"ID {saved_reports[i].id} - {saved_reports[i].report_date} (Week {saved_reports[i].week_start} to {saved_reports[i].week_end})",
                                               key="report_select")
        
        selected_report = saved_reports[selected_report_idx]
        
        # Clear delete confirmation state when switching to Export action
        if selected_action == "Export":
            st.session_state[f"confirm_delete_{selected_report.id}"] = False
        
        with col2:
            st.write("")
            st.write("")
            
            if selected_action == "Export":
                if st.button("📥 Export to CSV", key=f"export_action_{selected_report.id}"):
                    # Export CSV to download
                    csv_buffer = io.StringIO()
                    writer = csv.writer(csv_buffer)
                    writer.writerow(["Field", "Value"])
                    writer.writerow(["Report Date", selected_report.report_date])
                    writer.writerow(["Week Start", selected_report.week_start])
                    writer.writerow(["Week End", selected_report.week_end])
                    writer.writerow(["Sleep Debt (hrs)", selected_report.sleep_debt])
                    writer.writerow(["Average Mood", selected_report.average_mood])
                    writer.writerow(["Average Sleep Time (hrs)", selected_report.average_sleep_time])
                    writer.writerow(["Average Quality", selected_report.average_quality])
                    writer.writerow(["Insights", selected_report.insights if selected_report.insights else ""])
                    
                    csv_content = csv_buffer.getvalue()
                    st.download_button(
                        label="⬇️ Download",
                        data=csv_content,
                        file_name=f"report_{selected_report.report_date}.csv",
                        mime="text/csv",
                        key=f"download_{selected_report.id}"
                    )
            
            else:  # Delete action
                if st.button("🗑️ Delete Report", key=f"delete_action_{selected_report.id}"):
                    st.session_state[f"confirm_delete_{selected_report.id}"] = True
        
        # Show confirmation message if pending
        if st.session_state.get(f"confirm_delete_{selected_report.id}", False):
            st.warning(f"⚠️ Are you sure you want to delete the report for {selected_report.report_date}?")
            col_confirm1, col_confirm2 = st.columns(2)
            with col_confirm1:
                if st.button("✓ Confirm Delete", key=f"confirm_yes_{selected_report.id}"):
                    try:
                        delete_report(selected_report.id)
                        # Clean up all stale session state keys for reports
                        stale_keys = [k for k in st.session_state if k.startswith("confirm_delete_")]
                        for k in stale_keys:
                            del st.session_state[k]
                        st.success("Report deleted successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting report: {e}")
            with col_confirm2:
                if st.button("✗ Cancel", key=f"confirm_no_{selected_report.id}"):
                    st.session_state[f"confirm_delete_{selected_report.id}"] = False
                    st.rerun()


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

    # Past-day logging toggle
    allow_past_day_logging = settings.get("allow_past_day_logging", False)
    new_allow_past_day_logging = st.toggle(
        "Allow logging sleep for past days",
        value=allow_past_day_logging,
    )

    if st.button("Save Settings", type="primary"):
        settings["target_hours"] = new_target
        settings["auto_launch"] = new_auto_launch
        settings["allow_past_day_logging"] = new_allow_past_day_logging
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
