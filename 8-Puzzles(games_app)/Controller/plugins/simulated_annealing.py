import time
import math
import random
from Model.puzzle_model import PuzzleModel
from Controller.base_controller import BaseController
from Controller.heuristics import manhattan # Có thể dùng heuristic mặc định là Manhattan

class SimulatedAnnealingController(BaseController):
    ALGO_NAME = "Simulated Annealing"
    SUBTITLE = "Mô phỏng luyện kim: Chấp nhận bước đi lùi dựa trên nhiệt độ (T)"
    
    THEME = {
        "BG": "#1e1e1e", "PANEL_BG": "#252526", "GRID_LINE": "#333333",
        "TILE_BG": "#dcdcaa", "TILE_FG": "#1e1e1e", "TILE_BORD": "#dcdcaa",
        "EMPTY_BG": "#1e1e1e", "EMPTY_BORD": "#333333",
        "HL_BG": "#c586c0", "HL_FG": "#ffffff", "HL_BORD": "#ffffff",
        "SHADOW": "#000000", "PRI_BG": "#ce9178", "PRI_FG": "#1e1e1e",
        "SEC_BG": "#2d2d30", "SEC_FG": "#ce9178", "LABEL_FG": "#858585",
        "METRIC_BG": "#252526", "ABTN": "#b5cea8", "ABTN2": "#1e1e1e"
    }

    def solve(self):
        start = self.model.state
        goal = self.model.goal
        t0 = time.perf_counter()
        
        current_state = start
        current_h = manhattan(current_state, goal)
        
        self.solution_path = [current_state]
        self.nodes_visited = 1
        
        # Tham số cấu hình Luyện kim
        T = 100.0          # Nhiệt độ ban đầu
        cooling_rate = 0.99 # Tốc độ làm lạnh
        min_T = 0.001      # Nhiệt độ tối thiểu để dừng
        
        is_success = False
        
        while T > min_T:
            if current_h == 0:
                is_success = True
                break
                
            moves = self.model.get_moves(current_state)
            blank_idx = self.model.find_blank(current_state)
            
            # Chọn ngẫu nhiên 1 trạng thái kề (neighbor)
            random_move = random.choice(moves)
            neighbor = self.model.swap(current_state, blank_idx, random_move)
            self.nodes_visited += 1
            
            neighbor_h = manhattan(neighbor, goal)
            
            # Tính Delta E (lưu ý: Heuristic càng nhỏ càng tốt, nên Delta E > 0 là tốt)
            delta_e = current_h - neighbor_h 
            
            # Nếu neighbor tốt hơn, HOẶC tồi hơn nhưng thỏa mãn xác suất nhiệt độ
            if delta_e > 0 or random.random() < math.exp(delta_e / T):
                current_state = neighbor
                current_h = neighbor_h
                self.solution_path.append(current_state)
            
            # Hạ nhiệt độ
            T *= cooling_rate

        self.elapsed_ms = (time.perf_counter() - t0) * 1000
        return is_success