"""IDA* — lặp sâu dần theo ngưỡng f = g + h."""

import time
from typing import Dict, List, Optional, Tuple

from Model.puzzle_model import PuzzleModel
from Controller.base_controller import BaseController
from Controller.heuristics import (
    IDA_GROUPS,
    HEURISTIC_FNS,
    STEP_COST_FNS,
    State,
    get_neighbors,
    group_label,
)


def ida_star_search(
    start: State,
    goal: State,
    h_key: str,
    g_key: str,
    max_threshold: int = 10_000,
) -> Tuple[Optional[List[State]], int, int]:
    if start == goal:
        return [start], 0, 1

    h_fn = HEURISTIC_FNS[h_key]
    step_fn = STEP_COST_FNS[g_key]
    nodes_expanded = 0

    def search(current: State, g: int, threshold: int, path: List[State]) -> Tuple[int, Optional[List[State]]]:
        nonlocal nodes_expanded
        f = g + h_fn(current, goal)
        if f > threshold:
            return f, None
        if current == goal:
            return 0, path

        min_overflow = 10**9
        for nxt in get_neighbors(current):
            if nxt in path:
                continue
            nodes_expanded += 1
            step = step_fn(current, nxt, goal)
            result, solution = search(nxt, g + step, threshold, path + [nxt])
            if solution is not None:
                return 0, solution
            if result < min_overflow:
                min_overflow = result
        return min_overflow, None

    threshold = h_fn(start, goal)
    while threshold <= max_threshold:
        result, path = search(start, 0, threshold, [start])
        if path is not None:
            total_cost = 0
            for i in range(1, len(path)):
                total_cost += step_fn(path[i - 1], path[i], goal)
            return path, total_cost, nodes_expanded
        if result == 10**9:
            break
        threshold = result

    return None, 0, nodes_expanded


class IDAStarController(BaseController):
    ALGO_NAME = "IDA*"
    SUBTITLE = "IDA* — iterative deepening theo f = g + h"
    GROUPS = IDA_GROUPS
    THEME = {
        "BG": "#1a1208", "PANEL_BG": "#2a1c0a", "GRID_LINE": "#4d3810",
        "TILE_BG": "#3d2e14", "TILE_FG": "#ffe8b8", "TILE_BORD": "#ffb84d",
        "EMPTY_BG": "#1a1208", "EMPTY_BORD": "#4d3810",
        "HL_BG": "#5c4010", "HL_FG": "#ffffff", "HL_BORD": "#ffb84d",
        "SHADOW": "#100a04", "PRI_BG": "#ffb84d", "PRI_FG": "#1a1208",
        "SEC_BG": "#2a1c0a", "SEC_FG": "#ffb84d", "LABEL_FG": "#b8a07a",
        "METRIC_BG": "#201808", "ABTN": "#e6a020", "ABTN2": "#4d3810",
        "UI_BORD": "#ffb84d",
    }

    def __init__(self, model: PuzzleModel):
        super().__init__(model)
        self.group = 1
        self.total_cost = 0
        self.h_label = ""
        self.g_label = ""

    def set_group(self, group: int) -> None:
        self.group = max(1, min(3, int(group)))

    def _resolve_keys(self) -> Tuple[str, str]:
        cfg = self.GROUPS[self.group]
        return cfg["h"], cfg["g"]

    @classmethod
    def subtitle_for_group(cls, group: int) -> str:
        return f"IDA* — {group_label(cls.GROUPS[group])}"

    def solve(self) -> bool:
        start, goal = tuple(self.model.state), tuple(self.model.goal)
        h_key, g_key = self._resolve_keys()
        self.h_label = h_key
        self.g_label = g_key

        t0 = time.perf_counter()
        path, total_cost, nodes = ida_star_search(start, goal, h_key, g_key)
        self.elapsed_ms = (time.perf_counter() - t0) * 1000
        self.nodes_visited = nodes
        self.total_cost = total_cost

        if path:
            self.solution_path = path
            return True
        self.solution_path = []
        return False

    def get_summary(self) -> dict:
        summary = super().get_summary()
        summary["total_cost"] = self.total_cost
        summary["heuristic_group"] = self.group
        summary["h_metric"] = self.h_label
        summary["g_metric"] = self.g_label
        return summary
