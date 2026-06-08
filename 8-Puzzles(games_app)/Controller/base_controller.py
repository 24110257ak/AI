from Model.puzzle_model import PuzzleModel

class BaseController:
    # Các thuộc tính bắt buộc phải ghi đè ở class con
    ALGO_NAME = "BASE"
    SUBTITLE = "Mô tả thuật toán"
    THEME = {}  # Bộ màu sắc của thuật toán khi hiển thị trên giao diện

    def __init__(self, model: PuzzleModel):
        self.model = model
        self.solution_path = []
        self.nodes_visited = 0
        self.elapsed_ms = 0.0

    def solve(self) -> bool:
        """Hàm thực thi thuật toán giải. Trả về True nếu thành công."""
        raise NotImplementedError("Bạn chưa viết hàm solve() cho thuật toán này!")

    def get_summary(self) -> dict:
        """Trả về thống kê kết quả."""
        return {
            "algorithm": self.ALGO_NAME,
            "steps": max(0, len(self.solution_path) - 1),
            "nodes_visited": self.nodes_visited,
            "elapsed_ms": self.elapsed_ms,
        }