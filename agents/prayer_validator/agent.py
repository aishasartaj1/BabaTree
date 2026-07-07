from google.adk.agents import Agent

from agents.prayer_validator.prompts import INSTRUCTION
from agents.prayer_validator.tools import (
    evaluate_window,
    get_cached_prayer_time,
    get_current_time,
    log_prayer,
)
from core.config import settings

prayer_validator_agent = Agent(
    name="prayer_validator",
    model=settings.google_model,
    description="Validates whether a logged prayer falls within its on-time window.",
    instruction=INSTRUCTION,
    tools=[get_cached_prayer_time, get_current_time, evaluate_window, log_prayer],
    output_key="validator_reply",
)
