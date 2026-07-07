"""Screen 2 - Dashboard: tree visual, progress, and the weekly prayer table."""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st

from app.components.prayer_table import process_pending_prayer, render_prayer_table
from app.components.tree_visual import render_tree_visual


def render_dashboard() -> None:
    process_pending_prayer()  # must run before render_tree_visual() so its count is fresh

    profile = st.session_state.user_profile
    timezone_name = st.session_state.prayer_times.get("timezone")
    now = datetime.now(ZoneInfo(timezone_name)) if timezone_name else datetime.now().astimezone()

    st.title("🌳 BabaTree")
    st.markdown(f"#### Assalamu Alaikum, {profile['name']} 👋")
    st.markdown(
        f"<div style='font-size:16px; color:#4a4a4a;'>📍 {profile['city']} · "
        f"{now.strftime('%A, %d %B %Y · %I:%M %p')}</div>",
        unsafe_allow_html=True,
    )

    render_tree_visual()
    render_prayer_table()

    st.divider()
    if st.button("Log out / restart"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
