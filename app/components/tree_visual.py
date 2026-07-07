"""Tree visual + progress bar component for the dashboard."""
from __future__ import annotations

import streamlit as st

WEEKLY_MAX_PRAYERS = 35


def render_tree_visual() -> None:
    emoji = st.session_state.get("tree_emoji", "🌰")
    stage = st.session_state.get("tree_stage", "Seed")
    on_time_count = st.session_state.get("on_time_count", 0)

    st.markdown(f"<div style='text-align:center; font-size:96px'>{emoji}</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='text-align:center; font-weight:600; font-size:20px; color:#2e7d32'>{stage}</div>",
        unsafe_allow_html=True,
    )
    percent = min(on_time_count, WEEKLY_MAX_PRAYERS) / WEEKLY_MAX_PRAYERS * 100
    st.markdown(
        "<div style='margin-top:8px;'>"
        "<div style='display:flex; justify-content:space-between; font-size:16px; "
        "font-weight:600; color:#2e7d32; margin-bottom:4px;'>"
        f"<span>🌱 On-time prayers this week</span><span>{on_time_count}/{WEEKLY_MAX_PRAYERS}</span>"
        "</div>"
        "<div style='width:100%; background-color:#e0e0e0; border-radius:8px; height:22px;'>"
        f"<div style='width:{percent}%; background-color:#2e7d32; height:22px; border-radius:8px;'></div>"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    if st.session_state.get("milestone_reached"):
        st.success(
            "🎉 Milestone reached! In Phase 2, this moment triggers planting a real tree in your name."
        )

    with st.expander("🌳 Why does this tree matter? — Sadaqah Jariyah"):
        st.markdown(
            "<div style='font-size:16px; line-height:1.6;'>"
            "Two kinds of good, one small habit: <b>spiritual wellbeing</b> now, <b>reforestation</b> later.<br><br>"
            "🌱 <b>Instant gratification</b> — every on-time prayer grows your virtual tree right away, "
            "giving you something small and visible to feel <i>today</i>. Same dopamine hit as social "
            "media, used for good.<br><br>"
            "🌳 <b>Delayed, compounding gratification</b> <i>(Phase 2, milestone TBD ~50 prayers)</i> — unlocks "
            "<b>صدقة جارية — Sadaqah Jariyah</b>: a real tree in your name, giving shade and oxygen for "
            "decades — a reward that keeps growing long after you're gone."
            "</div>",
            unsafe_allow_html=True,
        )
