#!/bin/bash
cd "$(dirname "$0")/.."

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    streamlit run app.py
else
    echo ".venv not found, trying python -m streamlit..."
    python3 -m streamlit run app.py
fi
