from core.models import TreeStageName

# (min_count, max_count, stage, emoji) — max_count inclusive
STAGE_THRESHOLDS: list[tuple[int, int, TreeStageName, str]] = [
    (0, 0, TreeStageName.SEED, "🌰"),
    (1, 7, TreeStageName.SPROUT, "🌱"),
    (8, 17, TreeStageName.SAPLING, "🌿"),
    (18, 28, TreeStageName.YOUNG_TREE, "🌳"),
    (29, 35, TreeStageName.MATURE_TREE, "🌲"),
]


def get_tree_stage(on_time_count: int) -> tuple[TreeStageName, str]:
    """Map a cumulative on-time prayer count (0-35 for the week) to a tree stage + emoji."""
    capped = max(0, min(on_time_count, STAGE_THRESHOLDS[-1][1]))
    for low, high, stage, emoji in STAGE_THRESHOLDS:
        if low <= capped <= high:
            return stage, emoji
    return STAGE_THRESHOLDS[-1][2], STAGE_THRESHOLDS[-1][3]


def check_milestone(cumulative_on_time_count: int, milestone_target: int) -> bool:
    """Whether the running cumulative (across all weeks) on-time count has hit the Phase 2 milestone."""
    return cumulative_on_time_count >= milestone_target
