
# Sleep Tracker — Change Log
> Personal changes made on 2026-03-18.

## frontend_siyuan/pages.py

### Weekly Report: Export/Delete saved reports
- Replaced the saved report text list with a table-style display using pandas (`st.table`) so it looks like spreadsheet rows/columns.
- Added report actions section with selector:
  - `Export` action creates CSV using `csv.writer` + `io.StringIO` and downloads with `st.download_button`.
  - `Delete` action shows confirmation (`Confirm Delete` / `Cancel`) before calling delete.
- Added report ID at the front of selectable options (`ID {id} - ...`) to avoid confusion when selecting a report.
- Fixed UI state issue: when switching to Export action, delete confirmation is cleared so old delete warnings do not stay visible.

### Dashboard: Edit/Delete sleep logs
- Upgraded Recent Sleep Logs to table format with an `ID` column.
- Added log action controls under the table:
  - `Edit` opens an inline form prefilled with current record data.
  - `Delete` opens a confirmation block before removing record.
- Edit flow updates record via `update_sleep_record(...)` and recalculates duration using `calculate_duration(...)`.
- Delete flow removes record via `delete_sleep_record(...)` with confirm/cancel.
- Fixed UI state handling:
  - Switching action to `Delete` hides the edit form.
  - Switching action to `Edit` clears pending delete confirmation.

### Daily Check-in: switch for past-day logging
- Added settings-driven behavior in check-in page:
  - If past-day logging is OFF, date input is locked to today.
  - If ON, date input allows selecting any date up to today.
- Kept duplicate-date validation (`date_exists`) so users cannot insert two logs for the same date.

### Settings: toggle for past-day logging
- Added `st.toggle("Allow logging sleep for past days")`.
- Saves/loads `allow_past_day_logging` via existing settings helpers.

### Import and cleanup work in pages.py
- Removed unused imports in `pages.py` to keep the file clean.
- Kept only imports actually used by current page logic.

---

## database_hakim (only changes required to support my UI features)

### queries.py
- Added `delete_report(report_id)` so weekly report delete action can remove a saved report by ID.

### __init__.py
- Updated exports so frontend can import functions used by the new UI actions (`delete_report`, `update_sleep_record`, `delete_sleep_record`).

---

## Bug Fixes (2026-03-20)

### Bug: Orphaned habit records after deleting a sleep log
**Problem:** Deleting a sleep record left its linked `habits` row in the database because there was no cascade delete. This caused analysis algorithms (e.g. habit correlation in weekly reports) to reference habit data that no longer had a matching sleep record. 

**Fixes applied:**

1. **`database_hakim/connection.py` — Enable foreign key enforcement**
   - Added `conn.execute("PRAGMA foreign_keys = ON")` in `get_connection()` so SQLite actually enforces FK constraints at runtime (SQLite has them off by default).

2. **`database_hakim/connection.py` — Add `ON DELETE CASCADE` to habits FK**
   - Changed the habits table schema from `FOREIGN KEY (sleep_record_id) REFERENCES sleep_records(id)` to `FOREIGN KEY (sleep_record_id) REFERENCES sleep_records(id) ON DELETE CASCADE`, so new databases will automatically delete habits when their parent sleep record is removed.

3. **`database_hakim/queries.py` — Explicitly delete habits in `delete_sleep_record()`**
   - Added `DELETE FROM habits WHERE sleep_record_id = ?` before the sleep record delete. This ensures existing databases (where the schema cannot be altered retroactively) also clean up habits correctly.

### Bug: Stale `st.session_state` keys after deletion
**Problem:** After deleting a sleep log or report, the code only set the current record's confirmation key to `False`. Old keys from previously viewed records (e.g. `confirm_delete_log_5`, `edit_log_3`) were never removed, causing stale cached state that could resurface incorrect confirmation dialogs or interfere with UI logic on re-renders.

**Fixes applied:**

1. **`frontend_siyuan/pages.py` — Clean up session state after sleep log delete**
   - After a successful delete, all keys matching `confirm_delete_log_*` and `edit_log_*` are now removed from `st.session_state` instead of just toggling the current one to `False`.

2. **`frontend_siyuan/pages.py` — Clean up session state after report delete**
   - Same approach: all keys matching `confirm_delete_*` are purged from `st.session_state` after a report is deleted.

### Bug: Edit sleep log did not update habits
**Problem:** The edit form for sleep logs only updated the `sleep_records` table but never touched the linked `habits` row. Users had no way to correct habit data (coffee, exercise, screen) after initial entry, causing stale habit info to persist and skew analysis/correlation results.

**Fixes applied:**

1. **`database_hakim/queries.py` — Added `update_habit()` function**
   - New function: `UPDATE habits SET took_coffee=?, exercised=?, used_screen=? WHERE sleep_record_id=?` with commit.

2. **`database_hakim/__init__.py` — Exported new functions**
   - Added `update_habit` and `get_habit_by_sleep_record_id` to module exports.

3. **`frontend_siyuan/pages.py` — Added habit checkboxes to edit form**
   - Loads existing habit data via `get_habit_by_sleep_record_id()` when the edit form opens.
   - Added three checkboxes (coffee, exercise, screen) pre-filled with current values.
   - On submit, calls `update_habit()` right after `update_sleep_record()` succeeds.

### Enhancement: Show notes in sleep log table
- Added "Notes" column to the Recent Sleep Logs table on the Dashboard page.
