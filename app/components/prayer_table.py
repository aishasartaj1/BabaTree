"""Weekly prayer table - one tab per day, so days are navigated by clicking
"next" instead of stacking into one long vertical scroll."""
from __future__ import annotations

from datetime import datetime, timedelta

import streamlit as st

from agents.orchestrator import run_prayer_turn
from core.config import settings
from core.models import PrayerName

STATUS_COLORS = {"VALID": "#2e7d32", "LATE": "#f9a825"}
DEFAULT_STATUS_COLOR = "#d9d9d9"

MESSAGE_STYLES = {
    "success": ("#e8f5e9", "#2e7d32"),
    "warning": ("#fff8e1", "#8a6d3b"),
}

WINDOW_HELP = (
    "A prayer only counts as on-time within {minutes} minutes of its Adhan. "
    "The window isn't a technicality - praying as soon as its time begins reflects "
    "eagerness to answer the call, not just squeezing it in before it's too late."
)


def _mark_pending(prayer_name: str, date_str: str, checkbox_key: str) -> None:
    """Checkbox on_change callback - just records intent and returns instantly, so
    the checkbox visibly ticks right away. The actual slow validation runs afterward
    in process_pending_prayer(), called from the main script body where st.spinner and
    the result message can actually render (callbacks can't render UI)."""
    log_key = f"{date_str}::{prayer_name}"
    if st.session_state.prayer_log.get(log_key) is not None:
        return
    st.session_state.pending_validation = (prayer_name, date_str, checkbox_key)


def process_pending_prayer() -> None:
    """Runs the real validator/tree-growth agent turn for whatever checkbox was just
    ticked. Called from the main script body (not a callback) so the spinner renders,
    then stores the result for _render_last_message() to display with a dismiss button."""
    pending = st.session_state.get("pending_validation")
    if not pending:
        return
    prayer_name, date_str, checkbox_key = pending
    st.session_state.pending_validation = None

    state_slice = {
        "prayer_times": st.session_state.prayer_times,
        "prayer_log": st.session_state.prayer_log,
    }
    with st.spinner(f"🕊️ Validating {prayer_name} and growing your tree..."):
        try:
            updated_state = run_prayer_turn(state_slice, prayer_name, date_str)
        except Exception as e:  # LLM/API hiccup (e.g. rate limit) - don't crash the app
            st.session_state.last_message = (f"Could not validate this prayer right now: {e}", "warning")
            st.session_state[checkbox_key] = False  # reset so the user can retry
            return

    st.session_state.prayer_log = updated_state.get("prayer_log", st.session_state.prayer_log)
    st.session_state.tree_stage = updated_state.get("tree_stage", st.session_state.tree_stage)
    st.session_state.tree_emoji = updated_state.get("tree_emoji", st.session_state.tree_emoji)
    st.session_state.on_time_count = updated_state.get("on_time_count", st.session_state.on_time_count)
    st.session_state.milestone_reached = updated_state.get(
        "milestone_reached", st.session_state.milestone_reached
    )

    new_status = st.session_state.prayer_log.get(f"{date_str}::{prayer_name}")
    if new_status == "VALID":
        st.session_state.last_message = (
            f"🎉 Yay! You prayed {prayer_name} on time — your tree is growing!",
            "success",
        )
    else:
        st.session_state.last_message = (
            f"{prayer_name} logged, but just outside its on-time window this time.",
            "warning",
        )


def _render_last_message() -> None:
    message = st.session_state.get("last_message")
    if not message:
        return
    text, kind = message
    bg_color, text_color = MESSAGE_STYLES.get(kind, MESSAGE_STYLES["warning"])

    with st.container(key="last_message_box"):
        st.markdown(
            f"<style>"
            f".st-key-last_message_box {{ background-color:{bg_color}; border-radius:8px; "
            f"padding:2px 8px; }}"
            f".st-key-last_message_box .stButton button {{ background:transparent; border:none; "
            f"color:{text_color}; font-weight:700; padding:0; box-shadow:none; }}"
            f"</style>",
            unsafe_allow_html=True,
        )
        col_text, col_close = st.columns([20, 1])
        col_text.markdown(
            f"<div style='color:{text_color}; padding-top:8px;'>{text}</div>",
            unsafe_allow_html=True,
        )
        if col_close.button("✕", key="dismiss_last_message"):
            st.session_state.last_message = None
            st.rerun()


def _render_day(date_str: str, prayers: dict) -> None:
    for prayer in PrayerName:
        prayer_name = prayer.value
        adhan_iso = prayers.get(prayer_name)
        if not adhan_iso:
            continue
        adhan_dt = datetime.fromisoformat(adhan_iso)
        window_end = adhan_dt + timedelta(minutes=settings.prayer_window_minutes)

        log_key = f"{date_str}::{prayer_name}"
        status = st.session_state.prayer_log.get(log_key)
        already_logged = status is not None
        checkbox_key = f"checkbox::{log_key}"

        with st.container(border=True):
            col_status, col_name, col_time, col_check = st.columns([0.5, 2, 2.5, 1])
            status_color = STATUS_COLORS.get(status, DEFAULT_STATUS_COLOR)
            col_status.markdown(
                f"<div style='width:26px; height:26px; border-radius:6px; "
                f"background-color:{status_color}; margin-top:10px;'></div>",
                unsafe_allow_html=True,
            )
            col_name.markdown(f"**{prayer_name}**")
            col_time.markdown(
                f"{adhan_dt.strftime('%H:%M')} → {window_end.strftime('%H:%M')}",
                help=WINDOW_HELP.format(minutes=settings.prayer_window_minutes),
            )
            col_check.checkbox(
                "Prayed",
                value=already_logged,
                key=checkbox_key,
                disabled=already_logged,
                on_change=_mark_pending,
                args=(prayer_name, date_str, checkbox_key),
            )


def render_prayer_table() -> None:
    _render_last_message()

    st.info(
        "🕐 It's not enough to pray - pray **early**. Only prayers logged within their "
        "window (Adhan → +20 min) grow your tree."
    )

    days = st.session_state.prayer_times.get("days", {})
    sorted_dates = sorted(days.keys())
    tab_labels = [datetime.fromisoformat(d).strftime("%a, %d %b") for d in sorted_dates]

    tabs = st.tabs(tab_labels)
    for tab, date_str in zip(tabs, sorted_dates):
        with tab:
            _render_day(date_str, days[date_str])
