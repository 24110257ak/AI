"""
Heuristic và chi phí bước đi (g) cho A* / IDA*.

Khóa nội bộ: zero | misplaced | manhattan | inversions | swap
Nhãn UI:      rỗng | số ô sai | Manhattan | dãy ngược | swap
"""

from typing import Callable, Dict, Tuple

from Model.puzzle_model import GRID_SIZE, PuzzleModel

State = Tuple[int, ...]

LABELS: Dict[str, str] = {
    "zero": "rỗng",
    "misplaced": "số ô sai",
    "manhattan": "Manhattan",
    "inversions": "dãy ngược",
    "swap": "swap",
}


def count_misplaced(state: State, goal: State) -> int:
    return sum(1 for i in range(9) if state[i] != 0 and state[i] != goal[i])


def manhattan(state: State, goal: State) -> int:
    dist = 0
    for tile in range(1, GRID_SIZE * GRID_SIZE):
        si, gi = state.index(tile), goal.index(tile)
        dist += abs(si // GRID_SIZE - gi // GRID_SIZE) + abs(si % GRID_SIZE - gi % GRID_SIZE)
    return dist


def count_inversions(state: State, goal: State) -> int:
    """Số nghịch thế so với thứ tự ô trên goal (bỏ ô 0)."""
    goal_rank = {goal[i]: i for i in range(9)}
    seq = [goal_rank[v] for v in state if v != 0]
    inv = 0
    for i in range(len(seq)):
        for j in range(i + 1, len(seq)):
            if seq[i] > seq[j]:
                inv += 1
    return inv


def h_swap(state: State, goal: State) -> int:
    """Xung đột hàng: cặp ô cùng hàng nhưng sai thứ tự so với goal."""
    cost = 0
    for r in range(GRID_SIZE):
        row_vals = [state[r * GRID_SIZE + c] for c in range(GRID_SIZE) if state[r * GRID_SIZE + c] != 0]
        goal_row = [v for v in goal[r * GRID_SIZE : (r + 1) * GRID_SIZE] if v != 0]
        rank = {goal_row[i]: i for i in range(len(goal_row))}
        seq = [rank[t] for t in row_vals if t in rank]
        for i in range(len(seq)):
            for j in range(i + 1, len(seq)):
                if seq[i] > seq[j]:
                    cost += 1
    return cost


HEURISTIC_FNS: Dict[str, Callable[[State, State], int]] = {
    "zero": lambda _s, _g: 0,
    "misplaced": count_misplaced,
    "manhattan": manhattan,
    "inversions": count_inversions,
    "swap": h_swap,
}


def step_cost_zero(_cur: State, _nxt: State, _goal: State) -> int:
    return 1


def step_cost_metric(cur: State, nxt: State, goal: State, metric: str) -> int:
    if metric == "zero":
        return 1
    fn = HEURISTIC_FNS.get(metric, count_misplaced)
    return max(1, fn(nxt, goal))


STEP_COST_FNS: Dict[str, Callable[[State, State, State], int]] = {
    "zero": step_cost_zero,
    "misplaced": lambda c, n, g: step_cost_metric(c, n, g, "misplaced"),
    "manhattan": lambda c, n, g: step_cost_metric(c, n, g, "manhattan"),
    "inversions": lambda c, n, g: step_cost_metric(c, n, g, "inversions"),
    "swap": lambda c, n, g: step_cost_metric(c, n, g, "swap"),
}


# ── Preset nhóm (theo bảng đề) ───────────────────────────────────────────────

ASTAR_GROUPS: Dict[int, Dict[str, str]] = {
    1: {"h": "misplaced", "g": "inversions"},
    2: {"h": "swap", "g": "manhattan"},
    3: {"h": "manhattan", "g": "misplaced"},
}

IDA_GROUPS: Dict[int, Dict[str, str]] = {
    1: {"h": "misplaced", "g": "manhattan"},
    2: {"h": "inversions", "g": "misplaced"},
    3: {"h": "manhattan", "g": "manhattan"},
}

SHC_GROUPS: Dict[int, Dict[str, str]] = {
    1: {"value": "manhattan"},
    2: {"value": "misplaced"},
    3: {"value": "swap"},
}

# Stochastic / Random-Restart / Local Beam: Manhattan + số ô sai (theo đề)
SHC_MANHATTAN_MISPLACED_GROUPS: Dict[int, Dict[str, str]] = {
    1: {"value": "manhattan"},
    2: {"value": "misplaced"},
}


def group_label(group: Dict[str, str]) -> str:
    h = LABELS.get(group["h"], group["h"])
    g = LABELS.get(group["g"], group["g"])
    return f"h(n)={h}  |  g(n)={g}"


def hill_group_label(group: Dict[str, str]) -> str:
    key = group["value"]
    return f"Value(n)={LABELS.get(key, key)}"


def hill_group_button_text(group_num: int, groups: Dict[int, Dict[str, str]]) -> str:
    """Nhãn nút nhóm trên UI (vd. Manhattan, Số ô sai)."""
    key = groups[group_num]["value"]
    return LABELS.get(key, key)


def get_neighbors(state: State):
    blank = state.index(0)
    for nxt in PuzzleModel.get_moves(state):
        yield PuzzleModel.swap(state, blank, nxt)
