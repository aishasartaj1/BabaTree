"""Screen 1 - Login: collect name + city, fetch the week's prayer times once."""
from __future__ import annotations

from datetime import datetime, timedelta

import streamlit as st

from agents.guardrails import GuardrailError, sanitize_city, sanitize_name
from mcp_server.aladhan_client import fetch_weekly_prayer_times


def _apply_demo_offsets(prayer_times: dict) -> dict:
    """Demo/recording aid: shift every cached prayer's Adhan time to just under a
    minute ago, so every checkbox is immediately inside its on-time window for the
    length of a demo. The real validator/tree-growth agents still run for real -
    only the synthetic Adhan timestamps are injected, not the VALID/LATE decision.
    """
    shifted_time = (datetime.now().astimezone() - timedelta(minutes=1)).isoformat()
    for prayers in prayer_times.get("days", {}).values():
        for prayer_name in prayers:
            prayers[prayer_name] = shifted_time
    return prayer_times


def render_login() -> None:
    st.title("🌳 BabaTree")
    st.markdown(
        "<div style='font-size:20px; color:#4a4a4a;'>A nudge to pray. A tree that grows.</div>",
        unsafe_allow_html=True,
    )
    st.write("")

    with st.form("login_form"):
        name = st.text_input("Full name")
        city = st.text_input("City")
        country = st.text_input("Country (optional)")
        demo_mode = st.checkbox(
            "🎬 Demo mode - shift every prayer time to just now (for recording/testing)"
        )
        submitted = st.form_submit_button("Start")

    if not submitted:
        return

    try:
        clean_name = sanitize_name(name)
        clean_city = sanitize_city(city)
    except GuardrailError as e:
        st.error(str(e))
        return

    with st.spinner(f"Fetching this week's prayer times for {clean_city}..."):
        try:
            prayer_times = fetch_weekly_prayer_times(clean_city, country.strip())
        except Exception as e:  # Aladhan lookup failed (bad city, network, etc.)
            st.error(f"Could not fetch prayer times for '{clean_city}': {e}")
            return

    if demo_mode:
        prayer_times = _apply_demo_offsets(prayer_times)

    st.session_state.user_profile = {
        "name": clean_name,
        "city": clean_city,
        "country": country.strip(),
    }
    st.session_state.prayer_times = prayer_times
    st.session_state.prayer_log = {}
    st.session_state.tree_stage = "Seed"
    st.session_state.tree_emoji = "🌰"
    st.session_state.on_time_count = 0
    st.session_state.milestone_reached = False
    st.rerun()
