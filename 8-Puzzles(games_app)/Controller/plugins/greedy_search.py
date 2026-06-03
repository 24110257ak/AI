import time
import heapq
from Model.puzzle_model import PuzzleModel
from Controller.base_controller import BaseController


class GreedySearchController(BaseController):

    ALGO_NAME = "Greedy Search"

    SUBTITLE = "Tìm kiếm tham lam — luôn chọn trạng thái có heuristic h(n) nhỏ nhất"

    THEME = {
        "BG": "#1a1a2e", "PANEL_BG": "#16213e", "GRID_LINE": "#0f3460",
        "TILE_BG": "#1a4a6b", "TILE_FG": "#e0e0e0", "TILE_BORD": "#e94560",
        "EMPTY_BG": "#1a1a2e", "EMPTY_BORD": "#0f3460",
        "HL_BG": "#e94560", "HL_FG": "#ffffff", "HL_BORD": "#ffffff",
        "SHADOW": "#0d0d1a", "PRI_BG": "#e94560", "PRI_FG": "#ffffff",
        "SEC_BG": "#16213e", "SEC_FG": "#e94560", "LABEL_FG": "#7a7a9a",
        "METRIC_BG": "#0f0f1f", "ABTN": "#c73652", "ABTN2": "#1a1a2e"
    }

    # ------------------------------------------------------------------
    # Heuristic: Manhattan Distance
    # Tổng khoảng cách Manhattan của mỗi ô so với vị trí đích
    # ------------------------------------------------------------------
    @staticmethod
    def _manhattan(state: tuple, goal: tuple) -> int:
        distance = 0
        size = 3
        for tile in range(1, size * size):          # bỏ qua ô trống (0)
            si = state.index(tile)
            gi = goal.index(tile)
            distance += abs(si // size - gi // size) + abs(si % size - gi % size)
        return distance

    # ------------------------------------------------------------------
    # Sinh các trạng thái con (neighbor) hợp lệ
    # ------------------------------------------------------------------
    @staticmethod
    def _neighbors(state: tuple):
        neighbors = []
        size = 3
        zero = state.index(0)
        r, c = divmod(zero, size)
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < size and 0 <= nc < size:
                new_idx = nr * size + nc
                lst = list(state)
                lst[zero], lst[new_idx] = lst[new_idx], lst[zero]
                neighbors.append(tuple(lst))
        return neighbors

    # ------------------------------------------------------------------
    # Greedy Best-First Search
    # ------------------------------------------------------------------
    def solve(self):
        start = tuple(self.model.state)
        goal  = tuple(self.model.goal)
        t0    = time.perf_counter()

        # Mỗi phần tử trong heap: (h(n), tie_breaker, state)
        counter   = 0
        h_start   = self._manhattan(start, goal)
        frontier  = [(h_start, counter, start)]   # min-heap theo h(n)
        heapq.heapify(frontier)

        reached  = set()          # tập trạng thái đã xét
        parent   = {start: None}  # để truy vết đường đi
        total_nodes = 0

        is_success = False
        final_state = None

        while frontier:
            h_val, _, current = heapq.heappop(frontier)

            # ── Bước b: kiểm tra đích ──────────────────────────────────
            if current == goal:
                is_success  = True
                final_state = current
                break

            # ── Bước c: thêm vào reached ──────────────────────────────
            if current in reached:
                continue
            reached.add(current)
            total_nodes += 1

            # ── Bước d: mở rộng các trạng thái con ────────────────────
            for neighbor in self._neighbors(current):
                if neighbor not in reached and neighbor not in {s for _, _, s in frontier}:
                    parent[neighbor] = current
                    h_n = self._manhattan(neighbor, goal)
                    counter += 1
                    heapq.heappush(frontier, (h_n, counter, neighbor))

        # ------------------------------------------------------------------
        # Truy vết đường đi từ goal về start
        # ------------------------------------------------------------------
        elapsed = (time.perf_counter() - t0) * 1000

        if is_success:
            path = []
            node = final_state
            while node is not None:
                path.append(list(node))
                node = parent[node]
            path.reverse()

            self.solution_path = path
            self.nodes_visited  = total_nodes
            self.elapsed_ms     = elapsed
            return True
        else:
            self.solution_path = []
            self.nodes_visited  = total_nodes
            self.elapsed_ms     = elapsed
            return False