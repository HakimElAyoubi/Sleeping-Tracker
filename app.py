"""
Sleep Tracker - Main Entry Point
================================
This is the main Streamlit application entry point.
Run with: streamlit run app.py
"""

import streamlit as st

# Import backend initialization
from database_hakim import init_database

# Import frontend entry point
from frontend_siyuan.pages import render


# Page configuration (must be first Streamlit command)
st.set_page_config(
    page_title="Sleep Tracker",
    page_icon="😴",
    layout="wide"
)

# Initialize database
init_database()

# Launch the frontend application
render()

