"""Random-Restart Hill Climbing cho 8-puzzle (Value = Manhattan)."""

import time
import random
from typing import List, Tuple

from Controller.base_controller import BaseController
from Controller.heuristics import (
    HEURISTIC_FNS,
    SHC_MANHATTAN_MISPLACED_GROUPS,
    State,
    get_neighbors,
    hill_group_label,
)
from Controller.plugins.steepest_ascent_hill_climbing import steepest_ascent_hill_climbing
from Model.puzzle_model import PuzzleModel


class RandomRestartHillClimbingController(BaseController):
    ALGO_NAME = "Random-Restart Hill Climbing"
    SUBTITLE = "Random-Restart — Steepest-Ascent + khởi động lại ngẫu nhiên"
    GROUPS = SHC_MANHATTAN_MISPLACED_GROUPS
    THEME = {
        "BG": "#1a140f",
        "PANEL_BG": "#261c14",
        "GRID_LINE": "#4a3828",
        "TILE_BG": "#332618",
        "TILE_FG": "#ffe8d4",
        "TILE_BORD": "#fb923c",
        "EMPTY_BG": "#1a140f",
        "EMPTY_BORD": "#4a3828",
        "HL_BG": "#6b3f1f",
        "HL_FG": "#ffffff",
        "HL_BORD": "#fb923c",
        "SHADOW": "#100c08",
        "PRI_BG": "#fb923c",
        "PRI_FG": "#1a140f",
        "SEC_BG": "#261c14",
        "SEC_FG": "#fb923c",
        "LABEL_FG": "#c4a894",
        "METRIC_BG": "#201810",
        "ABTN": "#f97316",
        "ABTN2": "#4a3828",
        "UI_BORD": "#fb923c",
    }

    def __init__(self, model: PuzzleModel):
        super().__init__(model)
        self.group = 1
        self.value_metric = ""
        self.max_restarts = 30
        self.restart_walk_steps = 15

    def set_group(self, group: int) -> None:
        self.group = max(1, min(len(self.GROUPS), int(group)))

    @classmethod
    def subtitle_for_group(cls, group: int) -> str:
        return f"Random-Restart — {hill_group_label(cls.GROUPS[group])}"

    def _value_key(self) -> str:
        return self.GROUPS[self.group]["value"]

    def _perturbed_start(self, base: State) -> State:
        cur = base
        for _ in range(self.restart_walk_steps):
            nxts = list(get_neighbors(cur))
            if not nxts:
                break
            cur = random.choice(nxts)
        return cur

    def solve(self) -> bool:
        start, goal = tuple(self.model.state), tuple(self.model.goal)
        self.value_metric = self._value_key()
        value_fn = HEURISTIC_FNS[self.value_metric]

        t0 = time.perf_counter()
        best_path: List[State] = []
        best_score = -10**9
        expanded_sum = 0

        seeds = [start]
        seeds.extend(self._perturbed_start(start) for _ in range(self.max_restarts))

        for seed in seeds:
            path, expanded = steepest_ascent_hill_climbing(seed, goal, self.value_metric)
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
