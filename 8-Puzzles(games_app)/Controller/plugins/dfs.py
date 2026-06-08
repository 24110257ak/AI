import time
from Model.puzzle_model import PuzzleModel
from Controller.base_controller import BaseController

class DFSController(BaseController):
    ALGO_NAME = "DFS"
    SUBTITLE = "Depth-First Search — KHÔNG đảm bảo lời giải ngắn nhất"
    THEME = {
        "BG": "#0f0a00", "PANEL_BG": "#1a1200", "GRID_LINE": "#2a1f00",
        "TILE_BG": "#1c1400", "TILE_FG": "#ffaa00", "TILE_BORD": "#ffaa00",
        "EMPTY_BG": "#0f0a00", "EMPTY_BORD": "#2a1f00",
        "HL_BG": "#2a0d00", "HL_FG": "#ff4500", "HL_BORD": "#ff4500",
        "SHADOW": "#1a0a00", "PRI_BG": "#ffaa00", "PRI_FG": "#0f0a00",
        "SEC_BG": "#1a1200", "SEC_FG": "#ffaa00", "LABEL_FG": "#c8860a",
        "METRIC_BG": "#120d00", "ABTN": "#cc8800", "ABTN2": "#2a1f00"
    }

    def __init__(self, model):
        super().__init__(model)
        self.depth_limit = 50  # Có thể thay đổi động từ View

    def solve(self):
        start, goal = self.model.state, self.model.goal
        t0 = time.perf_counter()
        
        if start == goal:
            self.solution_path, self.nodes_visited = [start], 1
            self.elapsed_ms = (time.perf_counter() - t0) * 1000
            return True

        stack, nodes = [(start, [start], {start})], 1
        while stack:
            state, path, visited = stack.pop()
            if len(path) > self.depth_limit:
                continue
            blank = state.index(0)
            for m in PuzzleModel.get_moves(state):
                nxt = PuzzleModel.swap(state, blank, m)
                if nxt not in visited:
                    nodes += 1
                    new_path = path + [nxt]
                    if nxt == goal:
                        self.solution_path = new_path
                        self.nodes_visited = nodes
                        self.elapsed_ms = (time.perf_counter() - t0) * 1000
                        return True
                    stack.append((nxt, new_path, visited | {nxt}))

        self.solution_path, self.nodes_visited = [], nodes
        self.elapsed_ms = (time.perf_counter() - t0) * 1000
        return False