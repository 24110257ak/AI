import time
from collections import deque
from Model.puzzle_model import PuzzleModel
from Controller.base_controller import BaseController

class BFSController(BaseController):
    ALGO_NAME = "BFS"
    SUBTITLE = "Breadth-First Search — Đảm bảo lời giải NGẮN NHẤT"
    THEME = {
        "BG": "#0a0f1d", "PANEL_BG": "#0e1525", "GRID_LINE": "#1a2540",
        "TILE_BG": "#111c35", "TILE_FG": "#00f0ff", "TILE_BORD": "#00f0ff",
        "EMPTY_BG": "#0a0f1d", "EMPTY_BORD": "#1a2540",
        "HL_BG": "#1a003a", "HL_FG": "#ff007f", "HL_BORD": "#ff007f",
        "SHADOW": "#001a33", "PRI_BG": "#00f0ff", "PRI_FG": "#0a0f1d",
        "SEC_BG": "#0e1525", "SEC_FG": "#00f0ff", "LABEL_FG": "#7ab8d4",
        "METRIC_BG": "#0b1220", "ABTN": "#00c8d4", "ABTN2": "#1a2a44"
    }

    def solve(self):
        start, goal = self.model.state, self.model.goal
        t0 = time.perf_counter()
        
        if start == goal:
            self.solution_path, self.nodes_visited = [start], 1
            self.elapsed_ms = (time.perf_counter() - t0) * 1000
            return True

        queue, visited, nodes = deque([(start, [start])]), {start}, 1
        while queue:
            state, path = queue.popleft()
            blank = state.index(0)
            for m in PuzzleModel.get_moves(state):
                nxt = PuzzleModel.swap(state, blank, m)
                if nxt not in visited:
                    visited.add(nxt)
                    nodes += 1
                    new_path = path + [nxt]
                    if nxt == goal:
                        self.solution_path = new_path
                        self.nodes_visited = nodes
                        self.elapsed_ms = (time.perf_counter() - t0) * 1000
                        return True
                    queue.append((nxt, new_path))
        
        self.solution_path, self.nodes_visited = [], nodes
        self.elapsed_ms = (time.perf_counter() - t0) * 1000
        return False