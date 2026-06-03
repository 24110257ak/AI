"""
main.py — Entry point hoàn chỉnh
─────────────────────────────────
Kết nối Model, View và các Controller Plugin (BFS, DFS, IDS, UCS)
theo kiến trúc MVC động.
"""

import sys
from Model.puzzle_model import PuzzleModel, DEFAULT_GOAL
from Controller.plugins.bfs import BFSController
from Controller.plugins.dfs import DFSController
from Controller.plugins.ids import IDSController
from Controller.plugins.ucs import UCSController
from Controller.plugins.greedy_search import GreedySearchController
from Controller.plugins.astar import AStarController
from Controller.plugins.ida_star import IDAStarController
from Controller.plugins.simple_hill_climbing import SimpleHillClimbingController
from Controller.plugins.steepest_ascent_hill_climbing import SteepestAscentHillClimbingController
from Controller.plugins.stochastic_hill_climbing import StochasticHillClimbingController
from Controller.plugins.random_restart_hill_climbing import RandomRestartHillClimbingController
from Controller.plugins.local_beam_search import LocalBeamSearchController
from Controller.compare_algorithms import compare_all_algorithms
from View.puzzle_view import PuzzleView


def main():
    # ── 1. Chọn thuật toán mặc định từ tham số dòng lệnh ───────────────
    default_algo = "BFS"
    cli_aliases = {
        "BFS": "BFS",
        "DFS": "DFS",
        "IDS": "IDS",
        "UCS": "UCS",
        "A*": "A*",
        "IDA*": "IDA*",
        "GREEDY SEARCH": "Greedy Search",
        "SIMPLE HILL CLIMBING": "Simple Hill Climbing",
        "STEEPEST-ASCENT HILL CLIMBING": "Steepest-Ascent Hill Climbing",
        "STOCHASTIC HILL CLIMBING": "Stochastic Hill Climbing",
        "RANDOM-RESTART HILL CLIMBING": "Random-Restart Hill Climbing",
        "LOCAL BEAM SEARCH": "Local Beam Search",
    }
    if len(sys.argv) > 1:
        key = sys.argv[1].upper()
        if key in cli_aliases:
            default_algo = cli_aliases[key]

    # ── 2. Khởi tạo Model ───────────────────────────────────────────────
    model = PuzzleModel()

    # ── 3. Trích xuất Metadata tự động từ các Controller Plugins ───────
    # Giúp View nạp giao diện, màu sắc Cyberpunk độc bản của từng thuật toán một cách linh hoạt
    algos_metadata = {
        BFSController.ALGO_NAME: {
            "subtitle": BFSController.SUBTITLE,
            "theme": BFSController.THEME
        },
        DFSController.ALGO_NAME: {
            "subtitle": DFSController.SUBTITLE,
            "theme": DFSController.THEME
        },
        IDSController.ALGO_NAME: {
            "subtitle": IDSController.SUBTITLE,
            "theme": IDSController.THEME
        },
        UCSController.ALGO_NAME: {
            "subtitle": UCSController.SUBTITLE,
            "theme": UCSController.THEME
        },
        GreedySearchController.ALGO_NAME: {
            "subtitle": GreedySearchController.SUBTITLE,
            "theme": GreedySearchController.THEME
        },
        AStarController.ALGO_NAME: {
            "subtitle": AStarController.SUBTITLE,
            "theme": AStarController.THEME,
        },
        IDAStarController.ALGO_NAME: {
            "subtitle": IDAStarController.SUBTITLE,
            "theme": IDAStarController.THEME,
        },
        SimpleHillClimbingController.ALGO_NAME: {
            "subtitle": SimpleHillClimbingController.SUBTITLE,
            "theme": SimpleHillClimbingController.THEME,
        },
        SteepestAscentHillClimbingController.ALGO_NAME: {
            "subtitle": SteepestAscentHillClimbingController.SUBTITLE,
            "theme": SteepestAscentHillClimbingController.THEME,
        },
        StochasticHillClimbingController.ALGO_NAME: {
            "subtitle": StochasticHillClimbingController.SUBTITLE,
            "theme": StochasticHillClimbingController.THEME,
        },
        RandomRestartHillClimbingController.ALGO_NAME: {
            "subtitle": RandomRestartHillClimbingController.SUBTITLE,
            "theme": RandomRestartHillClimbingController.THEME,
        },
        LocalBeamSearchController.ALGO_NAME: {
            "subtitle": LocalBeamSearchController.SUBTITLE,
            "theme": LocalBeamSearchController.THEME,
        },
    }

    # ── 4. Khởi tạo cấu trúc Callbacks rỗng để liên kết View ───────────
    callbacks = {}
    view = PuzzleView(algos_metadata=algos_metadata, default_algo=default_algo, callbacks=callbacks)

    # ── 5. Quản lý danh sách các Bộ điều khiển (Controllers) ──────────
    controllers = {
        "BFS": BFSController(model),
        "DFS": DFSController(model),
        "IDS": IDSController(model),
        "UCS": UCSController(model),
        "Greedy Search": GreedySearchController(model),
        "A*": AStarController(model),
        "IDA*": IDAStarController(model),
        "Simple Hill Climbing": SimpleHillClimbingController(model),
        "Steepest-Ascent Hill Climbing": SteepestAscentHillClimbingController(model),
        "Stochastic Hill Climbing": StochasticHillClimbingController(model),
        "Random-Restart Hill Climbing": RandomRestartHillClimbingController(model),
        "Local Beam Search": LocalBeamSearchController(model),
    }

    # ── 6. Cài đặt chi tiết các hàm xử lý sự kiện (MVC Callbacks) ──────

    def on_solve(algo_name):
        """Được gọi khi người dùng nhấn nút SOLVE trên giao diện."""
        if view.is_sliding:
            return
        if model.is_goal():
            view.set_status("done", "Bàn cờ đang ở trạng thái đích (Goal) rồi!")
            return

        # Lấy bộ điều khiển tương ứng với thuật toán đang chọn trên UI
        current_controller = controllers.get(algo_name)
        if not current_controller:
            view.set_status("error", f"Lỗi: Không tìm thấy thuật toán {algo_name}")
            return

        # Cấu hình giới hạn độ sâu động dựa theo từng loại thuật toán đặc thù
        if isinstance(current_controller, DFSController):
            current_controller.depth_limit = view.get_depth_limit()
        elif isinstance(current_controller, IDSController):
            current_controller.max_depth = view.get_depth_limit()
        elif isinstance(
            current_controller,
            (
                AStarController,
                IDAStarController,
                SimpleHillClimbingController,
                SteepestAscentHillClimbingController,
                StochasticHillClimbingController,
                RandomRestartHillClimbingController,
                LocalBeamSearchController,
            ),
        ):
            current_controller.set_group(view.get_heuristic_group())

        # Hiển thị trạng thái đang tính toán lên màn hình
        view.set_status("computing", f"Đang thực thi giải thuật {algo_name}...")
        view.update_idletasks()

        # Tiến hành giải thuật toán
        success = current_controller.solve()
        summary = current_controller.get_summary()

        if success:
            # Gửi danh sách các bước đi và bảng thống kê hiệu năng sang cho View hiển thị
            view.show_solution(current_controller.solution_path, summary)
            if "total_cost" in summary:
                view.set_status(
                    "done",
                    f"Solved — {summary['steps']} moves, cost {summary['total_cost']}, "
                    f"{summary['elapsed_ms']:.0f} ms, {summary['algorithm']}",
                )
        else:
            limit_msg = " Thử tăng giới hạn độ sâu (Depth Limit) lên." if algo_name in ["DFS", "IDS"] else ""
            hill_algos = (
                "Simple Hill Climbing",
                "Steepest-Ascent Hill Climbing",
                "Stochastic Hill Climbing",
                "Random-Restart Hill Climbing",
                "Local Beam Search",
            )
            hill_msg = (
                " Thuật toán đã dừng ở cực đại cục bộ (local maximum)."
                if algo_name in hill_algos
                else ""
            )
            view.set_status("error", f"Không tìm thấy lời giải bằng {algo_name}.{limit_msg}{hill_msg}")

    def on_shuffle():
        """Được gọi khi người dùng nhấn nút SHUFFLE."""
        if view.is_sliding:
            return
        model.shuffle()
        view.clear_solution()
        view.draw_board(model.state)
        view.set_status("idle", "")
        # Đồng bộ hóa dữ liệu vừa xáo trộn vào hai ô văn bản nhập liệu phía dưới
        view.set_input_fields(model.state, model.goal)

    def on_reset():
        """Được gọi khi người dùng nhấn nút RESET."""
        if view.is_sliding:
            return
        model.reset()
        view.clear_solution()
        view.draw_board(model.state)
        view.set_status("idle", "")
        view.set_input_fields(model.state, model.goal)

    def on_tile_click(idx):
        """Được gọi khi người dùng click chuột trực tiếp để di chuyển ô số trên bàn cờ."""
        from Model.puzzle_model import PuzzleModel as PM
        blank = PM.find_blank(model.state)
        if idx in PM.get_moves(model.state):
            view.clear_solution()
            view.set_status("idle", "")
            
            new_state = PM.swap(model.state, blank, idx)
            model.state = new_state
            
            # Thực hiện hiệu ứng trượt mượt mà, sau đó cập nhật lại thanh ký tự hiển thị số
            view.slide_tile(idx, blank, new_state)
            view.set_input_fields(model.state, model.goal)

    def on_compare_all():
        """Chạy tất cả thuật toán trên cùng start/goal và mở bảng so sánh."""
        if view.is_sliding:
            return
        if model.is_goal():
            view.set_status("done", "Bàn cờ đã ở goal — không cần so sánh.")
            return

        view.set_status("computing", "Đang chạy và so sánh tất cả thuật toán...")
        view.update_idletasks()

        results, winners = compare_all_algorithms(
            model,
            controllers,
            depth_limit=view.get_depth_limit(),
            heuristic_group=view.get_heuristic_group(),
        )
        view.show_compare_dialog(results, winners)

        ok_count = sum(1 for r in results if r["success"])
        view.set_status(
            "done",
            f"So sánh xong: {ok_count}/{len(results)} thuật toán tìm được lời giải. "
            f"Double-click một dòng trong bảng để xem chi tiết.",
        )

    def on_compare_pick(row):
        """Khi double-click một dòng trong bảng so sánh — nạp lời giải lên UI."""
        algo = row["algorithm"]
        if hasattr(view, "_algo_var"):
            view._algo_var.set(algo)
        view.algo = algo
        view.T = algos_metadata[algo]["theme"]
        view._apply_theme()
        view.clear_solution()

        summary = {
            "algorithm": algo,
            "steps": row["steps"],
            "nodes_visited": row["nodes_visited"],
            "elapsed_ms": row["elapsed_ms"],
        }
        if row.get("total_cost") is not None:
            summary["total_cost"] = row["total_cost"]

        view.show_solution(row["path_states"], summary)

    def on_apply_states(start_str, goal_str):
        """Được gọi khi người dùng tự nhập chuỗi ma trận và nhấn APPLY CUSTOM STATES."""
        try:
            # Chuyển đổi và kiểm tra tính hợp lệ của chuỗi Start State nhập vào
            start_state = tuple(map(int, start_str.split()))
            if len(start_state) != 9 or sorted(start_state) != list(range(9)):
                view.set_status("error", "Lỗi: Trạng thái START phải chứa đủ 9 số từ 0 đến 8 không trùng lặp!")
                return
            
            # Chuyển đổi và kiểm tra tính hợp lệ của chuỗi Goal State nhập vào
            goal_state = tuple(map(int, goal_str.split()))
            if len(goal_state) != 9 or sorted(goal_state) != list(range(9)):
                view.set_status("error", "Lỗi: Trạng thái GOAL phải chứa đủ 9 số từ 0 đến 8 không trùng lặp!")
                return

            # Áp dụng cấu hình bàn cờ mới vào hệ thống Model
            model.state = start_state
            model.goal = goal_state
            model.start_state = start_state  # Định vị lại điểm mốc để nút Reset hoạt động chính xác

            # Làm sạch lịch sử giải cũ và vẽ lại bàn cờ mới lên UI
            view.clear_solution()
            view.draw_board(model.state)
            view.set_status("idle", "Đã áp dụng cấu hình bàn cờ tự chọn thành công.")
        except Exception:
            view.set_status("error", "Lỗi định dạng! Vui lòng nhập 9 ký số cách nhau bằng khoảng trắng (Ví dụ: 1 2 3 4 5 6 7 8 0)")

    # Inject (tiêm) toàn bộ các hàm xử lý sự kiện vào View thông qua dictionary
    callbacks["on_solve"]        = on_solve
    callbacks["on_shuffle"]      = on_shuffle
    callbacks["on_reset"]        = on_reset
    callbacks["on_tile_click"]   = on_tile_click
    callbacks["get_model_state"] = lambda: model.state
    callbacks["on_apply_states"] = on_apply_states
    callbacks["on_compare_all"] = on_compare_all
    callbacks["on_compare_pick"] = on_compare_pick

    # ── 7. Thiết lập trạng thái hiển thị ban đầu khi mở phần mềm ──────
    view.set_input_fields(model.state, model.goal)
    view.draw_board(model.state)

    # ── 8. Chạy ứng dụng ───────────────────────────────────────────────
    view.mainloop()


if __name__ == "__main__":
    main()