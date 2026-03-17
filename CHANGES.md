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
