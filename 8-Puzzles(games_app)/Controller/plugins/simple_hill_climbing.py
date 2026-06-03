"""Simple Hill Climbing cho 8-puzzle."""

import time
import random
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


def simple_hill_climbing(start: State, goal: State, value_key: str) -> Tuple[List[State], int]:
    """
    Simple (first-improvement) Hill Climbing:
    - Duyệt neighbor, chọn neighbor đầu tiên có Value tốt hơn Current
    - Dừng khi không còn neighbor tốt hơn (local maximum)
    """
    value_fn = HEURISTIC_FNS[value_key]
    parents = {start: None}
    current = start
    expanded = 0

    def score(state: State) -> int:
        # Hill climbing cần "lớn hơn là tốt hơn", còn heuristic càng nhỏ càng tốt.
        # Đảo dấu để thống nhất điều kiện Value(next) > Value(current).
        return -value_fn(state, goal)

    if current == goal:
        return [current], expanded

    while True:
        expanded += 1
        cur_score = score(current)
        moved = False
        for nxt in get_neighbors(current):
            if score(nxt) > cur_score:
                parents[nxt] = current
                current = nxt
                moved = True
                break
        if current == goal:
            break
        if not moved:
            break

    return _reconstruct(parents, current), expanded


class SimpleHillClimbingController(BaseController):
    ALGO_NAME = "Simple Hill Climbing"
    SUBTITLE = "Simple Hill Climbing — first-improvement + random restart"
    GROUPS = SHC_GROUPS
    THEME = {
        "BG": "#101218",
        "PANEL_BG": "#171b24",
        "GRID_LINE": "#2b3445",
        "TILE_BG": "#202938",
        "TILE_FG": "#dbe7ff",
        "TILE_BORD": "#8ab4ff",
        "EMPTY_BG": "#101218",
        "EMPTY_BORD": "#2b3445",
        "HL_BG": "#254470",
        "HL_FG": "#ffffff",
        "HL_BORD": "#8ab4ff",
        "SHADOW": "#0a0c11",
        "PRI_BG": "#8ab4ff",
        "PRI_FG": "#101218",
        "SEC_BG": "#171b24",
        "SEC_FG": "#8ab4ff",
        "LABEL_FG": "#96a4bf",
        "METRIC_BG": "#151a23",
        "ABTN": "#6ea2ff",
        "ABTN2": "#2b3445",
        "UI_BORD": "#8ab4ff",
    }

    def __init__(self, model: PuzzleModel):
        super().__init__(model)
        self.group = 1
        self.value_metric = ""
        self.max_restarts = 20
        self.restart_walk_steps = 12

    def set_group(self, group: int) -> None:
        self.group = max(1, min(3, int(group)))

    @classmethod
    def subtitle_for_group(cls, group: int) -> str:
        return f"Simple Hill Climbing — {hill_group_label(cls.GROUPS[group])}"

    def _value_key(self) -> str:
        return self.GROUPS[self.group]["value"]

    def solve(self) -> bool:
        start, goal = tuple(self.model.state), tuple(self.model.goal)
        self.value_metric = self._value_key()
        value_fn = HEURISTIC_FNS[self.value_metric]

        def seed_state(base: State) -> State:
            cur = base
            for _ in range(self.restart_walk_steps):
                nxts = list(get_neighbors(cur))
                if not nxts:
                    break
                cur = random.choice(nxts)
            return cur

        t0 = time.perf_counter()
        best_path: List[State] = []
        best_score = -10**9
        expanded_sum = 0

        seeds = [start]
        seeds.extend(seed_state(start) for _ in range(self.max_restarts))

        for seed in seeds:
            path, expanded = simple_hill_climbing(seed, goal, self.value_metric)
            expanded_sum += expanded
            end_state = path[-1]
            end_score = -value_fn(end_state, goal)
            if end_score > best_score:
                best_score = end_score
                best_path = path
            if end_state == goal:
                best_path = path
                break

        self.elapsed_ms = (time.perf_counter() - t0) * 1000
        self.nodes_visited = expanded_sum
        self.solution_path = best_path

        return bool(best_path and best_path[-1] == goal)

    def get_summary(self) -> dict:
        summary = super().get_summary()
        summary["heuristic_group"] = self.group
        summary["value_metric"] = self.value_metric
        return summary
