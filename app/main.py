"""BabaTree Streamlit entrypoint.

Run with: streamlit run app/main.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure the project root is importable regardless of the working directory
# Streamlit was launched from (it only puts this file's own folder on sys.path).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st  # noqa: E402

from app.screens.dashboard import render_dashboard  # noqa: E402
from app.screens.login import render_login  # noqa: E402

st.set_page_config(page_title="BabaTree", page_icon="🌳", layout="centered")

st.markdown(
    """
    <style>
    .stApp { background-color: #f6fbf6; }
    div[data-baseweb="tab-list"] { gap: 4px; }
    .stProgress > div > div > div { background-color: #2e7d32; }
    .block-container { padding-top: 2.5rem; padding-bottom: 2rem; }
    div[data-testid="stExpander"] { margin-top: 0.25rem; margin-bottom: 0.25rem; }
    hr { margin: 0.5rem 0 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


def main() -> None:
    if "user_profile" not in st.session_state:
        render_login()
    else:
        render_dashboard()


if __name__ == "__main__":
    main()
