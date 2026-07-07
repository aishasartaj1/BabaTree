from google.adk.agents import Agent

from agents.tree_growth.prompts import INSTRUCTION
from agents.tree_growth.tools import (
    check_milestone,
    get_prayer_log,
    trigger_tree_planting,
    update_tree_stage,
)
from core.config import settings

tree_growth_agent = Agent(
    name="tree_growth",
    model=settings.google_model,
    description="Updates the tree's growth stage and checks the Phase 2 real-tree-planting milestone.",
    instruction=INSTRUCTION,
    tools=[get_prayer_log, update_tree_stage, check_milestone, trigger_tree_planting],
    output_key="growth_reply",
)
