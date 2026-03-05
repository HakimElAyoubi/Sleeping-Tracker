# Sleep Tracker

A collaborative Python Streamlit application for tracking and analyzing sleep patterns.

## Team Members & Responsibilities

| Member  | Folder       | Responsibility                                      |
|---------|--------------|-----------------------------------------------------|
| Siyuan  | `frontend/`  | Streamlit UI components, pages, and user interface  |
| Hakim   | `database/`  | SQLite schema, queries, and data models             |
| Yeraly  | `analysis/`  | Sleep debt calculations, pattern detection, reports |
| Yibo    | `system/`    | Application logic, startup, module integration      |

## Project Structure

```
sleep-tracker/
    app.py              # Main entry point (run with: streamlit run app.py)
    requirements.txt    # Python dependencies
    README.md           # This file
    .gitignore          # Git ignore rules

    frontend/           # Siyuan - UI components
    database/           # Hakim - Database operations
    analysis/           # Yeraly - Analysis algorithms
    system/             # Yibo - Integration logic
```

## Getting Started

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## How to Import Modules Across Folders

Each folder is a Python package. You can import modules like this:

```python
from frontend.pages import some_function
from database.queries import some_function
from analysis.algorithms import some_function
from system.integration import some_function
```

## Guidelines to Avoid Merge Conflicts

1. **Work in your own folder**: Each team member should primarily work in their assigned folder.

2. **Communicate before editing shared files**: The `app.py` file is shared. Coordinate with team members before making changes.

3. **Pull before you push**: Always pull the latest changes before pushing:
   ```bash
   git pull origin main
   git push origin main
   ```

4. **Use feature branches** (optional but recommended):
   ```bash
   git checkout -b feature/your-feature-name
   # ... make changes ...
   git push origin feature/your-feature-name
   # Then create a pull request
   ```

5. **Keep commits small and focused**: Make frequent, small commits rather than large ones.

6. **Add clear commit messages**: Describe what you changed and why.

## Notes

- The folder structure is flexible and can be reorganized as the project evolves.
- Each folder contains `__init__.py` to make it importable as a Python package.
- Database files (`.db`, `.sqlite`) are gitignored to avoid conflicts.
