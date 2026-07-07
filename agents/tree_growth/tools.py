"""Tools for TreeGrowthAgent."""
from __future__ import annotations

from google.adk.tools import ToolContext

from core.config import settings
from core.models import ValidationStatus
from core.tree_stages import check_milestone as _check_milestone
from core.tree_stages import get_tree_stage


def get_prayer_log(tool_context: ToolContext) -> dict:
    """Return the current on-time count and total logged prayers for this week."""
    log = tool_context.state.get("prayer_log", {})
    on_time_count = sum(1 for status in log.values() if status == ValidationStatus.VALID.value)
    return {"on_time_count": on_time_count, "total_logged": len(log)}


def update_tree_stage(on_time_count: int, tool_context: ToolContext) -> dict:
    """Recompute and persist the tree's growth stage from the weekly on-time count."""
    stage, emoji = get_tree_stage(on_time_count)
    tool_context.state["tree_stage"] = stage.value
    tool_context.state["tree_emoji"] = emoji
    tool_context.state["on_time_count"] = on_time_count
    return {"stage": stage.value, "emoji": emoji}


def check_milestone(cumulative_on_time_count: int, tool_context: ToolContext) -> dict:
    """Check whether the running cumulative on-time count has hit the Phase 2 milestone."""
    reached = _check_milestone(cumulative_on_time_count, settings.milestone_target)
    tool_context.state["milestone_reached"] = reached
    return {"milestone_reached": reached, "target": settings.milestone_target}


def trigger_tree_planting(user_name: str, tool_context: ToolContext) -> dict:
    """[Phase 2 stub] Would call a reforestation partner API to plant a real tree.

    Not implemented in Phase 1 - only records that the milestone was reached.
    """
    tool_context.state["tree_planting_requested"] = True
    return {"status": "not_implemented", "note": "Phase 2 feature - no external API call is made yet."}
