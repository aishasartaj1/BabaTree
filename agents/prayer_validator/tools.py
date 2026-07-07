"""Tools for PrayerValidatorAgent. All read/write ADK session state, which is
seeded per-turn from Streamlit's session_state (see agents/orchestrator.py).
"""
from __future__ import annotations

from datetime import datetime

from google.adk.tools import ToolContext

from core.config import settings
from core.models import PrayerName
from core.prayer_rules import validate_prayer_time


def get_cached_prayer_time(prayer_name: str, date: str, tool_context: ToolContext) -> dict:
    """Look up the cached Adhan time for a prayer on a given date (YYYY-MM-DD).

    Reads the 'prayer_times' key in session state, populated once at login by
    the Aladhan MCP server. This tool never calls the MCP server itself.
    """
    days = tool_context.state.get("prayer_times", {}).get("days", {})
    adhan_time = days.get(date, {}).get(prayer_name)
    if not adhan_time:
        return {"found": False}
    return {"found": True, "adhan_time": adhan_time}


def get_current_time(tool_context: ToolContext) -> dict:
    """Return the current wall-clock time in ISO format."""
    return {"current_time": datetime.now().astimezone().isoformat()}


def evaluate_window(
    prayer_name: str, date: str, adhan_time: str, current_time: str, tool_context: ToolContext
) -> dict:
    """Deterministically decide VALID or LATE using the fixed-minute window rule.

    This performs the actual time comparison in plain Python, not LLM reasoning,
    so the on-time/late decision is always numerically correct.
    """
    result = validate_prayer_time(
        prayer_name=PrayerName(prayer_name),
        date=date,
        adhan_time=datetime.fromisoformat(adhan_time),
        tick_time=datetime.fromisoformat(current_time),
        window_minutes=settings.prayer_window_minutes,
    )
    return {"status": result.status.value, "minutes_after_adhan": result.minutes_after_adhan}


def log_prayer(prayer_name: str, date: str, status: str, tool_context: ToolContext) -> dict:
    """Persist the validated prayer status ('VALID' or 'LATE') into session state."""
    log = tool_context.state.get("prayer_log", {})
    log[f"{date}::{prayer_name}"] = status
    tool_context.state["prayer_log"] = log
    return {"logged": True, "status": status}
