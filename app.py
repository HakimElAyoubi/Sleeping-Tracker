"""
Sleep Tracker - Main Entry Point
================================
This is the main Streamlit application entry point.
Run with: streamlit run app.py
"""

import streamlit as st

st.set_page_config(
    page_title="Sleep Tracker",
    page_icon="😴",
    layout="wide"
)

from frontend_siyuan.pages import render
render()
