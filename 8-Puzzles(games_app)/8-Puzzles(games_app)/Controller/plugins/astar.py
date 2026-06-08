"""A* — f(n) = g(n) + h(n) với preset nhóm h/g."""

import heapq
import time
from typing import Dict, List, Optional, Tuple

from Model.puzzle_model import PuzzleModel
from Controller.base_controller import BaseController
from Controller.heuristics import (
    ASTAR_GROUPS,
    HEURISTIC_FNS,
    STEP_COST_FNS,
    State,
    get_neighbors,
    group_label,
)


def astar_search(
    start: State,
    goal: State,
    h_key: str,
    g_key: str,
) -> Tuple[Optional[List[State]], int, int]:
    if start == goal:
        return [start], 0, 1

    h_fn = HEURISTIC_FNS[h_key]
    step_fn = STEP_COST_FNS[g_key]

    counter = 0
    open_heap: List[Tuple[int, int, State]] = []
    g_score: Dict[State, int] = {start: 0}
    came_from: Dict[State, Optional[State]] = {start: None}
    closed: set = set()
    nodes_expanded = 0

    counter += 1
    heapq.heappush(open_heap, (h_fn(start, goal), counter, start))

    while open_heap:
        _, _, current = heapq.heappop(open_heap)
        if current in closed:
            continue
        if current == goal:
            path = []
            node = current
            while node is not None:
                path.append(node)
                node = came_from[node]
            path.reverse()
            return path, g_score[goal], nodes_expanded

        closed.add(current)
        nodes_expanded += 1

        for nxt in get_neighbors(current):
            if nxt in closed:
                continue
            tentative = g_score[current] + step_fn(current, nxt, goal)
            if nxt not in g_score or tentative < g_score[nxt]:
                g_score[nxt] = tentative
                came_from[nxt] = current
                counter += 1
                f = tentative + h_fn(nxt, goal)
                heapq.heappush(open_heap, (f, counter, nxt))

    return None, 0, nodes_expanded


class AStarController(BaseController):
    ALGO_NAME = "A*"
    SUBTITLE = "A* — f = g + h"
    GROUPS = ASTAR_GROUPS
    THEME = {
        "BG": "#0d1a12", "PANEL_BG": "#122818", "GRID_LINE": "#1e4d30",
        "TILE_BG": "#1a3d28", "TILE_FG": "#b8ffd4", "TILE_BORD": "#3dff8a",
        "EMPTY_BG": "#0d1a12", "EMPTY_BORD": "#1e4d30",
        "HL_BG": "#1a5c38", "HL_FG": "#ffffff", "HL_BORD": "#3dff8a",
        "SHADOW": "#061008", "PRI_BG": "#3dff8a", "PRI_FG": "#0d1a12",
        "SEC_BG": "#122818", "SEC_FG": "#3dff8a", "LABEL_FG": "#7ab89a",
        "METRIC_BG": "#0f2018", "ABTN": "#2ecc71", "ABTN2": "#1e4d30",
        "UI_BORD": "#3dff8a",
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
        return f"A* — {group_label(cls.GROUPS[group])}"

    def solve(self) -> bool:
        start, goal = tuple(self.model.state), tuple(self.model.goal)
        h_key, g_key = self._resolve_keys()
        self.h_label = h_key
        self.g_label = g_key

        t0 = time.perf_counter()
        path, total_cost, nodes = astar_search(start, goal, h_key, g_key)
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
