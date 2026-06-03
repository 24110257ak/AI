import time
from Model.puzzle_model import PuzzleModel
from Controller.base_controller import BaseController

class IDSController(BaseController):
    ALGO_NAME = "IDS"
    SUBTITLE = "Iterative Deepening Search — Tiết kiệm bộ nhớ & Tối ưu đường đi"
    THEME = {
        "BG": "#130a1d", "PANEL_BG": "#1a0e25", "GRID_LINE": "#2e1a40",
        "TILE_BG": "#241135", "TILE_FG": "#bf00ff", "TILE_BORD": "#bf00ff",
        "EMPTY_BG": "#130a1d", "EMPTY_BORD": "#2e1a40",
        "HL_BG": "#3a0050", "HL_FG": "#ff00ff", "HL_BORD": "#ff00ff",
        "SHADOW": "#0a0015", "PRI_BG": "#bf00ff", "PRI_FG": "#130a1d",
        "SEC_BG": "#1a0e25", "SEC_FG": "#bf00ff", "LABEL_FG": "#a37ab8",
        "METRIC_BG": "#170c20", "ABTN": "#9900cc", "ABTN2": "#2e1a40"
    }

    def __init__(self, model):
        super().__init__(model)
        self.max_depth = 50

    def solve(self):
        start, goal = self.model.state, self.model.goal
        t0 = time.perf_counter()
        total_nodes = 0
        
        for depth in range(self.max_depth + 1):
            path, nodes = self._dls(start, goal, depth)
            total_nodes += nodes
            if path:
                self.solution_path = path
                self.nodes_visited = total_nodes
                self.elapsed_ms = (time.perf_counter() - t0) * 1000
                return True
                
        self.solution_path, self.nodes_visited = [], total_nodes
        self.elapsed_ms = (time.perf_counter() - t0) * 1000
        return False

    @staticmethod
    def _dls(start, goal, limit):
        if start == goal: return [start], 1
        stack, nodes = [(start, [start], {start})], 1
        while stack:
            state, path, visited = stack.pop()
            if len(path) - 1 < limit:
                blank = state.index(0)
                for m in reversed(PuzzleModel.get_moves(state)):
                    nxt = PuzzleModel.swap(state, blank, m)
                    if nxt not in visited:
                        nodes += 1
                        new_path = path + [nxt]
                        if nxt == goal: return new_path, nodes
                        stack.append((nxt, new_path, visited | {nxt}))
        return None, nodes