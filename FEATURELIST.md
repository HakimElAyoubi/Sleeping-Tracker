# Sleep Tracker — Feature List

Complete list of all implemented features with their corresponding functions and files.

---

## 1. User Consent Screen

Shown on first launch when no records exist and no consent flag is stored in `settings.json`.

| What | Where |
|---|---|
| Page render | `_page_consent()` — `frontend_siyuan/pages.py` |
| Consent flag write | `_save_settings(settings)` — `frontend_siyuan/pages.py` |
| Consent flag read | `_load_settings()` — `frontend_siyuan/pages.py` |
| Gate check | `render()` — `frontend_siyuan/pages.py` (checks `consent_given` and `get_record_count() == 0`) |
| Record count query | `get_record_count()` — `database_hakim/queries.py` |

---

## 2. Daily Sleep Check-in

Allows the user to log one sleep entry per day (or past days when the setting is enabled).

| What | Where |
|---|---|
| Page render | `_page_checkin()` — `frontend_siyuan/pages.py` |
| Duplicate date guard | `date_exists(date_str)` — `database_hakim/queries.py` |
| Sleep duration calculation | `calculate_duration(bedtime_str, wake_str)` — `analysis_yeraly/algorithms.py` |
| Save sleep record | `add_sleep_record(record)` — `database_hakim/queries.py` |
| Save linked habit record | `insert_habit(habit)` — `database_hakim/queries.py` |
| Data model — sleep | `SleepRecord` dataclass — `database_hakim/models.py` |
| Data model — habit | `HabitRecord` dataclass — `database_hakim/models.py` |

**Fields collected per entry:** date, bedtime, wake time, sleep quality (1–5), mood (1–5), notes, coffee/caffeine taken, exercised, screen use within 1 hour of bed.

---

## 3. Past-Day Logging Switch

A toggle in Settings that unlocks the date picker in the check-in form to allow backfilling missed days.

| What | Where |
|---|---|
| Toggle UI | `_page_settings()` — `frontend_siyuan/pages.py` (`st.toggle` — "Allow logging sleep for past days") |
| Setting persist | `_save_settings(settings)` — `frontend_siyuan/pages.py` (key: `allow_past_day_logging` in `settings.json`) |
| Setting read | `_load_settings()` — `frontend_siyuan/pages.py` |
| Enforce in check-in | `_page_checkin()` — `frontend_siyuan/pages.py` (unlocks `st.date_input` min_value and bypasses today-already-logged guard) |

---

## 4. Dashboard

Overview page showing key metrics, charts, a calendar heatmap, and the recent sleep log table.

### 4a. Key Metrics Bar

Five metrics displayed side by side at the top of the dashboard.

| Metric | Function | File |
|---|---|---|
| Streak (consecutive days) | `get_streak(all_records)` | `analysis_yeraly/algorithms.py` |
| Sleep Debt (7-day) | `calculate_sleep_debt(recent, target)` | `analysis_yeraly/algorithms.py` |
| Avg Duration (7-day) | Computed inline from `get_recent_records(7)` | `database_hakim/queries.py` |
| Avg Quality (7-day) | Computed inline from `get_recent_records(7)` | `database_hakim/queries.py` |
| Avg Mood (7-day) | Computed inline from `get_recent_records(7)` | `database_hakim/queries.py` |
| Target hours (for debt) | `_get_target_hours()` → `_load_settings()` | `frontend_siyuan/pages.py` |

### 4b. Streak Milestone Messages

Shown below the metrics bar when the streak reaches a threshold.

| Threshold | Message | Code location |
|---|---|---|
| ≥ 3 days | "🔥 3-day streak! Keep it going!" | `_page_dashboard()` — `frontend_siyuan/pages.py` |
| ≥ 7 days | "🔥 7-day streak! Great week of tracking!" | `_page_dashboard()` — `frontend_siyuan/pages.py` |
| ≥ 14 days | "🔥 2-week streak! Incredible consistency!" | `_page_dashboard()` — `frontend_siyuan/pages.py` |
| ≥ 30 days | "🔥 30-day streak! You're a sleep champion! 🏆" | `_page_dashboard()` — `frontend_siyuan/pages.py` |

Streak logic: `get_streak(records)` — `analysis_yeraly/algorithms.py` — counts consecutive days ending at today.

### 4c. Sleep Debt Progress Indicator

`st.progress` bar visualising remaining "sleep budget" for the 7-day window.

| What | Where |
|---|---|
| Debt value | `calculate_sleep_debt(recent, target)` — `analysis_yeraly/algorithms.py` |
| Progress render | `st.progress(debt_ratio, text=...)` — `_page_dashboard()`, `frontend_siyuan/pages.py` |

### 4d. 30-Day Sleep Duration Trend Chart

Line chart of daily sleep hours over the last 30 days.

| What | Where |
|---|---|
| Data fetch | `get_recent_records(30)` — `database_hakim/queries.py` |
| Chart render | `st.line_chart(chart_data)` — `_page_dashboard()`, `frontend_siyuan/pages.py` |

### 4e. 28-Day Check-in Calendar Heatmap

4-week grid where logged days appear green and missed days appear grey.

| What | Where |
|---|---|
| All records fetch | `get_all_records()` — `database_hakim/queries.py` |
| Grid render | `st.markdown(...)` with inline HTML/CSS — `_page_dashboard()`, `frontend_siyuan/pages.py` |

### 4f. Recent Sleep Logs Table

Pandas DataFrame table showing the 7 most recent logs (Date, Bedtime, Wake, Duration, Quality, Mood, ID).

| What | Where |
|---|---|
| Data fetch | `get_recent_records(7)` — `database_hakim/queries.py` |
| Table render | `pd.DataFrame(table_data)` + `st.table(df_logs)` — `_page_dashboard()`, `frontend_siyuan/pages.py` |

---

## 5. Edit Sleep Log

Inline edit form that appears below the logs table when "Edit" is selected.

| What | Where |
|---|---|
| Action selector | `st.radio(["Edit", "Delete"])` + `st.selectbox(...)` — `_page_dashboard()`, `frontend_siyuan/pages.py` |
| Edit form render | `st.form(f"edit_form_{id}")` inside `_page_dashboard()` — `frontend_siyuan/pages.py` |
| Duration recalculation | `calculate_duration(bedtime_str, wake_time_str)` — `analysis_yeraly/algorithms.py` |
| Save changes | `update_sleep_record(updated_record)` — `database_hakim/queries.py` |
| Data model | `SleepRecord` dataclass — `database_hakim/models.py` |

Edit form fields: date, bedtime, wake time, quality (1–5), mood (1–5), notes.

---

## 6. Delete Sleep Log

Removes a sleep log entry after user confirmation.

| What | Where |
|---|---|
| Delete button | `st.button("🗑️ Delete Log")` — `_page_dashboard()`, `frontend_siyuan/pages.py` |
| Confirmation warning | `st.warning(...)` + two buttons (Confirm / Cancel) — `_page_dashboard()`, `frontend_siyuan/pages.py` |
| Database delete | `delete_sleep_record(record_id)` — `database_hakim/queries.py` |
| State management | `st.session_state[f"confirm_delete_log_{id}"]` — `frontend_siyuan/pages.py` |

---

## 7. Weekly Report

Analysis page covering the last 7 days of sleep with charts, habit insights, personalised advice, and a save button.

### 7a. Summary Metrics

Six metrics: Total Logs, Best Night, Avg Sleep, Avg Quality, Avg Mood, Sleep Debt.

| What | Where |
|---|---|
| Full summary computation | `generate_weekly_summary(records, all_habits)` — `analysis_yeraly/algorithms.py` |
| Records fetch | `get_recent_records(7)` — `database_hakim/queries.py` |
| Habits fetch | `get_all_habits()` — `database_hakim/queries.py` |

### 7b. Sleep Duration Bar Chart

`st.bar_chart` of daily sleep hours for the last 7 days — rendered inside `_page_report()`, `frontend_siyuan/pages.py`.

### 7c. Sleep Quality Trend Line Chart

`st.line_chart` of daily quality ratings for the last 7 days — rendered inside `_page_report()`, `frontend_siyuan/pages.py`.

### 7d. Habit Correlation Insights

Shows which habits (coffee, exercise, screen use) are associated with higher or lower sleep quality.

| What | Where |
|---|---|
| Correlation data | `summary["habit_correlations"]` produced by `generate_weekly_summary()` → `analyze_habit_correlations()` — `analysis_yeraly/algorithms.py` |
| UI render | `_page_report()` — `frontend_siyuan/pages.py` |

### 7e. Personalised Advice

Text advice cards tailored to the user's sleep debt, habit correlations, quality, and streak.

| What | Where |
|---|---|
| Advice generation | `summary["advice_list"]` produced by `generate_weekly_summary()` → `generate_advice()` — `analysis_yeraly/algorithms.py` |
| UI render | `st.info(advice)` loop — `_page_report()`, `frontend_siyuan/pages.py` |

### 7f. Sleep Debt Assessment

Summary message indicating whether the user has under-slept, over-slept, or hit their target.

Rendered in `_page_report()` using `summary["total_debt"]` from `generate_weekly_summary()`.

### 7g. Save Report

Saves a snapshot of the current weekly report to the database.

| What | Where |
|---|---|
| Save button | `st.button("Save this report")` — `_page_report()`, `frontend_siyuan/pages.py` |
| Database insert | `insert_report(report)` — `database_hakim/queries.py` |
| Data model | `ReportRecord` dataclass — `database_hakim/models.py` |

---

## 8. Saved Reports Table

Displays up to 5 saved reports in a pandas DataFrame table (Report Date, Week Start, Week End, Sleep Debt, Avg Sleep, Avg Quality, Avg Mood, ID).

| What | Where |
|---|---|
| Data fetch | `get_all_reports()` — `database_hakim/queries.py` |
| Table render | `pd.DataFrame(table_data)` + `st.table(df)` — `_page_report()`, `frontend_siyuan/pages.py` |

---

## 9. Export Report to CSV

Downloads a selected saved report as a `.csv` file.

| What | Where |
|---|---|
| Action selector | `st.radio(["Export", "Delete"])` + `st.selectbox(...)` — `_page_report()`, `frontend_siyuan/pages.py` |
| CSV generation | `csv.writer` writing to `io.StringIO()` — `_page_report()`, `frontend_siyuan/pages.py` |
| Download trigger | `st.download_button(...)` — `_page_report()`, `frontend_siyuan/pages.py` |

CSV fields: Report Date, Week Start, Week End, Sleep Debt (hrs), Average Mood, Average Sleep Time (hrs), Average Quality, Insights.

---

## 10. Delete Saved Report

Removes a selected saved report after user confirmation.

| What | Where |
|---|---|
| Delete button | `st.button("🗑️ Delete Report")` — `_page_report()`, `frontend_siyuan/pages.py` |
| Confirmation warning | `st.warning(...)` + Confirm / Cancel buttons — `_page_report()`, `frontend_siyuan/pages.py` |
| Database delete | `delete_report(report_id)` — `database_hakim/queries.py` |
| State management | `st.session_state[f"confirm_delete_{id}"]` — `frontend_siyuan/pages.py` |

---

## 11. Settings

Persistent user preferences stored in `settings.json`.

| Setting | UI element | Key in settings.json | Where used |
|---|---|---|---|
| Target sleep hours (4–12 h, default 8) | `st.number_input` | `target_hours` | `_get_target_hours()` → `calculate_sleep_debt()` |
| Auto-launch on startup | `st.checkbox` | `auto_launch` | `enable_auto_launch()` / `disable_auto_launch()` — `system_yibo/integration.py` |
| Allow past-day logging | `st.toggle` | `allow_past_day_logging` | `_page_checkin()` date picker and today-logged guard |

All settings written by `_save_settings(settings)` and read by `_load_settings()` — `frontend_siyuan/pages.py`.

---

## 12. Delete All Data

Nuclear reset that wipes all records, habits, and reports from the database and resets consent.

| What | Where |
|---|---|
| Button | `st.button("Delete all my data")` — `_page_settings()`, `frontend_siyuan/pages.py` |
| Database wipe | Raw SQL `DELETE FROM habits / reports / sleep_records` via `get_connection()` — `database_hakim/connection.py` |
| Consent reset | Sets `consent_given = False` via `_save_settings()` — `frontend_siyuan/pages.py` |

---

## 13. Auto-Launch on Startup

OS-level scripts to start the app automatically at login.

| Platform | Script | Logic |
|---|---|---|
| Windows | `system_yibo/auto_launch_windows.bat` | Copied to `shell:startup` folder by `enable_auto_launch()` |
| Mac / Linux | `system_yibo/auto_launch_mac.sh` | Instructions for crontab or Login Items shown by `enable_auto_launch()` |

Functions: `enable_auto_launch()`, `disable_auto_launch()`, `get_auto_launch_script_path()` — `system_yibo/integration.py`.

---

## Module Summary

| Module | Responsibility | Key functions |
|---|---|---|
| `app.py` | Entry point, page config | `render()` call |
| `frontend_siyuan/pages.py` | All Streamlit UI pages | `render()`, `_page_consent()`, `_page_checkin()`, `_page_dashboard()`, `_page_report()`, `_page_settings()` |
| `database_hakim/connection.py` | SQLite connection, schema init | `get_connection()`, `init_database()` |
| `database_hakim/models.py` | Data classes | `SleepRecord`, `HabitRecord`, `ReportRecord` |
| `database_hakim/queries.py` | All CRUD operations | `add_sleep_record`, `get_all_records`, `get_recent_records`, `update_sleep_record`, `delete_sleep_record`, `get_record_count`, `date_exists`, `get_record_by_date`, `insert_habit`, `get_all_habits`, `insert_report`, `get_all_reports`, `delete_report` |
| `analysis_yeraly/algorithms.py` | Sleep analysis | `calculate_duration`, `calculate_sleep_debt`, `get_streak`, `analyze_habit_correlations`, `generate_advice`, `generate_weekly_summary` |
| `system_yibo/integration.py` | OS auto-launch | `get_auto_launch_script_path`, `enable_auto_launch`, `disable_auto_launch` |
