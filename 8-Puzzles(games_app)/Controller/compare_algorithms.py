"""
Chạy và so sánh tất cả thuật toán trên cùng một cặp (start, goal).
"""

from typing import Any, Dict, List, Tuple

from Model.puzzle_model import PuzzleModel
from Controller.plugins.dfs import DFSController
from Controller.plugins.ids import IDSController
from Controller.plugins.astar import AStarController
from Controller.plugins.ida_star import IDAStarController
from Controller.plugins.simple_hill_climbing import SimpleHillClimbingController
from Controller.plugins.steepest_ascent_hill_climbing import SteepestAscentHillClimbingController
from Controller.plugins.stochastic_hill_climbing import StochasticHillClimbingController
from Controller.plugins.random_restart_hill_climbing import RandomRestartHillClimbingController
from Controller.plugins.local_beam_search import LocalBeamSearchController


def _configure_controller(
    controller,
    depth_limit: int,
    heuristic_group: int = 1,
) -> None:
    if isinstance(controller, DFSController):
        controller.depth_limit = depth_limit
    elif isinstance(controller, IDSController):
        controller.max_depth = depth_limit
    elif isinstance(
        controller,
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
        controller.set_group(heuristic_group)


def run_single(
    algo_name: str,
    controller,
    model: PuzzleModel,
    start: Tuple[int, ...],
    goal: Tuple[int, ...],
    depth_limit: int,
    heuristic_group: int = 1,
) -> Dict[str, Any]:
    """Chạy một thuật toán, không làm đổi state cuối của model (khôi phục sau khi chạy)."""
    model.state = start
    model.goal = goal
    _configure_controller(controller, depth_limit, heuristic_group)

    success = controller.solve()
    summary = controller.get_summary()

    row = {
        "algorithm": algo_name,
        "success": success,
        "steps": summary["steps"] if success else None,
        "nodes_visited": summary["nodes_visited"],
        "elapsed_ms": round(summary["elapsed_ms"], 2),
        "total_cost": summary.get("total_cost"),
        "path_states": list(controller.solution_path) if success else [],
    }
    return row


def compare_all_algorithms(
    model: PuzzleModel,
    controllers: Dict[str, Any],
    depth_limit: int = 50,
    heuristic_group: int = 1,
) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
    """
    Chạy lần lượt mọi thuật toán trong `controllers` trên start/goal hiện tại.

    Trả về:
        results — danh sách kết quả từng thuật toán
        winners — gợi ý thuật toán tốt nhất theo từng tiêu chí
    """
    start = tuple(model.state)
    goal = tuple(model.goal)
    saved_state = model.state
    saved_goal = model.goal

    results: List[Dict[str, Any]] = []
    for algo_name, controller in controllers.items():
        results.append(
            run_single(
                algo_name, controller, model, start, goal, depth_limit, heuristic_group
            )
        )

    model.state = saved_state
    model.goal = saved_goal

    winners = _pick_winners(results)
    return results, winners


def _pick_winners(results: List[Dict[str, Any]]) -> Dict[str, str]:
    """Chọn thuật toán tốt nhất theo moves / nodes / thời gian (chỉ trong các lời giải thành công)."""
    ok = [r for r in results if r["success"]]
    hints: Dict[str, str] = {}

    if not ok:
        hints["note"] = "Khong thuat toan nao tim duoc loi giai (thu tang Depth Limit voi DFS/IDS)."
        return hints

    def _min_row(key, label):
        best = min(ok, key=lambda r: r[key])
        tied = [r["algorithm"] for r in ok if r[key] == best[key]]
        hints[label] = best["algorithm"] if len(tied) == 1 else ", ".join(tied)

    _min_row("steps", "fewest_moves")
    _min_row("nodes_visited", "fewest_nodes")
    _min_row("elapsed_ms", "fastest")

    # So sánh đường đi (cùng số bước hay khác)
    steps_set = {r["steps"] for r in ok}
    if len(steps_set) == 1:
        hints["same_path_length"] = f"Tat ca deu {ok[0]['steps']} nuoc di"
    else:
        hints["same_path_length"] = f"Khac so nuoc di: {min(steps_set)} .. {max(steps_set)}"

    return hints
