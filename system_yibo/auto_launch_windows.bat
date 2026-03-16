@echo off
cd /d "%~dp0.."

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    streamlit run app.py
) else (
    echo .venv not found, trying python -m streamlit...
    python -m streamlit run app.py
)
