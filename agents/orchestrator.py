"""Composes PrayerValidatorAgent and TreeGrowthAgent into a single sequential
multi-agent turn, and exposes a synchronous helper Streamlit calls directly
from a checkbox callback.
"""
from __future__ import annotations

import asyncio
import time
import uuid

from google.adk.agents import SequentialAgent
from google.adk.runners import InMemoryRunner
from google.genai import types as genai_types

from agents.prayer_validator.agent import prayer_validator_agent
from agents.tree_growth.agent import tree_growth_agent

APP_NAME = "babatree"

babatree_orchestrator = SequentialAgent(
    name="babatree_orchestrator",
    sub_agents=[prayer_validator_agent, tree_growth_agent],
)


async def _run_prayer_turn_async(state: dict, prompt: str) -> dict:
    runner = InMemoryRunner(agent=babatree_orchestrator, app_name=APP_NAME)
    user_id = "babatree_user"
    session_id = str(uuid.uuid4())

    await runner.session_service.create_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id, state=state
    )

    message = genai_types.Content(role="user", parts=[genai_types.Part(text=prompt)])
    async for _ in runner.run_async(user_id=user_id, session_id=session_id, new_message=message):
        pass  # only the final session state matters, not the streamed events

    session = await runner.session_service.get_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )
    return session.state


def run_prayer_turn(state: dict, prayer_name: str, date: str, max_retries: int = 2) -> dict:
    """Run one full validator -> tree-growth agent turn for a single prayer tick.

    `state` is the relevant slice of Streamlit's session_state (prayer_times,
    prayer_log, tree_stage, etc). Returns the updated state dict to merge back
    into st.session_state - the ADK session itself is discarded after this call.

    Retries a couple of times on transient Gemini errors (e.g. 503 UNAVAILABLE,
    per-minute 429s) since those clear up on their own within seconds. Daily quota
    errors are not retried - waiting a few seconds won't fix those.
    """
    prompt = (
        f"The user just marked the prayer '{prayer_name}' as prayed, for date {date}. "
        f"Validate it and update the tree growth accordingly."
    )

    last_error: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            return asyncio.run(_run_prayer_turn_async(state, prompt))
        except Exception as e:  # noqa: BLE001 - deliberately broad, see retry policy above
            last_error = e
            if "PerDay" in str(e) or attempt == max_retries:
                raise
            time.sleep(2)

    raise last_error  # unreachable, but keeps type checkers happy
