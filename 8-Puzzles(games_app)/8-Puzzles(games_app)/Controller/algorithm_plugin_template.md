# Algorithm Plugin Template

import time
from Model.puzzle_model import PuzzleModel
from Controller.base_controller import BaseController

<!-- Bạn chỉ cần đổi tên lớp này thành tên thuật toán của bạn -->

class MyNewAlgoController(BaseController):

    # 1. Điền tên hiển thị trên nút bấm giao diện
    ALGO_NAME = "TEN_THUAT_TOAN_MOI" 
    
    # 2. Điền dòng chữ mô tả thuật toán
    SUBTITLE = "Thuật toán này giúp giải bài toán bằng cách..."
    
    # 3. Thích giao diện màu gì thì tự chỉnh mã màu HEX ở đây
    # Khi chọn thuật toán này, toàn bộ giao diện game sẽ tự đổi sang màu này!
    THEME = {
        "BG": "#2b2b2b", "PANEL_BG": "#3c3f41", "GRID_LINE": "#555555",
        "TILE_BG": "#4b5052", "TILE_FG": "#a9b7c6", "TILE_BORD": "#a9b7c6",
        "EMPTY_BG": "#2b2b2b", "EMPTY_BORD": "#555555",
        "HL_BG": "#214283", "HL_FG": "#ffffff", "HL_BORD": "#ffffff",
        "SHADOW": "#1e1e1e", "PRI_BG": "#cc7832", "PRI_FG": "#2b2b2b",
        "SEC_BG": "#3c3f41", "SEC_FG": "#cc7832", "LABEL_FG": "#808080",
        "METRIC_BG": "#323232", "ABTN": "#b36829", "ABTN2": "#2b2b2b"
    }

    def solve(self):
        """
        Nơi bạn viết logic thuật toán giải 8-puzzle của bạn.
        """
        start = self.model.state  # Trạng thái hiện tại của bàn cờ
        goal = self.model.goal    # Trạng thái đích cần đạt được
        t0 = time.perf_counter()
        
        # ====================================================
        # BẠN VIẾT CODE THUẬT TOÁN CỦA BẠN Ở ĐÂY...
        # ====================================================
        
        # Sau khi thuật toán chạy xong, bạn gán kết quả vào đây:
        is_success = True # Đổi thành True nếu giải được, False nếu thất bại
        path = [start, goal] # Thay bằng danh sách các bước đi thực tế từ start đến goal
        total_nodes = 100 # Thay bằng số lượng node thực tế mà thuật toán đã duyệt
        
        # 4. Trả kết quả về cho giao diện hiển thị
        if is_success:
            self.solution_path = path
            self.nodes_visited = total_nodes
            self.elapsed_ms = (time.perf_counter() - t0) * 1000
            return True
        else:
            self.solution_path = []
            self.nodes_visited = total_nodes
            self.elapsed_ms = (time.perf_counter() - t0) * 1000
            return False
