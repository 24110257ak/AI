"""
Uniform Cost Search (UCS) cho bài toán 8-Puzzle.

Cost dùng trong app (sau khi so sánh C1 vs C2): **misplaced tiles**
  — mỗi nước đi có cost = số ô sai của trạng thái sau khi di chuyển (không tính ô 0).

Chạy demo:
    python -m Controller.plugins.ucs
"""

import heapq
import time
from typing import Dict, List, Optional, Tuple

from Model.puzzle_model import PuzzleModel, GRID_SIZE
from Controller.base_controller import BaseController

# Trạng thái dạng tuple 9 phần tử (hashable) — tương thích Model hiện tại
State = Tuple[int, ...]

# ── Chuyển đổi biểu diễn 2D ↔ tuple ─────────────────────────────────────────

def list2d_to_tuple(grid: List[List[int]]) -> State:
    """Chuyển ma trận 3x3 thành tuple phẳng (row-major)."""
    return tuple(grid[r][c] for r in range(GRID_SIZE) for c in range(GRID_SIZE))


def tuple_to_list2d(state: State) -> List[List[int]]:
    """Chuyển tuple phẳng thành ma trận 3x3."""
    return [
        [state[r * GRID_SIZE + c] for c in range(GRID_SIZE)]
        for r in range(GRID_SIZE)
    ]


# ── Tiện ích trạng thái ─────────────────────────────────────────────────────

def find_blank(state: State) -> int:
    """Trả về chỉ số (0–8) của ô trống trong tuple."""
    return state.index(0)


def get_neighbors(state: State) -> List[Tuple[State, str]]:
    """
    Sinh các trạng thái kế tiếp hợp lệ.
    Trả về danh sách (next_state, action) với action ∈ {Up, Down, Left, Right}
    (hướng di chuyển của ô trống).
    """
    blank = find_blank(state)
    r, c = divmod(blank, GRID_SIZE)
    neighbors = []

    # (delta_index, tên hướng)
    moves = []
    if r > 0:
        moves.append((-GRID_SIZE, "Up"))
    if r < GRID_SIZE - 1:
        moves.append((GRID_SIZE, "Down"))
    if c > 0:
        moves.append((-1, "Left"))
    if c < GRID_SIZE - 1:
        moves.append((1, "Right"))

    for delta, action in moves:
        nxt_idx = blank + delta
        nxt = PuzzleModel.swap(state, blank, nxt_idx)
        neighbors.append((nxt, action))

    return neighbors


# ── Misplaced tiles cost (luật cost duy nhất trong app) ───────────────────────

def count_misplaced(state: State, goal: State) -> int:
    """
    Đếm số ô sai so với goal (bỏ qua ô trống 0).
    """
    return sum(
        1 for i in range(len(state))
        if state[i] != 0 and state[i] != goal[i]
    )


def get_misplaced_cost(next_state: State, goal: State) -> int:
    """Chi phí một nước đi (C2) = số ô sai của trạng thái sau khi di chuyển."""
    return count_misplaced(next_state, goal)


# ── Lấy chi phí cạnh theo chế độ ────────────────────────────────────────────

def get_step_cost(nxt: State, goal: State) -> int:
    """Chi phí cạnh UCS: misplaced tiles của trạng thái sau nước đi."""
    return get_misplaced_cost(nxt, goal)


# ── UCS core ──────────────────────────────────────────────────────────────────

def reconstruct_path(
    came_from: Dict[State, Tuple[State, str]],
    start: State,
    goal: State,
) -> Tuple[List[State], List[str]]:
    """
    Dựng lại đường đi từ came_from.
    Trả về (danh_sách_trạng_thái, danh_sách_hướng_đi).
    """
    path = [goal]
    actions: List[str] = []
    cur = goal
    while cur != start:
        prev, action = came_from[cur]
        actions.append(action)
        path.append(prev)
        cur = prev
    path.reverse()
    actions.reverse()
    return path, actions


def uniform_cost_search(
    start: State,
    goal: State,
    cost_mode: str = "misplaced",
) -> Tuple[Optional[List[State]], int, int, List[str]]:
    """
    Uniform Cost Search dùng heapq.

    Trả về:
        path        — danh sách trạng thái từ start → goal (None nếu thất bại)
        total_cost  — tổng chi phí g(n) tại goal
        nodes_expanded — số node đã expand (lấy ra khỏi hàng đợi)
        actions     — dãy nước đi Up/Down/Left/Right
    """
    if start == goal:
        return [start], 0, 1, []

    # (priority, counter, state) — counter tránh so sánh tuple khi priority bằng nhau
    counter = 0
    frontier: List[Tuple[int, int, State]] = []
    heapq.heappush(frontier, (0, counter, start))

    cost_so_far: Dict[State, int] = {start: 0}
    came_from: Dict[State, Tuple[State, str]] = {}
    nodes_expanded = 0

    while frontier:
        _, _, current = heapq.heappop(frontier)
        nodes_expanded += 1

        if current == goal:
            path, actions = reconstruct_path(came_from, start, goal)
            return path, cost_so_far[goal], nodes_expanded, actions

        for nxt, action in get_neighbors(current):
            if cost_mode != "misplaced":
                raise ValueError(f"App chi ho tro cost_mode='misplaced', nhan: {cost_mode!r}")
            step = get_step_cost(nxt, goal)
            new_cost = cost_so_far[current] + step

            if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                cost_so_far[nxt] = new_cost
                came_from[nxt] = (current, action)
                counter += 1
                heapq.heappush(frontier, (new_cost, counter, nxt))

    return None, 0, nodes_expanded, []


# ── In kết quả (CLI / demo) ───────────────────────────────────────────────────

def format_state(state: State) -> str:
    """In ma trận 3x3 đẹp mắt."""
    grid = tuple_to_list2d(state)
    lines = []
    for row in grid:
        cells = " ".join(f"{v:2d}" if v != 0 else " _" for v in row)
        lines.append(f"  [{cells}]")
    return "\n".join(lines)


def print_solution(
    path: List[State],
    total_cost: int,
    nodes_expanded: int,
    actions: List[str],
    cost_mode: str,
) -> None:
    """In day du ket qua ra console (ASCII-safe cho Windows terminal)."""
    mode_label = "Misplaced tiles" if cost_mode == "misplaced" else cost_mode
    print("=" * 52)
    print(f"  UCS  |  {mode_label}")
    print("=" * 52)
    print(f"\nSo buoc trang thai : {len(path)}")
    print(f"Tong chi phi (g)   : {total_cost}")
    print(f"So node expand     : {nodes_expanded}")
    arrow = " -> ".join(actions) if actions else "(da o goal)"
    print(f"Day nuoc di        : {arrow}")

    print("\n-- Duong di tung buoc --")
    for i, st in enumerate(path):
        print(f"\nBuoc {i}:")
        print(format_state(st))


# ── Controller plugin (tích hợp MVC) ─────────────────────────────────────────

class UCSController(BaseController):
    """
    UCS — cost = số ô sai (misplaced tiles) của trạng thái sau mỗi nước đi.
    (Giữ bản này sau so sánh: ít node expand & nhanh hơn UCS-C1 dynamic.)
    """

    ALGO_NAME = "UCS"
    SUBTITLE = "Uniform Cost Search — cost = số ô sai (misplaced tiles)"
    COST_MODE = "misplaced"
    THEME = {
        "BG": "#1a0010", "PANEL_BG": "#2a0018", "GRID_LINE": "#4d0030",
        "TILE_BG": "#35102a", "TILE_FG": "#ff4d88", "TILE_BORD": "#ff4d88",
        "EMPTY_BG": "#1a0010", "EMPTY_BORD": "#4d0030",
        "HL_BG": "#4a0028", "HL_FG": "#ff99bb", "HL_BORD": "#ff99bb",
        "SHADOW": "#0d0008", "PRI_BG": "#ff4d88", "PRI_FG": "#1a0010",
        "SEC_BG": "#2a0018", "SEC_FG": "#ff4d88", "LABEL_FG": "#bf6b8a",
        "METRIC_BG": "#200014", "ABTN": "#cc3d6a", "ABTN2": "#4d0030",
    }

    def __init__(self, model: PuzzleModel):
        super().__init__(model)
        self.total_cost = 0
        self.actions: List[str] = []

    def solve(self) -> bool:
        start, goal = self.model.state, self.model.goal
        t0 = time.perf_counter()

        path, total_cost, nodes_expanded, actions = uniform_cost_search(
            start, goal, self.COST_MODE
        )

        self.elapsed_ms = (time.perf_counter() - t0) * 1000
        self.nodes_visited = nodes_expanded
        self.total_cost = total_cost
        self.actions = actions

        if path:
            self.solution_path = path
            return True

        self.solution_path = []
        return False

    def get_summary(self) -> dict:
        summary = super().get_summary()
        summary["total_cost"] = self.total_cost
        summary["actions"] = " ".join(self.actions)
        return summary


# ── Demo CLI với start/goal mẫu của đề bài ───────────────────────────────────

if __name__ == "__main__":
    START_2D = [
        [1, 2, 3],
        [4, 0, 6],
        [7, 5, 8],
    ]
    GOAL_2D = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 0],
    ]

    start = list2d_to_tuple(START_2D)
    goal = list2d_to_tuple(GOAL_2D)

    print("\n>>> START:")
    print(format_state(start))
    print("\n>>> GOAL:")
    print(format_state(goal))

    path, cost, expanded, actions = uniform_cost_search(start, goal, "misplaced")
    if path:
        print_solution(path, cost, expanded, actions, "misplaced")
    else:
        print(f"\nKhong tim thay loi giai. Node expand: {expanded}")
