"""Sync client for the BabaTree Aladhan MCP server.

Spawns aladhan_server.py as a subprocess over stdio and calls its single tool
exactly once, at login. Never called again during prayer logging.
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PROJECT_ROOT = Path(__file__).parent.parent
SERVER_SCRIPT = PROJECT_ROOT / "mcp_server" / "aladhan_server.py"


async def _fetch_weekly_prayer_times_async(city: str, country: str) -> dict:
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_SCRIPT)],
        cwd=str(PROJECT_ROOT),
        env={**os.environ, "PYTHONPATH": str(PROJECT_ROOT)},
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "get_weekly_prayer_times", {"city": city, "country": country}
            )
            if result.isError:
                raise RuntimeError(f"Aladhan MCP tool error: {result.content}")
            if result.structuredContent is None:
                raise RuntimeError("Aladhan MCP tool returned no structured content")
            return result.structuredContent


def fetch_weekly_prayer_times(city: str, country: str = "") -> dict:
    """Fetch 7 days of prayer times for a city. Called once at login."""
    return asyncio.run(_fetch_weekly_prayer_times_async(city, country))
