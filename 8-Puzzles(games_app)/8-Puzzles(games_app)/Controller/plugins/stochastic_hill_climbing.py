"""Stochastic Hill Climbing cho 8-puzzle (Value = Manhattan)."""

import time
import random
from typing import List, Optional, Tuple

from Controller.base_controller import BaseController
from Controller.heuristics import (
    HEURISTIC_FNS,
    SHC_MANHATTAN_MISPLACED_GROUPS,
    State,
    get_neighbors,
    hill_group_label,
)
from Model.puzzle_model import PuzzleModel


def _reconstruct(parents: dict, end_state: State) -> List[State]:
    path = []
    cur: Optional[State] = end_state
    while cur is not None:
        path.append(cur)
        cur = parents.get(cur)
    path.reverse()
    return path


def stochastic_hill_climbing(
    start: State, goal: State, value_key: str
) -> Tuple[List[State], int]:
    """
    Stochastic Hill Climbing:
    - Sinh tất cả neighbor của Current
    - Chọn ngẫu nhiên một neighbor có Value tốt hơn Current
    - Dừng khi không còn neighbor tốt hơn (local maximum)
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
        improving = [nxt for nxt in get_neighbors(current) if score(nxt) > cur_score]
        if not improving:
            break
        nxt = random.choice(improving)
        parents[nxt] = current
        current = nxt
        if current == goal:
            break

    return _reconstruct(parents, current), expanded


class StochasticHillClimbingController(BaseController):
    ALGO_NAME = "Stochastic Hill Climbing"
    SUBTITLE = "Stochastic Hill Climbing — chọn ngẫu nhiên neighbor cải thiện"
    GROUPS = SHC_MANHATTAN_MISPLACED_GROUPS
    THEME = {
        "BG": "#0f1814",
        "PANEL_BG": "#152620",
        "GRID_LINE": "#2d4a3d",
        "TILE_BG": "#1e3329",
        "TILE_FG": "#d4f5e4",
        "TILE_BORD": "#4ade80",
        "EMPTY_BG": "#0f1814",
        "EMPTY_BORD": "#2d4a3d",
        "HL_BG": "#1f5c42",
        "HL_FG": "#ffffff",
        "HL_BORD": "#4ade80",
        "SHADOW": "#08100c",
        "PRI_BG": "#4ade80",
        "PRI_FG": "#0f1814",
        "SEC_BG": "#152620",
        "SEC_FG": "#4ade80",
        "LABEL_FG": "#8fb9a8",
        "METRIC_BG": "#122018",
        "ABTN": "#34d399",
        "ABTN2": "#2d4a3d",
        "UI_BORD": "#4ade80",
    }

    def __init__(self, model: PuzzleModel):
        super().__init__(model)
        self.group = 1
        self.value_metric = ""

    def set_group(self, group: int) -> None:
        self.group = max(1, min(len(self.GROUPS), int(group)))

    @classmethod
    def subtitle_for_group(cls, group: int) -> str:
        return f"Stochastic — {hill_group_label(cls.GROUPS[group])}"

    def _value_key(self) -> str:
        return self.GROUPS[self.group]["value"]

    def solve(self) -> bool:
        start, goal = tuple(self.model.state), tuple(self.model.goal)
        self.value_metric = self._value_key()

        t0 = time.perf_counter()
        path, expanded = stochastic_hill_climbing(start, goal, self.value_metric)
        self.elapsed_ms = (time.perf_counter() - t0) * 1000
        self.nodes_visited = expanded
        self.solution_path = path

        return bool(path and path[-1] == goal)

    def get_summary(self) -> dict:
        summary = super().get_summary()
        summary["heuristic_group"] = self.group
        summary["value_metric"] = self.value_metric
        return summary
