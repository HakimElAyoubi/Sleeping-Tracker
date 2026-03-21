"""
Sleep Tracker - Main Entry Point (Demo Version)
================================================
This is the main Streamlit application entry point.
Run with: streamlit run app.py

This demo version includes pre-populated sample data.
"""

import streamlit as st

st.set_page_config(
    page_title="Sleep Tracker",
    layout="wide"
)

# Populate demo data on first run
from demo_data import populate_demo_data
populate_demo_data()

from frontend_siyuan.pages import render
render()
