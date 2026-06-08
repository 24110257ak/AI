"""Steepest-Ascent Hill Climbing cho 8-puzzle."""

import time
from typing import List, Optional, Tuple

from Controller.base_controller import BaseController
from Controller.heuristics import HEURISTIC_FNS, SHC_GROUPS, State, get_neighbors, hill_group_label
from Model.puzzle_model import PuzzleModel


def _reconstruct(parents: dict, end_state: State) -> List[State]:
    path = []
    cur: Optional[State] = end_state
    while cur is not None:
        path.append(cur)
        cur = parents.get(cur)
    path.reverse()
    return path


def steepest_ascent_hill_climbing(
    start: State, goal: State, value_key: str
) -> Tuple[List[State], int]:
    """
    Steepest-Ascent Hill Climbing:
    - Sinh tất cả neighbor của Current_State
    - Chọn neighbor có Value cao nhất trong các neighbor tốt hơn Current
    - Dừng khi không còn neighbor nào tốt hơn (local maximum)
    """
    value_fn = HEURISTIC_FNS[value_key]
    parents = {start: None}
    current = start
    expanded = 0

    def score(state: State) -> int:
        return -value_fn(state, goal)

    if current == goal:
        return [current], expanded

    while True:
        expanded += 1
        cur_score = score(current)
        best_next: Optional[State] = None
        best_score = cur_score

        for nxt in get_neighbors(current):
            nxt_score = score(nxt)
            if nxt_score > best_score:
                best_score = nxt_score
                best_next = nxt

        if best_next is None:
            break

        parents[best_next] = current
        current = best_next
        if current == goal:
            break

    return _reconstruct(parents, current), expanded


class SteepestAscentHillClimbingController(BaseController):
    ALGO_NAME = "Steepest-Ascent Hill Climbing"
    SUBTITLE = "Steepest-Ascent — chọn neighbor có Value(n) cao nhất"
    GROUPS = SHC_GROUPS
    THEME = {
        "BG": "#140f1a",
        "PANEL_BG": "#1f1730",
        "GRID_LINE": "#3a2d55",
        "TILE_BG": "#2a2140",
        "TILE_FG": "#e8d4ff",
        "TILE_BORD": "#c77dff",
        "EMPTY_BG": "#140f1a",
        "EMPTY_BORD": "#3a2d55",
        "HL_BG": "#4a2f70",
        "HL_FG": "#ffffff",
        "HL_BORD": "#c77dff",
        "SHADOW": "#0b0812",
        "PRI_BG": "#c77dff",
        "PRI_FG": "#140f1a",
        "SEC_BG": "#1f1730",
        "SEC_FG": "#c77dff",
        "LABEL_FG": "#a894c8",
        "METRIC_BG": "#1a1328",
        "ABTN": "#a855f7",
        "ABTN2": "#3a2d55",
        "UI_BORD": "#c77dff",
    }

    def __init__(self, model: PuzzleModel):
        super().__init__(model)
        self.group = 1
        self.value_metric = ""

    def set_group(self, group: int) -> None:
        self.group = max(1, min(3, int(group)))

    @classmethod
    def subtitle_for_group(cls, group: int) -> str:
        return f"Steepest-Ascent — {hill_group_label(cls.GROUPS[group])}"

    def _value_key(self) -> str:
        return self.GROUPS[self.group]["value"]

    def solve(self) -> bool:
        start, goal = tuple(self.model.state), tuple(self.model.goal)
        self.value_metric = self._value_key()

        t0 = time.perf_counter()
        path, expanded = steepest_ascent_hill_climbing(start, goal, self.value_metric)
        self.elapsed_ms = (time.perf_counter() - t0) * 1000
        self.nodes_visited = expanded
        self.solution_path = path

        return bool(path and path[-1] == goal)

    def get_summary(self) -> dict:
        summary = super().get_summary()
        summary["heuristic_group"] = self.group
        summary["value_metric"] = self.value_metric
        return summary
