# 8-Puzzles (games_app)

Ứng dụng giải bài toán 8-puzzle theo kiến trúc MVC, hỗ trợ nhiều thuật toán tìm kiếm và giao diện Tkinter theo theme.

## 1) Chạy chương trình

```bash
python main.py
```

Có thể chọn thuật toán mặc định từ CLI:

```bash
python main.py BFS
python main.py "SIMPLE HILL CLIMBING"
python main.py "A*"
python main.py "IDA*"
```

## 2) Flow tổng thể của game

1. `main.py` khởi tạo `PuzzleModel`.
2. Nạp metadata thuật toán (tên, subtitle, theme) và dựng `PuzzleView`.
3. Tạo các controller (mỗi thuật toán là một plugin).
4. Gắn callback View -> Controller:
   - `SOLVE`: chạy thuật toán đang chọn.
   - `SHUFFLE`: xáo trạng thái mới.
   - `RESET`: về trạng thái bắt đầu hiện tại.
   - `APPLY CUSTOM STATES`: nhập start/goal thủ công.
   - `COMPARE ALL`: chạy toàn bộ thuật toán trên cùng một cặp start/goal.
5. View hiển thị:
   - bàn cờ,
   - số bước, số node, thời gian, cost (nếu có),
   - danh sách path và playback.

## 3) Liên kết giữa các file (bản đồ mã nguồn)

### Entry point
- `main.py`
  - khởi tạo app
  - đăng ký plugin thuật toán
  - điều phối callback View/Model/Controller

### Model
- `Model/puzzle_model.py`
  - biểu diễn state puzzle
  - `get_moves`, `swap`, `shuffle`, `reset`, `is_goal`

### View
- `View/puzzle_view.py`
  - toàn bộ UI Tkinter
  - đổi theme theo thuật toán
  - panel chọn nhóm heuristic/cost cho A*, IDA*, Simple Hill Climbing
  - playback, compare dialog, status bar

### Controller nền
- `Controller/base_controller.py`
  - interface chung cho mọi thuật toán
  - `solve()` + `get_summary()`

### Heuristic và cost dùng chung
- `Controller/heuristics.py`
  - metric: `misplaced`, `manhattan`, `inversions`, `swap`
  - preset nhóm:
    - `ASTAR_GROUPS`
    - `IDA_GROUPS`
    - `SHC_GROUPS` (Manhattan / số ô sai / swap)
    - `SHC_MANHATTAN_MISPLACED_GROUPS` (Manhattan / số ô sai — cho Stochastic, RRHC, Local Beam)

### Plugin thuật toán
- `Controller/plugins/bfs.py`
- `Controller/plugins/dfs.py`
- `Controller/plugins/ids.py`
- `Controller/plugins/ucs.py`
- `Controller/plugins/greedy_search.py`
- `Controller/plugins/astar.py`
- `Controller/plugins/ida_star.py`
- `Controller/plugins/simple_hill_climbing.py`
- `Controller/plugins/steepest_ascent_hill_climbing.py`
- `Controller/plugins/stochastic_hill_climbing.py`
- `Controller/plugins/random_restart_hill_climbing.py`
- `Controller/plugins/local_beam_search.py`

### So sánh thuật toán
- `Controller/compare_algorithms.py`
  - chạy lần lượt từng plugin trên cùng start/goal
  - tổng hợp winners theo tiêu chí `moves`, `nodes`, `time`

## 4) Phân tích nhanh các thuật toán

## BFS
- Ưu: đảm bảo lời giải ngắn nhất theo số bước.
- Nhược: tốn RAM và node khi trạng thái khó.

## DFS (depth limit)
- Ưu: ít RAM hơn BFS.
- Nhược: không đảm bảo tối ưu; phụ thuộc `Depth Limit`.

## IDS
- Ưu: kết hợp ưu điểm DFS về RAM và vẫn tìm được nghiệm nông trước.
- Nhược: lặp lại nhiều node qua các vòng sâu.

## UCS
- Ưu: tối ưu theo định nghĩa cost tích lũy `g(n)`.
- Nhược: có thể mở rộng nhiều node nếu cost không phân tách tốt.

## Greedy Best-First Search
- Ưu: thường nhanh, ít node.
- Nhược: không đảm bảo tối ưu số bước/cost.

## A*
- Ưu: cân bằng giữa `g(n)` và `h(n)`, thường cho nghiệm tốt.
- Nhược: có thể nặng RAM hơn Greedy.
- Nhóm cấu hình:
  - Nhóm 1: `h=misplaced`, `g=inversions`
  - Nhóm 2: `h=swap`, `g=manhattan`
  - Nhóm 3: `h=manhattan`, `g=misplaced`

## IDA*
- Ưu: tiết kiệm RAM hơn A* nhờ iterative deepening theo ngưỡng `f`.
- Nhược: có thể chậm do tìm lại nhiều lần.
- Nhóm cấu hình:
  - Nhóm 1: `h=misplaced`, `g=manhattan`
  - Nhóm 2: `h=inversions`, `g=misplaced`
  - Nhóm 3: `h=manhattan`, `g=manhattan`

## Simple Hill Climbing
- Ưu: rất nhẹ, đơn giản, tốc độ cao.
- Nhược: dễ kẹt local maximum; không đảm bảo tới goal.
- Cơ chế: **first-improvement** (neighbor tốt hơn đầu tiên) + random-restart.
- Nhóm value: Manhattan / số ô sai / swap (giống Steepest-Ascent).

## Steepest-Ascent Hill Climbing
- Ưu: mỗi bước chọn neighbor **tốt nhất** trong tất cả neighbor (ổn định hơn Simple).
- Nhược: vẫn dễ kẹt local maximum; không đảm bảo tới goal.
- Cơ chế: duyệt hết neighbor, chọn `Value(n)` cao nhất nếu tốt hơn current.
- Nhóm value:
  - Nhóm 1: `Value=manhattan`
  - Nhóm 2: `Value=misplaced`
  - Nhóm 3: `Value=swap`

## Stochastic Hill Climbing
- Cơ chế: trong các neighbor có `Value` tốt hơn current, chọn **ngẫu nhiên** một neighbor.
- Nhóm value:
  - **Manhattan** (nhóm 1)
  - **Số ô sai** (nhóm 2)

## Random-Restart Hill Climbing
- Cơ chế: lặp **Steepest-Ascent** từ start và các điểm khởi động lại (random walk).
- Nhóm value: Manhattan / số ô sai (tối đa 30 lần restart).

## Local Beam Search
- Cơ chế: giữ `k=5` trạng thái tốt nhất theo `Value(n)`; mỗi vòng mở rộng toàn bộ beam.
- Nhóm value: Manhattan / số ô sai.

> Lưu ý: fail của Hill Climbing / Beam Search thường là **đúng bản chất thuật toán**, không nhất thiết là bug.

## 5) Ghi chú UI và trải nghiệm

- App tự khóa kích thước để không vỡ layout.
- Với thuật toán có panel nhóm (`A*`, `IDA*`, các Hill Climbing, Local Beam), UI tăng chiều cao và tự canh giữa.
- Nếu thuật toán leo đồi thất bại, status báo rõ đã dừng ở local maximum.

## 6) Hướng nâng cấp tiếp

- Thêm `Steepest-Ascent + Sideway moves`.
- Cho phép bật/tắt từng thuật toán trong `COMPARE ALL`.
