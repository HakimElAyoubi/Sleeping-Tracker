# Sleep Tracker

A Streamlit web app that helps university students track and improve their sleep habits through daily check-ins, sleep debt monitoring, habit correlation analysis, and weekly reports.

**ENGF0034 Scenario 2 — UCL**

## Features

- **Daily check-in** — log bedtime, wake time, sleep quality (1-5), mood (1-5), and lifestyle habits (caffeine, exercise, screen use)
- **Dashboard** — key metrics (streak, sleep debt, avg duration/quality/mood over 7 days), 30-day duration trend chart, 28-day check-in heatmap calendar, and recent logs table
- **Sleep debt tracking** — cumulative difference vs a user-defined target (default 8 hours)
- **Streak tracking** — consecutive check-in days with milestone messages at 3, 7, 14, and 30 days
- **Weekly report** — duration bar chart, quality trend line, habit correlation insights (coffee/exercise/screen vs sleep quality), personalised advice, and saveable report snapshots
- **Auto-launch** — Windows `.bat` and Mac/Linux `.sh` scripts that activate the venv and start the app
- **Privacy-first** — all data stored locally in SQLite; no data sent anywhere; user consent required on first launch; full data deletion from Settings
- **Settings** — configurable target sleep hours, auto-launch toggle, delete-all-data option

## Tech Stack

- **Python 3.10+**
- **Streamlit** — UI framework (built-in `st.line_chart`, `st.bar_chart` for visualisations)
- **SQLite** — local database (Python standard library `sqlite3`)

## Getting Started

### Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Setup with uv

```bash
uv venv
uv pip install -r requirements.txt
```

### Setup with pip

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### Run

```bash
streamlit run app.py
```

Or use the auto-launch scripts:

- **Windows**: double-click `system_yibo/auto_launch_windows.bat`
- **Mac/Linux**: run `bash system_yibo/auto_launch_mac.sh`

## Project Structure

```
app.py                      Entry point
database_hakim/             SQLite database — schema, models, CRUD operations
frontend_siyuan/            Streamlit UI — check-in, dashboard, weekly report, consent, settings
analysis_yeraly/            Analysis algorithms — sleep debt, streaks, habit correlations, advice
system_yibo/                OS integration — auto-launch scripts (Windows .bat, Mac .sh)
requirements.txt            Python dependencies
```

## Privacy

All data is stored locally in a SQLite database file (`sleep_tracker.db`). No data is sent to any server or third party. On first launch, users must review and consent to the data practices. All data can be permanently deleted from the Settings page at any time.

## Team

| Member | Module |
|---|---|
| Hakim El Ayoubi | `database_hakim/` — database schema, models, queries |
| Siyuan Wu | `frontend_siyuan/` — Streamlit UI and page logic |
| Yeraly Baimagambetov | `analysis_yeraly/` — analysis algorithms and advice generation |
| Yibo Ma | `system_yibo/` — OS integration and auto-launch scripts |
