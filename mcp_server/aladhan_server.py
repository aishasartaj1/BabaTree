"""MCP server wrapping the Aladhan prayer-times API.

Run standalone: python mcp_server/aladhan_server.py
Spawned once per session by mcp_server/aladhan_client.py at login — never
called again during prayer logging (validation reads from cached session state).
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import httpx
from mcp.server.fastmcp import FastMCP

from core.config import settings
from core.models import PrayerName

mcp = FastMCP(name="aladhan-prayer-times")

PRAYER_KEYS = [p.value for p in PrayerName]  # Fajr, Dhuhr, Asr, Maghrib, Isha


def _fetch_month(city: str, country: str, year: int, month: int) -> list[dict]:
    response = httpx.get(
        f"{settings.aladhan_base_url}/calendarByCity",
        params={"city": city, "country": country, "month": month, "year": year},
        timeout=15,
        follow_redirects=True,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("code") != 200:
        raise ValueError(f"Aladhan API error: {payload.get('status')}")
    return payload["data"]


@mcp.tool()
def get_weekly_prayer_times(city: str, country: str = "") -> dict[str, Any]:
    """Fetch the next 7 days of Fajr/Dhuhr/Asr/Maghrib/Isha prayer times for a city.

    Returns a dict keyed by ISO date ("YYYY-MM-DD"), each mapping prayer name to an
    ISO 8601 timestamp, timezone-aware in the city's local timezone.
    """
    if not city.strip():
        raise ValueError("city must not be empty")

    today = date.today()
    target_dates = [today + timedelta(days=i) for i in range(7)]

    months_needed = {(d.year, d.month) for d in target_dates}
    month_data = {ym: _fetch_month(city, country, ym[0], ym[1]) for ym in months_needed}

    days: dict[str, dict] = {}
    timezone_name = ""

    for d in target_dates:
        day_entry = month_data[(d.year, d.month)][d.day - 1]
        timezone_name = day_entry["meta"]["timezone"]
        tz = ZoneInfo(timezone_name)
        timings = day_entry["timings"]

        prayers = {}
        for prayer_name in PRAYER_KEYS:
            raw_time = timings[prayer_name].split(" ")[0]  # strip "(BST)"-style suffix
            hour, minute = map(int, raw_time.split(":"))
            prayers[prayer_name] = datetime(d.year, d.month, d.day, hour, minute, tzinfo=tz).isoformat()

        days[d.isoformat()] = prayers

    return {"city": city, "country": country, "timezone": timezone_name, "days": days}


if __name__ == "__main__":
    mcp.run(transport="stdio")
