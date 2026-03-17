# Sleep Tracker — Change Log
> All changes made by Siyuan on 2026-03-16 with team permission.
> This document explains every modification for team review.

## app.py
- **Fixed execution order bug**: Moved `st.set_page_config(page_title="Sleep Tracker", page_icon="😴", layout="wide")` to immediately after imports, before any other Streamlit call. Previously `render()` was called before `set_page_config()`, which caused a Streamlit error.
- **Removed duplicate UI elements**: Removed the standalone `st.title("Sleep Tracker")` and `st.write("Welcome to ...")` lines that appeared after `render()` — all page content is now handled inside `render()`.
- **Removed TODO comments**: Cleaned up the unused `# TODO: Import and integrate modules` block since integration is now complete.

## database_hakim/

### connection.py
- **Added `mood` column** to the `sleep_records` CREATE TABLE statement: `mood INTEGER CHECK(mood >= 1 AND mood <= 5)`.
- **Added ALTER TABLE migration**: Gracefully adds `mood` column to existing databases that were created before this change (uses try/except to ignore "column already exists" errors).
- **Created `habits` table**: New table with columns `id`, `sleep_record_id` (FK to sleep_records), `took_coffee`, `exercised`, `used_screen`. Tracks daily habits linked to each sleep entry.
- **Created `reports` table**: New table with columns `id`, `report_date`, `week_start`, `week_end`, `sleep_debt`, `average_mood`, `average_sleep_time`, `average_quality`, `insights`, `created_at`. Stores saved weekly report snapshots.

### models.py
- **Added `mood` field to `SleepRecord` dataclass**: New optional integer field (1-5 scale), defaulting to `None`. Updated `to_dict()`, `from_dict()`, and `from_row()` methods to include mood. `from_row()` handles backward compatibility with rows that don't have the mood column.
- **Created `HabitRecord` dataclass**: Fields: `id`, `sleep_record_id`, `took_coffee` (bool), `exercised` (bool), `used_screen` (bool). Includes `to_dict()` and `from_row()` methods.
- **Created `ReportRecord` dataclass**: Fields: `id`, `report_date`, `week_start`, `week_end`, `sleep_debt`, `average_mood`, `average_sleep_time`, `average_quality`, `insights`, `created_at`. Includes `to_dict()` and `from_row()` methods.

### queries.py
- **Updated `add_sleep_record()`**: INSERT query now includes the `mood` column.
- **Updated `update_sleep_record()`**: UPDATE query now includes the `mood` column.
- **Added `insert_habit(record)`**: Inserts a HabitRecord into the habits table. Returns new ID.
- **Added `get_habits_by_date_range(start, end)`**: Retrieves habit records by joining with sleep_records on date range.
- **Added `get_habit_by_sleep_record_id(record_id)`**: Gets the habit record linked to a specific sleep record.
- **Added `get_all_habits()`**: Returns all habit records.
- **Added `insert_report(record)`**: Inserts a ReportRecord into the reports table. Returns new ID.
- **Added `get_latest_report()`**: Returns the most recently created report.
- **Added `get_all_reports()`**: Returns all reports ordered by creation date descending.

### __init__.py
- **Updated exports**: Added `HabitRecord`, `ReportRecord` models and all new query functions (`insert_habit`, `get_habits_by_date_range`, `get_habit_by_sleep_record_id`, `get_all_habits`, `insert_report`, `get_latest_report`, `get_all_reports`) to module exports.
- **Updated docstring**: Added documentation for all new functions and models.

## analysis_yeraly/

### algorithms.py
- **Implemented `calculate_duration(bedtime_str, wake_time_str)`**: Calculates sleep duration in hours handling overnight sleep. Moved from temporary helper in `pages.py`.
- **Implemented `calculate_sleep_debt(records, target_hours=8.0)`**: Calculates cumulative sleep debt. Moved from temporary helper in `pages.py`.
- **Implemented `get_streak(records)`**: Counts consecutive check-in days ending at today. Moved from temporary helper in `pages.py`.
- **Implemented `analyze_habit_correlations(sleep_records, habits)`**: Compares average sleep quality and duration on days WITH each habit (coffee, exercise, screen) vs days WITHOUT. Returns a dict with quality_diff, duration_diff, and sample sizes for each habit.
- **Implemented `generate_advice(sleep_records, habits, sleep_debt)`**: Generates personalized advice strings based on sleep debt level, habit correlations, average quality, and streak length. Returns empty list if fewer than 3 records.
- **Implemented `generate_weekly_summary(sleep_records, habits)`**: Produces a complete summary dict with avg_duration, avg_quality, avg_mood, total_debt, best_day, worst_day, habit_correlations, and advice_list. Powers the weekly report page.

### __init__.py
- **Added proper exports**: Now exports all six analysis functions: `calculate_duration`, `calculate_sleep_debt`, `get_streak`, `analyze_habit_correlations`, `generate_advice`, `generate_weekly_summary`.

## frontend_siyuan/

### pages.py
- **Removed all temporary helper functions**: `_calculate_duration()`, `_calculate_sleep_debt()`, `_get_streak()` removed. Now imports these from `analysis_yeraly.algorithms`.
- **Added settings/consent system**: New `_load_settings()`, `_save_settings()`, `_get_target_hours()` functions using a local `settings.json` file.

#### Daily Check-in (`_page_checkin()`)
- **Added mood slider**: `st.select_slider` with labels (1=Very Bad through 5=Great).
- **Added habit checkboxes**: "Did you drink coffee/caffeine today?", "Did you exercise today?", "Did you use screens within 1 hour of bed?".
- **Added input validation**: Prevents submission if bedtime equals wake-up time.
- **Added habit record creation**: On submit, creates a HabitRecord linked to the new sleep record ID.
- **Updated SleepRecord creation**: Now includes the mood field.

#### Dashboard (`_page_dashboard()`)
- **Added mood metric**: New column showing average mood (7d) alongside existing metrics.
- **Uses target hours from settings**: Sleep debt calculation now uses the user-configured target instead of hardcoded 8.
- **Added trend line chart**: Shows sleep duration over the last 30 days using `st.line_chart`.
- **Added check-in calendar heatmap**: 28-day grid (4 weeks × 7 days) showing green for logged days and grey for missed days, using HTML/CSS in `st.markdown`.
- **Improved streak display**: Added 🔥 emoji to all streak milestone messages.
- **Added mood column to recent logs table**.

#### Weekly Report (`_page_report()`)
- **Integrated `generate_weekly_summary()`**: Now uses the analysis module instead of manual calculations.
- **Added mood metric**: Shows average mood in the summary section.
- **Added quality trend chart**: Line chart showing quality ratings alongside the duration bar chart.
- **Added habit correlation insights**: Displays which habits are associated with higher/lower quality ratings with sample sizes.
- **Added personalized advice section**: Shows tailored advice from `generate_advice()`.
- **Added "Save this report" button**: Saves the current report snapshot to the reports table.
- **Added saved reports history**: Shows up to 5 most recent saved reports at the bottom.

#### New: User Consent page (`_page_consent()`)
- Shown on first launch when no records exist and no consent flag is stored.
- Explains what data is collected (sleep times, mood, habits), that data is stored locally only, and that the user can delete data at any time.
- "I understand and consent" button stores consent flag in `settings.json` and reruns the app.

#### New: Settings page (`_page_settings()`)
- **Target sleep hours**: Number input (4-12, default 8, step 0.5). Used in sleep debt calculations.
- **Auto-launch toggle**: Checkbox that calls `system_yibo.enable_auto_launch()` or `disable_auto_launch()`.
- **Save Settings button**: Persists all settings to `settings.json`.
- **Delete all data button**: Clears all tables (habits, reports, sleep_records) and resets consent. Shows warning before deletion.

#### `render()` function
- **Added consent check**: Routes to consent page if consent not given and no existing records.
- **Added Settings to navigation**: Sidebar now has 4 options: Daily Check-in, Dashboard, Weekly Report, Settings.

## system_yibo/

### integration.py
- **Implemented `get_auto_launch_script_path()`**: Detects OS (Windows/Mac/Linux) and returns the path to the appropriate launch script.
- **Implemented `enable_auto_launch()`**: On Windows, copies the .bat file to the shell:startup folder. On Mac/Linux, returns instructions for crontab or Login Items.
- **Implemented `disable_auto_launch()`**: On Windows, removes the .bat file from the startup folder. On Mac/Linux, returns instructions for removing the crontab entry.

### auto_launch_windows.bat (NEW, updated 2026-03-16)
- **Fixed**: bare `streamlit` command fails when streamlit is installed inside a virtual environment and the system PATH doesn't include it.
- Now uses `%~dp0..` to `cd` into the project root first.
- Activates `.venv\Scripts\activate.bat` before running `streamlit run app.py`.
- Falls back to `python -m streamlit run app.py` if `.venv` doesn't exist.

### auto_launch_mac.sh (NEW, updated 2026-03-16)
- **Fixed**: same virtual-environment issue as the Windows script.
- Now uses `$(dirname "$0")/..` to `cd` into the project root first.
- Sources `.venv/bin/activate` before running `streamlit run app.py`.
- Falls back to `python3 -m streamlit run app.py` if `.venv` doesn't exist.

### __init__.py
- **Added proper exports**: Now exports `get_auto_launch_script_path`, `enable_auto_launch`, `disable_auto_launch`.

## Other files

### requirements.txt
- **Removed `pandas>=2.0.0`**: pandas is not directly imported anywhere in the codebase (it's installed as a transitive dependency of streamlit). Kept only `streamlit>=1.28.0`. No plotly — charts use built-in `st.line_chart` and `st.bar_chart`.

### settings.json (NEW, created at runtime)
- Local JSON file storing user preferences: `consent_given` (bool), `target_hours` (float), `auto_launch` (bool). Created on first consent or settings save. Listed in `.gitignore` pattern (local config).

### Virtual environment
- **Removed old `.venv`** from `frontend_siyuan/` (was created there by mistake in an earlier session).
- **Created new `.venv` in project root** using `uv venv` + `uv pip install -r requirements.txt`. All scripts and auto-launch files reference this root-level `.venv`.

### README.md (rewritten)
- Replaced the original scaffold README with a complete project README covering: description, all implemented features, tech stack, setup instructions (uv and pip), project structure, privacy statement, and team member table.

### .gitignore
- No changes. Already ignores `.venv/`, `.db`, and `.sqlite` files. `settings.json` is a user-local file.
