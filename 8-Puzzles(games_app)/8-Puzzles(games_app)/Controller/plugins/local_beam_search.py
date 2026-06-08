"""Local Beam Search cho 8-puzzle (Value = Manhattan)."""

import time
import random
from typing import Dict, List, Optional, Tuple

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


def local_beam_search(
    start: State,
    goal: State,
    value_key: str,
    beam_width: int = 5,
    max_iterations: int = 500,
) -> Tuple[List[State], int]:
    """
    Local Beam Search:
    - Giữ k trạng thái (beam) có Value cao nhất
    - Mỗi vòng: mở rộng mọi beam, gom neighbor, giữ k trạng thái tốt nhất
    """
    value_fn = HEURISTIC_FNS[value_key]
    k = max(1, beam_width)
    expanded = 0

    def score(state: State) -> int:
        return -value_fn(state, goal)

    parents: Dict[State, Optional[State]] = {start: None}
    beams: List[State] = [start]
    cur = start
    for _ in range(k - 1):
        nxts = list(get_neighbors(cur))
        if not nxts:
            break
        cur = random.choice(nxts)
        parents[cur] = start
        beams.append(cur)

    if start == goal:
        return [start], expanded

    for _ in range(max_iterations):
        if goal in beams:
            break

        candidates: List[Tuple[State, State]] = []
        for state in beams:
            expanded += 1
            for nxt in get_neighbors(state):
                candidates.append((nxt, state))

        if not candidates:
            break

        best_by_state: Dict[State, Tuple[State, State]] = {}
        for nxt, parent in candidates:
            if nxt not in best_by_state or score(nxt) > score(best_by_state[nxt][0]):
                best_by_state[nxt] = (nxt, parent)

        ranked = sorted(best_by_state.values(), key=lambda pair: score(pair[0]), reverse=True)
        new_beams = [nxt for nxt, _ in ranked[:k]]

        if set(new_beams) == set(beams):
            break

        for nxt, parent in ranked[:k]:
            if nxt not in parents:
                parents[nxt] = parent
        beams = new_beams

    end = goal if goal in beams else max(beams, key=score)
    return _reconstruct(parents, end), expanded


class LocalBeamSearchController(BaseController):
    ALGO_NAME = "Local Beam Search"
    SUBTITLE = "Local Beam Search — giữ k trạng thái tốt nhất theo Value(n)"
    GROUPS = SHC_MANHATTAN_MISPLACED_GROUPS
    THEME = {
        "BG": "#0f141a",
        "PANEL_BG": "#151d26",
        "GRID_LINE": "#2d3f55",
        "TILE_BG": "#1e2a38",
        "TILE_FG": "#d4e8ff",
        "TILE_BORD": "#38bdf8",
        "EMPTY_BG": "#0f141a",
        "EMPTY_BORD": "#2d3f55",
        "HL_BG": "#1f4a6b",
        "HL_FG": "#ffffff",
        "HL_BORD": "#38bdf8",
        "SHADOW": "#080c12",
        "PRI_BG": "#38bdf8",
        "PRI_FG": "#0f141a",
        "SEC_BG": "#151d26",
        "SEC_FG": "#38bdf8",
        "LABEL_FG": "#94b4d4",
        "METRIC_BG": "#121a22",
        "ABTN": "#0ea5e9",
        "ABTN2": "#2d3f55",
        "UI_BORD": "#38bdf8",
    }

    def __init__(self, model: PuzzleModel):
        super().__init__(model)
        self.group = 1
        self.value_metric = ""
        self.beam_width = 5

    def set_group(self, group: int) -> None:
        self.group = max(1, min(len(self.GROUPS), int(group)))

    @classmethod
    def subtitle_for_group(cls, group: int, beam_width: int = 5) -> str:
        return f"Local Beam (k={beam_width}) — {hill_group_label(cls.GROUPS[group])}"

    def _value_key(self) -> str:
        return self.GROUPS[self.group]["value"]

    def solve(self) -> bool:
        start, goal = tuple(self.model.state), tuple(self.model.goal)
        self.value_metric = self._value_key()

        t0 = time.perf_counter()
        path, expanded = local_beam_search(
            start, goal, self.value_metric, beam_width=self.beam_width
        )
        self.elapsed_ms = (time.perf_counter() - t0) * 1000
        self.nodes_visited = expanded
        self.solution_path = path

        return bool(path and path[-1] == goal)

    def get_summary(self) -> dict:
        summary = super().get_summary()
        summary["heuristic_group"] = self.group
        summary["value_metric"] = self.value_metric
        summary["beam_width"] = self.beam_width
        return summary
