import sys
import tkinter as tk
from tkinter import ttk

FONT_TITLE  = ("Courier New", 20, "bold")
FONT_SUB    = ("Courier New", 10)
FONT_TILE   = ("Courier New", 26, "bold")
FONT_BTN    = ("Courier New", 10, "bold")
FONT_PLAY_BTN = ("Courier New", 12, "bold")
FONT_INFO   = ("Courier New", 10)
FONT_STEP   = ("Courier New", 10)
FONT_METRIC = ("Courier New", 18, "bold")
FONT_METRIC_VAL = ("Courier New", 14, "bold")

TILE_SIZE  = 88
GAP        = 8
SLIDE_STEPS = 8
SLIDE_MS   = 12

# Kích thước tối thiểu panel phải / metric (tránh cắt chữ)
RIGHT_PANEL_MIN_W = 460
METRIC_BOX_W      = 210
METRIC_BOX_H      = 58
LISTBOX_CHARS     = 40
ACTIONS_TEXT_LINES = 4
# Kích thước cửa sổ gợi ý (DFS/IDS có thêm thanh DEPTH LIMIT)
WIN_W               = 920
WIN_H_STANDARD      = 700   # BFS, UCS, Greedy, ...
WIN_H_WITH_DEPTH    = 770   # DFS, IDS (+ thanh depth)
WIN_H_WITH_HEUR     = 820   # A*, IDA* (+ chọn nhóm h/g)
UI_BORD_W           = 2


class PuzzleView(tk.Tk):
    def __init__(self, algos_metadata: dict, default_algo: str, callbacks: dict):
        super().__init__()
        self.algos_data = algos_metadata
        self.algo = default_algo
        self.T = self.algos_data.get(default_algo, {}).get("theme", {})
        self.cb = callbacks

        self.title("8-PUZZLE  //  DYNAMIC PLUGINS")
        self.resizable(False, False)

        self._sliding     = False
        self._play_job    = None
        self._anim_delay  = tk.IntVar(value=350)
        self._depth_var   = tk.IntVar(value=50)
        self._heur_var    = tk.IntVar(value=1)
        self.solution_path = []
        self.play_idx      = 0
        self.tile_items    = {}

        self._build_ui()
        self._apply_theme()
        self._set_status("idle")

        # Căn giữa màn hình + tắt maximize (Windows) sau khi layout xong
        self.after_idle(self._on_window_ready)

        self.play_idx = 0
        self._play_job = None

    # ── BUILD UI ──────────────────────────────────────────────────────

    def _build_ui(self):
        # Top title bar
        self._top_frame = tk.Frame(self)
        self._top_frame.pack(fill="x", padx=20, pady=(18, 0))
        
        self._lbl_title_main = tk.Label(self._top_frame, text="8-PUZZLE", font=FONT_TITLE)
        self._lbl_title_main.pack(side="left")
        
        self._lbl_title_tag = tk.Label(self._top_frame, font=("Courier New", 12))
        self._lbl_title_tag.pack(side="left", pady=(6, 0))

        # Status indicator
        self._dot_frame = tk.Frame(self._top_frame)
        self._dot_frame.pack(side="right", padx=(0, 4))
        
        self._dot_cv = tk.Canvas(self._dot_frame, width=12, height=12, highlightthickness=0)
        self._dot_cv.pack(side="left", pady=(6, 0))
        self._dot = self._dot_cv.create_oval(1, 1, 11, 11, fill="#555", outline="")
        
        self._dot_lbl = tk.Label(self._dot_frame, text="IDLE", font=("Courier New", 9, "bold"), fg="#555")
        self._dot_lbl.pack(side="left", padx=(4, 0), pady=(6, 0))

        # Subtitle (wrap khi mô tả thuật toán dài)
        self._lbl_subtitle = tk.Label(
            self, font=("Courier New", 9), justify="left", wraplength=WIN_W - 40,
        )
        self._lbl_subtitle.pack(anchor="w", padx=20, fill="x")

        # Body
        self._body_frame = tk.Frame(self)
        self._body_frame.pack(padx=20, pady=12)
        
        self._left_frame = tk.Frame(self._body_frame)
        self._left_frame.pack(side="left", anchor="n")
        
        self._right_frame = tk.Frame(self._body_frame, padx=16, width=RIGHT_PANEL_MIN_W)
        self._right_frame.pack(side="left", anchor="n", fill="y")
        self._right_frame.pack_propagate(False)

        # Board canvas
        board_size = 3 * TILE_SIZE + 4 * GAP
        self._canvas = tk.Canvas(self._left_frame, width=board_size, height=board_size, highlightthickness=0)
        self._canvas.pack()
        self._canvas.bind("<Button-1>", self._on_canvas_click)

        # Buttons row
        self._btn_row = tk.Frame(self._left_frame)
        self._btn_row.pack(pady=(10, 0), fill="x")
        
        if len(self.algos_data) > 1:
            self._algo_var = tk.StringVar(value=self.algo)
            self._opt_frame = tk.Frame(self._btn_row)
            self._opt_frame.pack(side="right", padx=(8, 0))
            
            self._opt_menu = tk.OptionMenu(self._opt_frame, self._algo_var, *self.algos_data.keys())
            self._opt_menu.config(
                font=FONT_BTN,
                relief="flat",
                bd=0,
                padx=8,
                pady=3,
                width=16,
                anchor="w",
                cursor="hand2",
                highlightthickness=UI_BORD_W,
            )
            self._opt_menu.pack()
            
            def _on_algo_select(*args):
                new_algo = self._algo_var.get()
                if new_algo != self.algo:
                    self.algo = new_algo
                    self.T = self.algos_data[new_algo]["theme"]
                    self._apply_theme()
                    self.clear_solution()
                    if "on_algo_changed" in self.cb:
                        self.cb["on_algo_changed"](new_algo)
            self._algo_var.trace_add("write", _on_algo_select)

        self._btn_solve = self._mk_btn(self._btn_row, "▶  SOLVE", lambda: self.cb["on_solve"](self.algo), primary=True)
        self._btn_solve.pack(side="left", padx=(0, 8))
        
        self._btn_shuffle = self._mk_btn(self._btn_row, "SHUFFLE", lambda: self.cb["on_shuffle"]())
        self._btn_shuffle.pack(side="left", padx=(0, 8))
        
        self._btn_reset = self._mk_btn(self._btn_row, "RESET", lambda: self.cb["on_reset"]())
        self._btn_reset.pack(side="left")

        self._cmp_row = tk.Frame(self._left_frame)
        self._cmp_row.pack(pady=(8, 0), fill="x")
        self._btn_compare = self._mk_btn(
            self._cmp_row, "COMPARE ALL",
            lambda: self.cb["on_compare_all"]() if "on_compare_all" in self.cb else None,
        )
        self._btn_compare.pack(fill="x")

        # Depth Slider (Dành cho DFS/IDS) — hiện trong _apply_theme
        self._dep_row = tk.Frame(self._left_frame)
        self._lbl_dep_title = tk.Label(self._dep_row, text="DEPTH LIMIT:", font=FONT_SUB)
        self._lbl_dep_title.pack(side="left")
        self._dep_lbl = tk.Label(self._dep_row, text="50", font=FONT_SUB, width=4)
        self._dep_lbl.pack(side="right")
        self._scale_depth = tk.Scale(self._dep_row, from_=10, to=100, orient="horizontal", variable=self._depth_var,
                                     showvalue=False, highlightthickness=0,
                                     command=lambda v: self._dep_lbl.config(text=str(int(float(v)))))
        self._scale_depth.pack(side="left", fill="x", expand=True, padx=(8, 4))

        # Nhóm h(n)/g(n) — A* và IDA*
        self._heur_row = tk.Frame(self._left_frame)
        self._lbl_heur_title = tk.Label(self._heur_row, text="NHÓM h(n) / g(n):", font=FONT_SUB)
        self._lbl_heur_title.pack(anchor="w")
        self._heur_btn_row = tk.Frame(self._heur_row, padx=6, pady=4, bd=0, relief="flat")
        self._heur_btn_row.pack(fill="x", pady=(4, 2))
        self._heur_btn_row.columnconfigure(0, weight=1, uniform="heur")
        self._heur_btn_row.columnconfigure(1, weight=1, uniform="heur")
        self._heur_btn_row.columnconfigure(2, weight=1, uniform="heur")
        self._heur_radios = []
        for i in range(1, 4):
            rb = tk.Radiobutton(
                self._heur_btn_row, text=f"Nhóm {i}", variable=self._heur_var, value=i,
                font=FONT_SUB, indicatoron=False, bd=0, padx=10, pady=3,
                width=9, command=self._on_heur_group_change,
            )
            rb.grid(row=0, column=i - 1, padx=4, sticky="ew")
            self._heur_radios.append(rb)
        self._lbl_heur_detail = tk.Label(self._heur_row, text="", font=("Courier New", 9))
        self._lbl_heur_detail.pack(anchor="w", pady=(2, 0))

        # ─── KHUNG NHẬP LIỆU START & GOAL ───
        self._input_frame = tk.Frame(self._left_frame)
        self._input_frame.pack(pady=(12, 0), fill="x")
        self._input_frame.columnconfigure(1, weight=1)

        self._input_frame.columnconfigure(0, minsize=56)

        self._lbl_st_tag = tk.Label(self._input_frame, text="START:", font=FONT_SUB, width=7, anchor="w")
        self._lbl_st_tag.grid(row=0, column=0, sticky="w", pady=2, padx=(0, 10))
        self._ent_start = tk.Entry(self._input_frame, font=FONT_SUB, bd=1, relief="solid", width=22)
        self._ent_start.grid(row=0, column=1, sticky="ew", padx=(0, 0), pady=2)

        self._lbl_gl_tag = tk.Label(self._input_frame, text="GOAL:", font=FONT_SUB, width=7, anchor="w")
        self._lbl_gl_tag.grid(row=1, column=0, sticky="w", pady=2, padx=(0, 10))
        self._ent_goal = tk.Entry(self._input_frame, font=FONT_SUB, bd=1, relief="solid")
        self._ent_goal.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=2)

        self._btn_apply = self._mk_btn(self._input_frame, "APPLY CUSTOM STATES", self._on_apply_click)
        self._btn_apply.grid(row=2, column=0, columnspan=2, pady=(6, 0), sticky="ew")

        # Speed slider
        self._spd_row = tk.Frame(self._left_frame)
        self._spd_row.pack(pady=(6, 0), fill="x")
        self._lbl_spd_title = tk.Label(self._spd_row, text="SPEED:", font=FONT_SUB)
        self._lbl_spd_title.pack(side="left")
        self._spd_lbl = tk.Label(self._spd_row, text="350 ms", font=FONT_SUB, width=7)
        self._spd_lbl.pack(side="right")
        self._scale_speed = tk.Scale(self._spd_row, from_=50, to=1200, orient="horizontal", variable=self._anim_delay,
                                     showvalue=False, highlightthickness=0,
                                     command=lambda v: self._spd_lbl.config(text=f"{int(float(v))} ms"))
        self._scale_speed.pack(side="left", fill="x", expand=True, padx=(8, 4))

        # Playback + actions: pack side=bottom TRƯỚC để luôn hiện (listbox expand không đẩy chúng ra ngoài cửa sổ)
        self._ctrl_frame = tk.Frame(self._right_frame)
        self._ctrl_frame.pack(side="bottom", pady=(8, 0), fill="x")

        self._lbl_playback = tk.Label(
            self._ctrl_frame, text="PLAYBACK:", font=FONT_SUB, anchor="w",
        )
        self._lbl_playback.pack(anchor="w", pady=(0, 6))

        self._ctrl_btn_row = tk.Frame(self._ctrl_frame)
        self._ctrl_btn_row.pack(fill="x")

        self._btn_prev = self._mk_play_btn(self._ctrl_btn_row, "◀", self._step_back, state="disabled", w=5)
        self._btn_prev.pack(side="left", padx=(0, 10))

        self._btn_play = self._mk_play_btn(self._ctrl_btn_row, "▶  PLAY", self._auto_play, state="disabled", w=10)
        self._btn_play.pack(side="left", padx=(0, 10))

        self._btn_next = self._mk_play_btn(self._ctrl_btn_row, "▶", self._step_fwd, state="disabled", w=5)
        self._btn_next.pack(side="left")

        self._lbl_counter = tk.Label(self._ctrl_btn_row, text="", font=FONT_SUB)
        self._lbl_counter.pack(side="left", padx=(16, 0), pady=6)

        self._act_frame = tk.Frame(self._right_frame)
        self._act_frame.pack(side="bottom", pady=(8, 8), fill="x")
        self._act_frame.columnconfigure(0, weight=1)
        self._lbl_actions_title = tk.Label(
            self._act_frame, text="ACTIONS (U / D / L / R):",
            font=("Courier New", 10, "bold"),
        )
        self._lbl_actions_title.grid(row=0, column=0, sticky="w", pady=(0, 4))

        self._act_text_wrap = tk.Frame(self._act_frame)
        self._act_text_wrap.grid(row=1, column=0, sticky="ew")
        self._act_text_wrap.columnconfigure(0, weight=1)

        self._act_sb_y = ttk.Scrollbar(self._act_text_wrap, orient="vertical")
        self._act_sb_y.grid(row=0, column=1, sticky="ns")
        self._act_sb_x = ttk.Scrollbar(self._act_text_wrap, orient="horizontal")
        self._act_sb_x.grid(row=1, column=0, sticky="ew")

        self._text_actions = tk.Text(
            self._act_text_wrap, height=ACTIONS_TEXT_LINES, width=52,
            font=("Courier New", 9), wrap=tk.NONE, relief="flat",
            highlightthickness=1, yscrollcommand=self._act_sb_y.set,
            xscrollcommand=self._act_sb_x.set, state="disabled",
        )
        self._text_actions.grid(row=0, column=0, sticky="ew")
        self._act_sb_y.config(command=self._text_actions.yview)
        self._act_sb_x.config(command=self._text_actions.xview)

        # RIGHT: Solution path info (phần giữa co giãn; listbox không chiếm chỗ của playback)
        self._lbl_panel_title = tk.Label(self._right_frame, text="SOLUTION PATH", font=("Courier New", 11, "bold"))
        self._lbl_panel_title.pack(side="top", anchor="w")

        self._met_frame = tk.Frame(self._right_frame)
        self._met_frame.pack(side="top", anchor="w", pady=(10, 10), fill="x")
        self._met_frame.columnconfigure(0, weight=1, uniform="metric")
        self._met_frame.columnconfigure(1, weight=1, uniform="metric")

        self._f_steps, self._lbl_steps = self._mk_metric(self._met_frame, "MOVES")
        self._f_steps.grid(row=0, column=0, padx=(0, 8), pady=(0, 8), sticky="nsew")
        self._f_time, self._lbl_time = self._mk_metric(self._met_frame, "TIME (ms)")
        self._f_time.grid(row=0, column=1, pady=(0, 8), sticky="nsew")
        self._f_nodes, self._lbl_nodes = self._mk_metric(self._met_frame, "NODES VISITED")
        self._f_nodes.grid(row=1, column=0, columnspan=2, sticky="nsew")

        self._lb_wrap = tk.Frame(self._right_frame, padx=1, pady=1)
        self._lb_wrap.pack(side="top", fill="both", expand=True)
        self._inner_lb = tk.Frame(self._lb_wrap)
        self._inner_lb.pack(fill="both", expand=True)

        self._sb = ttk.Scrollbar(self._inner_lb, orient="vertical")
        self._sb.pack(side="right", fill="y")

        self._listbox = tk.Listbox(
            self._inner_lb, width=LISTBOX_CHARS, height=9, font=FONT_STEP,
            activestyle="none", relief="flat", yscrollcommand=self._sb.set,
            highlightthickness=0, bd=0,
        )
        self._listbox.pack(side="left", fill="both", expand=True)
        self._sb.config(command=self._listbox.yview)
        self._listbox.bind("<<ListboxSelect>>", self._on_list_select)

        # Status — full width dưới cùng (tránh cắt thông báo dài)
        self._status_frame = tk.Frame(self)
        self._status_frame.pack(fill="x", padx=20, pady=(4, 14))
        self._lbl_status = tk.Label(
            self._status_frame, text="", font=FONT_INFO, anchor="w",
            justify="left", wraplength=WIN_W - 40,
        )
        self._lbl_status.pack(fill="x")

    # ── PUBLIC API & LOGIC ────────────────────────────────────────────

    def _needs_depth_tools(self) -> bool:
        u = self.algo.upper()
        return "DFS" in u or "IDS" in u or u == "MY_ALGO"

    def _needs_heuristic_group(self) -> bool:
        return self.algo in (
            "A*",
            "IDA*",
            "Simple Hill Climbing",
            "Steepest-Ascent Hill Climbing",
            "Stochastic Hill Climbing",
            "Random-Restart Hill Climbing",
            "Local Beam Search",
        )

    def _is_hill_climbing_algo(self) -> bool:
        return "Hill Climbing" in self.algo or self.algo == "Local Beam Search"

    def _heuristic_groups_for_algo(self):
        from Controller.heuristics import ASTAR_GROUPS, IDA_GROUPS, SHC_GROUPS, SHC_MANHATTAN_MISPLACED_GROUPS
        from Controller.plugins.stochastic_hill_climbing import StochasticHillClimbingController
        from Controller.plugins.random_restart_hill_climbing import RandomRestartHillClimbingController
        from Controller.plugins.local_beam_search import LocalBeamSearchController
        from Controller.plugins.simulated_annealing import SimulatedAnnealingController # <--- THÊM DÒNG NÀY
        
        if self.algo == "A*": return ASTAR_GROUPS
        if self.algo == "IDA*": return IDA_GROUPS
        if self.algo in (
            StochasticHillClimbingController.ALGO_NAME,
            RandomRestartHillClimbingController.ALGO_NAME,
            LocalBeamSearchController.ALGO_NAME,
            SimulatedAnnealingController.ALGO_NAME, # <--- THÊM TÊN SA VÀO ĐÂY
        ):
            return SHC_MANHATTAN_MISPLACED_GROUPS
        if self._is_hill_climbing_algo():
            return SHC_GROUPS
        return ASTAR_GROUPS

    def _sync_heur_panel(self) -> None:
        """Cập nhật tiêu đề, nhãn nút và số nhóm theo thuật toán đang chọn."""
        if not self._needs_heuristic_group():
            return
        groups = self._heuristic_groups_for_algo()
        max_grp = max(groups.keys())
        if int(self._heur_var.get()) > max_grp:
            self._heur_var.set(1)

        if self._is_hill_climbing_algo():
            self._lbl_heur_title.config(text="NHÓM Value(n):")
        else:
            self._lbl_heur_title.config(text="NHÓM h(n) / g(n):")

        from Controller.heuristics import hill_group_button_text, group_label

        for i, rb in enumerate(self._heur_radios, start=1):
            if i <= max_grp:
                if self._is_hill_climbing_algo():
                    rb.config(text=hill_group_button_text(i, groups))
                else:
                    rb.config(text=f"Nhóm {i}")
                rb.grid()
            else:
                rb.grid_remove()

        if not self._is_hill_climbing_algo():
            grp = self.get_heuristic_group()
            self._lbl_heur_detail.config(text=group_label(groups[grp]))

    def get_heuristic_group(self) -> int:
        return int(self._heur_var.get())

    def _recommended_size(self) -> tuple[int, int]:
        if self._needs_heuristic_group():
            h = WIN_H_WITH_HEUR
        elif self._needs_depth_tools():
            h = WIN_H_WITH_DEPTH
        else:
            h = WIN_H_STANDARD
        return WIN_W, h

    def _on_heur_group_change(self):
        self._update_heur_subtitle()
        self.clear_solution()
        self.after_idle(self._fit_window_for_algo)

    def _update_heur_subtitle(self):
        if not self._needs_heuristic_group():
            return
        from Controller.plugins.astar import AStarController
        from Controller.plugins.ida_star import IDAStarController
        from Controller.plugins.simple_hill_climbing import SimpleHillClimbingController
        from Controller.plugins.steepest_ascent_hill_climbing import SteepestAscentHillClimbingController
        from Controller.plugins.stochastic_hill_climbing import StochasticHillClimbingController
        from Controller.plugins.random_restart_hill_climbing import RandomRestartHillClimbingController
        from Controller.plugins.local_beam_search import LocalBeamSearchController

        grp = self.get_heuristic_group()
        if self.algo == "A*":
            text = AStarController.subtitle_for_group(grp)
        elif self.algo == "Simple Hill Climbing":
            text = SimpleHillClimbingController.subtitle_for_group(grp)
        elif self.algo == "Steepest-Ascent Hill Climbing":
            text = SteepestAscentHillClimbingController.subtitle_for_group(grp)
        elif self.algo == "Stochastic Hill Climbing":
            text = StochasticHillClimbingController.subtitle_for_group(grp)
        elif self.algo == "Random-Restart Hill Climbing":
            text = RandomRestartHillClimbingController.subtitle_for_group(grp)
        elif self.algo == "Local Beam Search":
            text = LocalBeamSearchController.subtitle_for_group(grp)
        else:
            text = IDAStarController.subtitle_for_group(grp)
        T = self.T
        self._lbl_subtitle.config(bg=T["BG"], fg=T["LABEL_FG"], text=text)
        self._lbl_heur_detail.config(bg=T["BG"], fg=T["PRI_BG"], text=text)

    def _update_text_wraps(self):
        wrap = max(480, self.winfo_width() - 40)
        self._lbl_subtitle.config(wraplength=wrap)
        self._lbl_status.config(wraplength=wrap)

    def _on_window_ready(self):
        self._fit_window_for_algo(center=True)
        self._disable_maximize_button()

    def _disable_maximize_button(self):
        """Ẩn nút maximize trên title bar (Windows)."""
        if sys.platform != "win32":
            return
        try:
            import ctypes

            GWL_STYLE = -16
            WS_MAXIMIZEBOX = 0x00010000
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            if not hwnd:
                hwnd = self.winfo_id()
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
            ctypes.windll.user32.SetWindowLongW(
                hwnd, GWL_STYLE, style & ~WS_MAXIMIZEBOX,
            )
            ctypes.windll.user32.DrawMenuBar(hwnd)
        except Exception:
            pass

    def _fit_window_for_algo(self, center: bool = False):
        """Đặt minsize + geometry vừa nội dung (có/không thanh depth), giữ dòng status hiển thị."""
        w, h = self._recommended_size()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        h = min(h, max(620, sh - 80))
        self.minsize(w, h)
        self.maxsize(w, h)
        if center:
            x = max(0, (sw - w) // 2)
            y = 24
        else:
            x, y = self.winfo_x(), self.winfo_y()
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.update_idletasks()
        self._update_text_wraps()

    def _apply_theme(self):
        T = self.T
        self.configure(bg=T["BG"])
        
        algo_title = self.algos_data.get(self.algo, {}).get("name", self.algo)
        self._lbl_title_tag.config(bg=T["BG"], fg=T["LABEL_FG"], text=f"  //  {algo_title} SOLVER")
        
        if self._needs_heuristic_group():
            self._update_heur_subtitle()
            algo_sub = self._lbl_subtitle.cget("text")
        else:
            algo_sub = self.algos_data.get(self.algo, {}).get("subtitle", "")
            self._lbl_subtitle.config(bg=T["BG"], fg=T["LABEL_FG"], text=algo_sub)

        self._top_frame.config(bg=T["BG"])
        self._lbl_title_main.config(bg=T["BG"], fg=T["PRI_BG"])
        self._dot_frame.config(bg=T["BG"])
        self._dot_cv.config(bg=T["BG"])
        self._dot_lbl.config(bg=T["BG"])
        self._body_frame.config(bg=T["BG"])
        self._left_frame.config(bg=T["BG"])
        self._right_frame.config(bg=T["BG"])
        
        self._canvas.config(bg=T["BG"])
        self._canvas.delete("grid")
        self._draw_grid_lines()

        self._btn_row.config(bg=T["BG"])
        self._btn_solve.config(bg=T["PRI_BG"], fg=T["PRI_FG"], activebackground=T["ABTN"])
        self._btn_shuffle.config(bg=T["SEC_BG"], fg=T["SEC_FG"], activebackground=T["ABTN2"])
        self._btn_reset.config(bg=T["SEC_BG"], fg=T["SEC_FG"], activebackground=T["ABTN2"])
        self._cmp_row.config(bg=T["BG"])
        self._btn_compare.config(bg=T["SEC_BG"], fg=T["SEC_FG"], activebackground=T["ABTN2"])

        if hasattr(self, '_opt_frame'):
            self._opt_frame.config(bg=T["BG"])
            bord = self._border_color()
            self._opt_menu.config(
                bg=T["SEC_BG"],
                fg=T["SEC_FG"],
                activebackground=T["ABTN2"],
                activeforeground=T["SEC_FG"],
                highlightbackground=bord,
                highlightcolor=bord,
            )
            self._opt_menu["menu"].config(
                bg=T["PANEL_BG"],
                fg=T["LABEL_FG"],
                activebackground=T["HL_BG"],
                activeforeground=T["HL_FG"],
                selectcolor=T["HL_BG"],
                font=FONT_BTN,
            )

        if self._needs_depth_tools():
            self._dep_row.pack_forget()
            self._dep_row.pack(pady=(10, 0), fill="x", before=self._input_frame)
            self._dep_row.config(bg=T["BG"])
            self._lbl_dep_title.config(bg=T["BG"], fg=T["LABEL_FG"])
            self._dep_lbl.config(bg=T["BG"], fg=T["PRI_BG"])
            self._scale_depth.config(bg=T["BG"], fg=T["PRI_BG"], troughcolor=T["PANEL_BG"], activebackground=T["PRI_BG"])
        else:
            self._dep_row.pack_forget()

        if self._needs_heuristic_group():
            self._heur_row.pack_forget()
            self._heur_row.pack(pady=(10, 0), fill="x", before=self._input_frame)
            self._heur_row.config(bg=T["BG"])
            self._lbl_heur_title.config(bg=T["BG"], fg=T["LABEL_FG"])
            self._lbl_heur_detail.config(bg=T["BG"], fg=T["PRI_BG"])
            self._heur_btn_row.config(
                bg=T["PANEL_BG"],
                highlightthickness=UI_BORD_W,
                highlightbackground=T["GRID_LINE"],
                highlightcolor=T["GRID_LINE"],
            )
            for rb in self._heur_radios:
                rb.config(
                    bg=T["SEC_BG"],
                    fg=T["SEC_FG"],
                    selectcolor=T["ABTN"],
                    activebackground=T["ABTN2"],
                    activeforeground=T["HL_FG"],
                    highlightthickness=1,
                    highlightbackground=T["GRID_LINE"],
                    highlightcolor=T["PRI_BG"],
                )
            self._sync_heur_panel()
            self._update_heur_subtitle()
        else:
            self._heur_row.pack_forget()

        # Áp dụng màu cho khung nhập liệu Start/Goal
        self._input_frame.config(bg=T["BG"])
        self._lbl_st_tag.config(bg=T["BG"], fg=T["LABEL_FG"])
        self._lbl_gl_tag.config(bg=T["BG"], fg=T["LABEL_FG"])
        self._ent_start.config(bg=T["PANEL_BG"], fg=T["PRI_BG"], insertbackground=T["PRI_BG"], highlightbackground=T["GRID_LINE"])
        self._ent_goal.config(bg=T["PANEL_BG"], fg=T["PRI_BG"], insertbackground=T["PRI_BG"], highlightbackground=T["GRID_LINE"])
        self._btn_apply.config(bg=T["SEC_BG"], fg=T["SEC_FG"], activebackground=T["ABTN2"])

        self._spd_row.config(bg=T["BG"])
        self._lbl_spd_title.config(bg=T["BG"], fg=T["LABEL_FG"])
        self._spd_lbl.config(bg=T["BG"], fg=T["PRI_BG"])
        self._scale_speed.config(bg=T["BG"], fg=T["PRI_BG"], troughcolor=T["PANEL_BG"], activebackground=T["PRI_BG"])

        self._lbl_panel_title.config(bg=T["BG"], fg=T["PRI_BG"])
        self._met_frame.config(bg=T["BG"])

        for f, lbl, name in [(self._f_steps, self._lbl_steps, "MOVES"), 
                             (self._f_nodes, self._lbl_nodes, "NODES VISITED"), 
                             (self._f_time, self._lbl_time, "TIME (ms)")]:
            f.config(bg=T["METRIC_BG"], highlightbackground=T["GRID_LINE"])
            f.winfo_children()[0].config(bg=T["METRIC_BG"], fg=T["LABEL_FG"])
            lbl.config(bg=T["METRIC_BG"], fg=T["PRI_BG"])

        self._lb_wrap.config(bg=T["TILE_BORD"])
        self._inner_lb.config(bg=T["BG"])
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "App.Vertical.TScrollbar",
            background=T["PANEL_BG"],
            troughcolor=T["BG"],
            bordercolor=T["GRID_LINE"],
            darkcolor=T["PANEL_BG"],
            lightcolor=T["PANEL_BG"],
            arrowcolor=T["PRI_BG"],
            gripcount=0,
        )
        style.configure(
            "App.Horizontal.TScrollbar",
            background=T["PANEL_BG"],
            troughcolor=T["BG"],
            bordercolor=T["GRID_LINE"],
            darkcolor=T["PANEL_BG"],
            lightcolor=T["PANEL_BG"],
            arrowcolor=T["PRI_BG"],
            gripcount=0,
        )
        style.map(
            "App.Vertical.TScrollbar",
            background=[("active", T["ABTN2"])],
        )
        style.map(
            "App.Horizontal.TScrollbar",
            background=[("active", T["ABTN2"])],
        )
        self._sb.config(style="App.Vertical.TScrollbar")
        self._listbox.config(bg=T["BG"], fg=T["LABEL_FG"], selectbackground=T["HL_BG"], selectforeground=T["HL_FG"])

        self._act_frame.config(bg=T["BG"])
        self._act_text_wrap.config(bg=T["BG"])
        self._lbl_actions_title.config(bg=T["BG"], fg=T["PRI_BG"])
        self._text_actions.config(
            bg=T["PANEL_BG"], fg=T["LABEL_FG"], insertbackground=T["PRI_BG"],
            highlightbackground=T["GRID_LINE"], highlightcolor=T["PRI_BG"],
        )
        self._act_sb_x.config(style="App.Horizontal.TScrollbar")
        self._act_sb_y.config(style="App.Vertical.TScrollbar")
        self._status_frame.config(bg=T["BG"])
        self._lbl_status.config(bg=T["BG"])

        self._ctrl_frame.config(bg=T["BG"])
        self._ctrl_btn_row.config(bg=T["BG"])
        self._lbl_playback.config(bg=T["BG"], fg=T["LABEL_FG"])
        for btn in (self._btn_prev, self._btn_play, self._btn_next):
            btn.config(bg=T["SEC_BG"], fg=T["SEC_FG"], activebackground=T["ABTN2"])
        self._lbl_counter.config(bg=T["BG"], fg=T["LABEL_FG"])

        self._apply_widget_borders()
        self.after_idle(self._fit_window_for_algo)

    def set_input_fields(self, start_state, goal_state):
        """Hàm cập nhật text hiển thị trên 2 ô nhập liệu START và GOAL"""
        if hasattr(self, '_ent_start') and hasattr(self, '_ent_goal'):
            self._ent_start.delete(0, tk.END)
            self._ent_start.insert(0, " ".join(map(str, start_state)))
            self._ent_goal.delete(0, tk.END)
            self._ent_goal.insert(0, " ".join(map(str, goal_state)))

    def _on_apply_click(self):
        """Xử lý khi người dùng nhấn nút APPLY CUSTOM STATES"""
        if self._sliding: return
        if "on_apply_states" in self.cb:
            self.cb["on_apply_states"](self._ent_start.get(), self._ent_goal.get())

    def draw_board(self, state, highlight=None):
        T = self.T
        for ids in self.tile_items.values():
            for item in ids:
                self._canvas.delete(item)
        self.tile_items = {}
        if highlight is None:
            highlight = []
        for i, val in enumerate(state):
            x, y   = self._tile_xy(i)
            x2, y2 = x + TILE_SIZE, y + TILE_SIZE
            SD = 5
            if val == -1: # Trường hợp ô bị ẩn thông tin trong Belief State
                rect = self._canvas.create_rectangle(
                    x, y, x2, y2, fill=T["PANEL_BG"], outline=T["LABEL_FG"], width=2)
                txt = self._canvas.create_text(
                    x + TILE_SIZE // 2, y + TILE_SIZE // 2, text="?", font=FONT_TILE, fill=T["LABEL_FG"])
                self.tile_items[i] = (rect, txt)
            elif val == 0:
                r = self._canvas.create_rectangle(
                    x, y, x2, y2, fill=T["EMPTY_BG"], outline=T["EMPTY_BORD"], width=1, dash=(4, 4))
                self.tile_items[i] = (r,)
            else:
                hl = (i in highlight)
                bg = T["HL_BG"] if hl else T["TILE_BG"]
                fg = T["HL_FG"] if hl else T["TILE_FG"]
                bord = T["HL_BORD"] if hl else T["TILE_BORD"]
                sh = self._canvas.create_rectangle(
                    x+SD, y+SD, x2+SD, y2+SD, fill=T["SHADOW"], outline="", width=0)
                rect = self._canvas.create_rectangle(
                    x, y, x2, y2, fill=bg, outline=bord, width=2)
                txt = self._canvas.create_text(
                    x + TILE_SIZE // 2, y + TILE_SIZE // 2, text=str(val), font=FONT_TILE, fill=fg)
                self.tile_items[i] = (sh, rect, txt)

    def slide_tile(self, from_idx, to_idx, state_after, callback=None):
        ids = self.tile_items.get(from_idx, ())
        fx, fy = self._tile_xy(from_idx)
        tx, ty = self._tile_xy(to_idx)
        dx = (tx - fx) / SLIDE_STEPS
        dy = (ty - fy) / SLIDE_STEPS
        for item in self.tile_items.get(to_idx, ()):
            self._canvas.delete(item)
        self.tile_items.pop(to_idx, None)
        step = [0]
        def tick():
            step[0] += 1
            for item in ids:
                self._canvas.move(item, dx, dy)
            if step[0] < SLIDE_STEPS:
                self.after(SLIDE_MS, tick)
            else:
                for item in ids:
                    self._canvas.delete(item)
                self.tile_items.pop(from_idx, None)
                self.draw_board(state_after)
                self._sliding = False
                if callback:
                    callback()
        self._sliding = True
        tick()

    def show_solution(self, path, summary: dict):
        self.solution_path = path
        self.play_idx = 0
        self._lbl_steps.config(text=str(summary["steps"]))
        self._lbl_nodes.config(text=f"{summary['nodes_visited']:,}")
        self._lbl_time.config(text=f"{summary['elapsed_ms']:.1f}")
        algo_tag = summary.get("algorithm", self.algo)
        cost_part = f"  .  cost {summary['total_cost']}" if "total_cost" in summary else ""
        self._set_status(
            "done",
            f"Solved in {summary['steps']} moves{cost_part}  .  "
            f"{summary['elapsed_ms']:.0f} ms  .  {algo_tag}",
        )
        self._fill_listbox(path)
        
        # ─── TÍNH TOÁN CHUỖI HÀNH ĐỘNG DỊCH CHUYỂN Ô TRỐNG ───
        actions = []
        for i in range(1, len(path)):
            b1 = path[i-1].index(0)
            b2 = path[i].index(0)
            diff = b2 - b1
            if diff == -3:   actions.append("U")
            elif diff == 3:  actions.append("D")
            elif diff == -1: actions.append("L")
            elif diff == 1:  actions.append("R")
            
        action_str = " ".join(actions)
        self._set_actions_text(action_str)

        self._btn_prev.config(state="disabled")
        self._btn_next.config(state="normal")
        self._btn_play.config(state="normal")
        self._show_step(0)
        self._neon_flash()

    def set_status(self, mode, msg=""):
        self._set_status(mode, msg)

    def show_compare_dialog(self, results: list, winners: dict):
        """Cửa sổ bảng so sánh tất cả thuật toán trên cùng start/goal."""
        T = self.T
        win = tk.Toplevel(self)
        win.title("SO SANH THUAT TOAN")
        win.resizable(True, True)
        win.minsize(720, 380)
        win.configure(bg=T["BG"])

        hdr = tk.Label(
            win,
            text="Cung START / GOAL — double-click dong de xem loi giai tren UI",
            font=FONT_SUB, bg=T["BG"], fg=T["LABEL_FG"], anchor="w",
        )
        hdr.pack(fill="x", padx=14, pady=(12, 6))

        table_frame = tk.Frame(win, bg=T["BG"])
        table_frame.pack(fill="both", expand=True, padx=14, pady=4)

        cols = ("algo", "ok", "moves", "nodes", "time", "cost")
        tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=max(6, len(results)))
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        headings = [
            ("algo", "THUAT TOAN", 100),
            ("ok", "OK?", 52),
            ("moves", "NUOC DI", 72),
            ("nodes", "NODES", 110),
            ("time", "TIME (ms)", 88),
            ("cost", "COST", 64),
        ]
        for col, title, w in headings:
            tree.heading(col, text=title)
            tree.column(col, width=w, anchor="center")
        tree.column("algo", anchor="w")

        style = ttk.Style(win)
        style.theme_use("clam")
        style.configure(
            "Compare.Treeview",
            background=T["PANEL_BG"], foreground=T["LABEL_FG"],
            fieldbackground=T["PANEL_BG"], rowheight=26,
        )
        style.configure(
            "Compare.Treeview.Heading",
            background=T["METRIC_BG"], foreground=T["PRI_BG"], font=("Courier New", 9, "bold"),
        )
        style.map("Compare.Treeview", background=[("selected", T["HL_BG"])], foreground=[("selected", T["HL_FG"])])
        tree.configure(style="Compare.Treeview")

        self._compare_result_map = {}
        for r in results:
            iid = tree.insert("", "end", values=(
                r["algorithm"],
                "YES" if r["success"] else "NO",
                r["steps"] if r["success"] else "—",
                f"{r['nodes_visited']:,}",
                f"{r['elapsed_ms']:.1f}",
                r["total_cost"] if r.get("total_cost") is not None else "—",
            ))
            self._compare_result_map[iid] = r

        hint_lines = []
        labels_vn = {
            "fewest_moves": "It nuoc di nhat",
            "fewest_nodes": "It node expand nhat",
            "fastest": "Nhanh nhat (ms)",
            "same_path_length": "Do dai duong di",
            "note": "Ghi chu",
        }
        for key, val in winners.items():
            hint_lines.append(f"  • {labels_vn.get(key, key)}: {val}")
        hint_text = "\n".join(hint_lines) if hint_lines else "  (khong co goi y)"

        tk.Label(
            win, text="KET LUAN:\n" + hint_text,
            font=FONT_SUB, bg=T["BG"], fg=T["PRI_BG"], justify="left", anchor="w",
        ).pack(fill="x", padx=14, pady=(8, 12))

        def _on_pick(_event=None):
            sel = tree.selection()
            if not sel:
                return
            row = self._compare_result_map.get(sel[0])
            if row and row["success"] and "on_compare_pick" in self.cb:
                self.cb["on_compare_pick"](row)
                win.destroy()

        tree.bind("<Double-1>", _on_pick)

        win.transient(self)
        win.grab_set()
        self._center_toplevel(win)

    def _center_toplevel(self, win):
        win.update_idletasks()
        w, h = win.winfo_width(), win.winfo_height()
        if w < 100:
            win.geometry("760x400")
            win.update_idletasks()
            w, h = win.winfo_width(), win.winfo_height()
        x = (win.winfo_screenwidth() // 2) - (w // 2)
        y = (win.winfo_screenheight() // 2) - (h // 2)
        win.geometry(f"+{x}+{y}")

    def clear_solution(self):
        self._listbox.delete(0, tk.END)
        self._set_actions_text("")
        self._lbl_steps.config(text="—")
        self._lbl_nodes.config(text="—")
        self._lbl_time.config(text="—")
        self._lbl_counter.config(text="")
        self._btn_prev.config(state="disabled")
        self._btn_next.config(state="disabled")
        self._btn_play.config(state="disabled")
        self._stop_play()
        self.solution_path = []
        self.play_idx = 0

    def get_depth_limit(self):
        return self._depth_var.get()

    @property
    def is_sliding(self):
        return self._sliding

    # ── INTERNAL METHODS ──────────────────────────────────────────────

    def _set_status(self, mode, msg=""):
        colors = {
            "idle":      ("#555555", "IDLE"),
            "computing": ("#ffaa00", "COMPUTING"),
            "done":      ("#00ff88", "DONE"),
            "error":     ("#ff3355", "ERROR"),
        }
        col, label = colors.get(mode, ("#555", "IDLE"))
        self._dot_cv.itemconfig(self._dot, fill=col)
        self._dot_lbl.config(text=label, fg=col)
        if msg:
            self._lbl_status.config(text=msg, fg=col, bg=self.T.get("BG", self.cget("bg")))
        else:
            self._lbl_status.config(text="", bg=self.T.get("BG", self.cget("bg")))
        self._update_text_wraps()

    def _border_color(self):
        return self.T.get("UI_BORD", self.T.get("TILE_BORD", "#888"))

    def _apply_widget_borders(self):
        """Viền rõ cho nút, ô nhập, khung metric, listbox, v.v."""
        T = self.T
        bord = self._border_color()

        def _b(w, color=None):
            c = color or bord
            w.config(
                highlightthickness=UI_BORD_W,
                highlightbackground=c,
                highlightcolor=c,
            )

        for w in (
            self._btn_solve, self._btn_shuffle, self._btn_reset, self._btn_compare,
            self._btn_apply, self._btn_prev, self._btn_play, self._btn_next,
        ):
            _b(w)
        if hasattr(self, "_opt_menu"):
            _b(self._opt_menu)
        _b(self._ent_start)
        _b(self._ent_goal)
        _b(self._input_frame, T["GRID_LINE"])
        _b(self._lb_wrap, T["TILE_BORD"])
        _b(self._text_actions)
        _b(self._act_text_wrap, T["GRID_LINE"])
        _b(self._ctrl_frame, T["GRID_LINE"])
        for f in (self._f_steps, self._f_time, self._f_nodes):
            f.config(highlightthickness=UI_BORD_W, highlightbackground=bord)

    def _mk_btn(self, parent, text, cmd, primary=False, state="normal", w=None):
        T   = self.T
        kw  = dict(width=w) if w else {}
        fg  = T["PRI_FG"] if primary else T["SEC_FG"]
        bg  = T["PRI_BG"] if primary else T["SEC_BG"]
        abg = T["ABTN"]   if primary else T["ABTN2"]
        bord = T.get("UI_BORD", T["TILE_BORD"])
        return tk.Button(parent, text=text, command=cmd,
                         font=FONT_BTN, bg=bg, fg=fg,
                         padx=10, pady=5, relief="flat", bd=0,
                         activebackground=abg, activeforeground=fg,
                         cursor="hand2", state=state,
                         highlightthickness=UI_BORD_W,
                         highlightbackground=bord,
                         highlightcolor=bord, **kw)

    def _mk_play_btn(self, parent, text, cmd, state="normal", w=None):
        """Nút playback — cỡ chữ và vùng bấm lớn hơn nút thường."""
        T = self.T
        kw = dict(width=w) if w else {}
        return tk.Button(
            parent, text=text, command=cmd,
            font=FONT_PLAY_BTN, bg=T["SEC_BG"], fg=T["SEC_FG"],
            padx=18, pady=12, relief="flat", bd=0,
            activebackground=T["ABTN2"], activeforeground=T["SEC_FG"],
            cursor="hand2", state=state,
            highlightthickness=UI_BORD_W,
            highlightbackground=T.get("UI_BORD", T["TILE_BORD"]),
            highlightcolor=T.get("UI_BORD", T["TILE_BORD"]),
            **kw,
        )

    def _set_actions_text(self, text: str):
        self._text_actions.config(state=tk.NORMAL)
        self._text_actions.delete("1.0", tk.END)
        if text:
            self._text_actions.insert("1.0", text)
        self._text_actions.config(state=tk.DISABLED)

    def _mk_metric(self, parent, label):
        T = self.T
        f = tk.Frame(
            parent, bg=T["METRIC_BG"], padx=12, pady=8,
            width=METRIC_BOX_W, height=METRIC_BOX_H,
            highlightthickness=1, highlightbackground=T["GRID_LINE"],
        )
        f.pack_propagate(False)
        tk.Label(
            f, text=label, font=("Courier New", 9),
            bg=T["METRIC_BG"], fg=T["LABEL_FG"], anchor="w",
        ).pack(fill="x")
        v = tk.Label(
            f, text="—", font=FONT_METRIC_VAL,
            bg=T["METRIC_BG"], fg=T["PRI_BG"], anchor="w",
        )
        v.pack(fill="x", pady=(4, 0))
        return f, v

    def _draw_grid_lines(self):
        T = self.T
        board_size = 3 * TILE_SIZE + 4 * GAP
        for i in range(0, board_size + 1, TILE_SIZE + GAP):
            self._canvas.create_line(i, 0, i, board_size, fill=T["GRID_LINE"], tags="grid", width=1)
            self._canvas.create_line(0, i, board_size, i, fill=T["GRID_LINE"], tags="grid", width=1)

    def _tile_xy(self, idx):
        r, c = divmod(idx, 3)
        return GAP + c * (TILE_SIZE + GAP), GAP + r * (TILE_SIZE + GAP)

    def _on_canvas_click(self, event):
        if self._play_job or self._sliding:
            return
        col = (event.x - GAP) // (TILE_SIZE + GAP)
        row = (event.y - GAP) // (TILE_SIZE + GAP)
        if 0 <= col < 3 and 0 <= row < 3:
            self.cb["on_tile_click"](row * 3 + col)

    def _fill_listbox(self, path):
        self._listbox.delete(0, tk.END)
        self._listbox.insert(tk.END, "  [START]")
        for i in range(1, len(path)):
            prev, cur = path[i-1], path[i]
            moved = next(v for j, v in enumerate(cur) if v != prev[j] and v != 0)
            self._listbox.insert(tk.END, f"  step {i:>3}  ->  tile {moved}")

    def _on_list_select(self, event):
        sel = self._listbox.curselection()
        if sel and self.solution_path:
            self._show_step(sel[0])

    def _show_step(self, idx):
        if not self.solution_path:
            return
        idx = max(0, min(idx, len(self.solution_path) - 1))
        self.play_idx = idx
        cur = self.solution_path[idx]
        hl  = []
        if idx > 0:
            prev = self.solution_path[idx - 1]
            hl   = [i for i, v in enumerate(cur) if v != prev[i] and v != 0]
        self.draw_board(cur, hl)
        self._listbox.selection_clear(0, tk.END)
        self._listbox.selection_set(idx)
        self._listbox.see(idx)
        total = len(self.solution_path) - 1
        self._btn_prev.config(state="disabled" if idx == 0    else "normal")
        self._btn_next.config(state="disabled" if idx == total else "normal")
        self._lbl_counter.config(text=f"{idx} / {total}")

    def _step_back(self):
        if self._play_job: self._stop_play()
        self._show_step(self.play_idx - 1)

    def _step_fwd(self):
        if self._play_job: self._stop_play()
        self._show_step(self.play_idx + 1)

    def _auto_play(self):
        if self._play_job: self._stop_play(); return
        self._btn_play.config(text="⏸ PAUSE")
        self._tick()

    def _tick(self):
        if self.play_idx >= len(self.solution_path) - 1:
            self._stop_play(); return
        self._show_step(self.play_idx + 1)
        self._play_job = self.after(self._anim_delay.get(), self._tick)

    def _stop_play(self):
        if self._play_job:
            self.after_cancel(self._play_job)
            self._play_job = None
        self._btn_play.config(text="▶  PLAY")

    def _neon_flash(self, times=4):
        board_size = 3 * TILE_SIZE + 4 * GAP
        ov = self._canvas.create_rectangle(
            0, 0, board_size, board_size,
            fill="", outline=self.T.get("HL_BORD", "#ff007f"), width=4)
        def flash(n):
            if n <= 0:
                self._canvas.delete(ov); return
            vis = self._canvas.itemcget(ov, "outline")
            self._canvas.itemconfig(ov,
                outline=self.T.get("HL_BORD", "#ff007f") if vis == "" else "")
            self.after(120, lambda: flash(n - 1))
        flash(times * 2)