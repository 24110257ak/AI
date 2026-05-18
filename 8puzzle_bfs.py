"""
8-Puzzle Solver  ·  v2  ·  Cyberpunk / Sci-Fi theme
────────────────────────────────────────────────────
Tính năng mới so với v1:
  • Theme Cyberpunk (nền tối, neon cyan/pink, viền lưới)
  • Hiệu ứng trượt mượt (sliding animation) khi ô di chuyển
  • Thanh tốc độ (Speed Slider) điều chỉnh ANIM_DELAY
  • Chọn thuật toán: BFS / DFS / A* (Manhattan)
  • Chấm trạng thái (status dot): Idle / Computing / Done / Error
  • Neo-Brutalism shadow cho các ô số
  • Hiệu ứng nhấp nháy neon khi Solve xong
────────────────────────────────────────────────────
Chạy: python 8puzzle_bfs_v2.py
Yêu cầu: Python 3.8+ (stdlib only, không cần cài thêm)
"""

import tkinter as tk
from tkinter import messagebox
from collections import deque
import random
import time

# ═══════════════════════════════════════════════════════════════════
#  LOGIC
# ═══════════════════════════════════════════════════════════════════

GOAL = (1, 2, 3, 8, 0, 4, 7, 6, 5)

def find_blank(s):
    return s.index(0)

def get_moves(s):
    b = find_blank(s)
    r, c = divmod(b, 3)
    ms = []
    if r > 0: ms.append(b - 3)
    if r < 2: ms.append(b + 3)
    if c > 0: ms.append(b - 1)
    if c < 2: ms.append(b + 1)
    return ms

def swap(s, i, j):
    lst = list(s); lst[i], lst[j] = lst[j], lst[i]
    return tuple(lst)

def is_solvable(s):
    t = [x for x in s if x != 0]
    inv = sum(1 for i in range(len(t)) for j in range(i+1,len(t)) if t[i]>t[j])
    return inv % 2 == 0

def shuffle_puzzle():
    s = list(GOAL)
    for _ in range(400):
        b = s.index(0)
        m = random.choice(get_moves(tuple(s)))
        s[b], s[m] = s[m], s[b]
    s = tuple(s)
    if not is_solvable(s):
        i, j = s.index(1), s.index(2)
        lst = list(s); lst[i], lst[j] = lst[j], lst[i]
        s = tuple(lst)
    return s

# ── BFS ─────────────────────────────────────────────────────────────
def bfs(start):
    if start == GOAL: return [start], 1
    queue = deque([(start, [start])])
    visited = {start}; nodes = 1
    while queue:
        state, path = queue.popleft()
        b = find_blank(state)
        for m in get_moves(state):
            nxt = swap(state, b, m)
            if nxt not in visited:
                visited.add(nxt); nodes += 1
                np = path + [nxt]
                if nxt == GOAL: return np, nodes
                queue.append((nxt, np))
    return None, 0



# ═══════════════════════════════════════════════════════════════════
#  THEME  —  Cyberpunk / Sci-Fi
# ═══════════════════════════════════════════════════════════════════

BG          = "#0a0f1d"      # near-black navy
PANEL_BG    = "#0e1525"      # slightly lighter panel
GRID_LINE   = "#1a2540"      # subtle grid lines on bg
TILE_BG     = "#111c35"      # tile fill
TILE_FG     = "#00f0ff"      # cyan neon text
TILE_BORDER = "#00f0ff"      # cyan border
EMPTY_BG    = "#0a0f1d"      # invisible
EMPTY_BORD  = "#1a2540"
HL_BG       = "#1a003a"      # purple tint on highlight
HL_FG       = "#ff007f"      # hot pink
HL_BORD     = "#ff007f"
SHADOW      = "#001a33"      # neo-brutalism flat shadow
BTN_PRI_BG  = "#00f0ff"
BTN_PRI_FG  = "#0a0f1d"
BTN_SEC_BG  = "#0e1525"
BTN_SEC_FG  = "#00f0ff"
LABEL_FG    = "#7ab8d4"
METRIC_BG   = "#0b1220"
STATUS_FG   = "#00f0ff"

FONT_TITLE  = ("Courier New", 20, "bold")
FONT_SUB    = ("Courier New", 10)
FONT_TILE   = ("Courier New", 26, "bold")
FONT_BTN    = ("Courier New", 10, "bold")
FONT_INFO   = ("Courier New", 10)
FONT_STEP   = ("Courier New", 10)
FONT_METRIC = ("Courier New", 18, "bold")

TILE_SIZE   = 88
GAP         = 8
SLIDE_STEPS = 8      # frames per slide animation
SLIDE_MS    = 12     # ms per frame  (~96ms total slide)

# ═══════════════════════════════════════════════════════════════════
#  APP
# ═══════════════════════════════════════════════════════════════════

class PuzzleApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("8-PUZZLE  ·  AI SOLVER")
        self.configure(bg=BG)
        self.resizable(False, False)

        self.state      = shuffle_puzzle()
        self.solution   = []
        self.play_idx   = 0
        self._play_job  = None
        self._sliding   = False          # lock during animation
        self._anim_delay = tk.IntVar(value=350)

        self._build_ui()
        self._draw_board(self.state)
        self._set_status("idle")

    # ── BUILD UI ─────────────────────────────────────────────────────

    def _build_ui(self):
        # ── title bar ────────────────────────────────────────────────
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=20, pady=(18, 0))
        tk.Label(top, text="8-PUZZLE", font=FONT_TITLE,
                 bg=BG, fg=BTN_PRI_BG).pack(side="left")
        tk.Label(top, text="  //  AI SOLVER", font=("Courier New", 12),
                 bg=BG, fg=LABEL_FG).pack(side="left", pady=(6,0))

        # ── status dot ───────────────────────────────────────────────
        dot_frame = tk.Frame(top, bg=BG)
        dot_frame.pack(side="right", padx=(0,4))
        self.dot_canvas = tk.Canvas(dot_frame, width=12, height=12,
                                    bg=BG, highlightthickness=0)
        self.dot_canvas.pack(side="left", pady=(6,0))
        self.dot_item = self.dot_canvas.create_oval(1,1,11,11, fill="#555", outline="")
        self.lbl_dot = tk.Label(dot_frame, text="IDLE", font=("Courier New",9,"bold"),
                                bg=BG, fg="#555")
        self.lbl_dot.pack(side="left", padx=(4,0), pady=(6,0))

        # ── main body ────────────────────────────────────────────────
        body = tk.Frame(self, bg=BG)
        body.pack(padx=20, pady=12)

        left  = tk.Frame(body, bg=BG)
        left.pack(side="left", anchor="n")
        right = tk.Frame(body, bg=BG, padx=16)
        right.pack(side="left", anchor="n")

        # ── BOARD (left) ──────────────────────────────────────────────
        board_size = 3 * TILE_SIZE + 4 * GAP
        self.canvas = tk.Canvas(left, width=board_size, height=board_size,
                                bg=BG, highlightthickness=0)
        self.canvas.pack()
        self._draw_grid_lines()
        self.canvas.bind("<Button-1>", self._on_click)
        self.tile_items   = {}   # idx -> (shadow_id, rect_id, text_id)

        # ── action buttons ───────────────────────────────────────────
        btn_row = tk.Frame(left, bg=BG)
        btn_row.pack(pady=(10,0), fill="x")
        self.btn_solve = self._btn(btn_row, "▶  SOLVE", self._solve,
                                   primary=True)
        self.btn_solve.pack(side="left", padx=(0,8))
        self._btn(btn_row, "SHUFFLE", self._shuffle).pack(side="left", padx=(0,8))
        self._btn(btn_row, "RESET",   self._reset).pack(side="left")

        # ── speed slider ─────────────────────────────────────────────
        spd_row = tk.Frame(left, bg=BG)
        spd_row.pack(pady=(10,0), fill="x")
        tk.Label(spd_row, text="SPEED:", font=FONT_SUB,
                 bg=BG, fg=LABEL_FG).pack(side="left")
        self.spd_val_lbl = tk.Label(spd_row, text="350 ms", font=FONT_SUB,
                                    bg=BG, fg=BTN_PRI_BG, width=7)
        self.spd_val_lbl.pack(side="right")
        spd_slider = tk.Scale(spd_row, from_=50, to=1200,
                              orient="horizontal", variable=self._anim_delay,
                              showvalue=False, bg=BG, fg=BTN_PRI_BG,
                              troughcolor=PANEL_BG, highlightthickness=0,
                              activebackground=BTN_PRI_BG,
                              command=self._on_speed_change)
        spd_slider.pack(side="left", fill="x", expand=True, padx=(8,4))

        # ── status label ─────────────────────────────────────────────
        self.lbl_status = tk.Label(left, text="", font=FONT_INFO,
                                   bg=BG, fg=STATUS_FG, anchor="w")
        self.lbl_status.pack(pady=(8,0), fill="x")

        # ── RIGHT PANEL ───────────────────────────────────────────────
        tk.Label(right, text="SOLUTION PATH", font=("Courier New",11,"bold"),
                 bg=BG, fg=BTN_PRI_BG).pack(anchor="w")

        # metrics row
        met = tk.Frame(right, bg=BG)
        met.pack(anchor="w", pady=(10,10), fill="x")
        steps_f, self.lbl_steps = self._metric(met, "MOVES")
        steps_f.pack(side="left", padx=(0,10))
        nodes_f, self.lbl_nodes = self._metric(met, "NODES VISITED")
        nodes_f.pack(side="left", padx=(0,10))
        time_f,  self.lbl_time  = self._metric(met, "TIME (ms)")
        time_f.pack(side="left")

        # listbox
        lb_frame = tk.Frame(right, bg=TILE_BORDER, padx=1, pady=1)
        lb_frame.pack(fill="both", expand=True)
        inner = tk.Frame(lb_frame, bg=BG)
        inner.pack(fill="both", expand=True)

        sb = tk.Scrollbar(inner, bg=PANEL_BG, troughcolor=BG,
                          activebackground=BTN_PRI_BG)
        sb.pack(side="right", fill="y")
        self.listbox = tk.Listbox(inner, width=28, height=16,
                                  font=FONT_STEP, bg=BG, fg=LABEL_FG,
                                  selectbackground=HL_BG,
                                  selectforeground=HL_FG,
                                  activestyle="none", relief="flat",
                                  yscrollcommand=sb.set,
                                  highlightthickness=0, bd=0)
        self.listbox.pack(side="left", fill="both", expand=True)
        sb.config(command=self.listbox.yview)
        self.listbox.bind("<<ListboxSelect>>", self._on_list_select)

        # playback
        ctrl = tk.Frame(right, bg=BG)
        ctrl.pack(pady=(10,0), fill="x")
        self.btn_prev = self._btn(ctrl, "◀", self._step_back, state="disabled", w=4)
        self.btn_prev.pack(side="left", padx=(0,6))
        self.btn_play = self._btn(ctrl, "▶ PLAY", self._auto_play, state="disabled")
        self.btn_play.pack(side="left", padx=(0,6))
        self.btn_next = self._btn(ctrl, "▶", self._step_fwd, state="disabled", w=4)
        self.btn_next.pack(side="left")
        self.lbl_step_counter = tk.Label(ctrl, text="", font=FONT_INFO,
                                         bg=BG, fg=LABEL_FG)
        self.lbl_step_counter.pack(side="left", padx=(12,0))

    # ── helpers ──────────────────────────────────────────────────────

    def _btn(self, parent, text, cmd, primary=False, state="normal", w=None):
        kw = dict(width=w) if w else {}
        fg  = BTN_PRI_FG if primary else BTN_SEC_FG
        bg  = BTN_PRI_BG if primary else BTN_SEC_BG
        abg = "#00c8d4"   if primary else "#1a2a44"
        b = tk.Button(parent, text=text, command=cmd,
                      font=FONT_BTN, bg=bg, fg=fg,
                      padx=10, pady=5, relief="flat", bd=0,
                      activebackground=abg, activeforeground=fg,
                      cursor="hand2", state=state,
                      highlightthickness=1,
                      highlightbackground=TILE_BORDER, **kw)
        return b

    def _metric(self, parent, label):
        f = tk.Frame(parent, bg=METRIC_BG, padx=10, pady=6,
                     highlightthickness=1,
                     highlightbackground=GRID_LINE)
        tk.Label(f, text=label, font=("Courier New",8),
                 bg=METRIC_BG, fg=LABEL_FG).pack(anchor="w")
        v = tk.Label(f, text="—", font=FONT_METRIC,
                     bg=METRIC_BG, fg=BTN_PRI_BG)
        v.pack(anchor="w")
        return f, v

    def _draw_grid_lines(self):
        board_size = 3 * TILE_SIZE + 4 * GAP
        for i in range(0, board_size+1, TILE_SIZE+GAP):
            self.canvas.create_line(i, 0, i, board_size, fill=GRID_LINE, width=1)
            self.canvas.create_line(0, i, board_size, i, fill=GRID_LINE, width=1)

    def _on_speed_change(self, val):
        self.spd_val_lbl.config(text=f"{int(float(val))} ms")

    def _set_status(self, mode, msg=""):
        colors = {"idle":     ("#555555", "IDLE"),
                  "computing":("#ffaa00", "COMPUTING"),
                  "done":     ("#00ff88", "DONE"),
                  "error":    ("#ff3355", "ERROR")}
        col, label = colors.get(mode, ("#555", "IDLE"))
        self.dot_canvas.itemconfig(self.dot_item, fill=col)
        self.lbl_dot.config(text=label, fg=col)
        if msg:
            self.lbl_status.config(text=msg, fg=col)

    # ── BOARD DRAWING ─────────────────────────────────────────────────

    def _tile_xy(self, idx):
        r, c = divmod(idx, 3)
        x = GAP + c * (TILE_SIZE + GAP)
        y = GAP + r * (TILE_SIZE + GAP)
        return x, y

    def _draw_board(self, state, highlight=None):
        # delete only tile items (keep grid lines)
        for ids in self.tile_items.values():
            for item in ids:
                self.canvas.delete(item)
        self.tile_items = {}
        if highlight is None: highlight = []

        for i, val in enumerate(state):
            x, y = self._tile_xy(i)
            x2, y2 = x + TILE_SIZE, y + TILE_SIZE
            SD = 5  # shadow offset

            if val == 0:
                # empty slot — faint border only
                r = self.canvas.create_rectangle(
                    x, y, x2, y2, fill=EMPTY_BG,
                    outline=EMPTY_BORD, width=1, dash=(4,4))
                self.tile_items[i] = (r,)
            else:
                hl = (i in highlight)
                bg    = HL_BG    if hl else TILE_BG
                fg    = HL_FG    if hl else TILE_FG
                bord  = HL_BORD  if hl else TILE_BORDER

                # neo-brutalism flat shadow
                sh = self.canvas.create_rectangle(
                    x+SD, y+SD, x2+SD, y2+SD,
                    fill=SHADOW, outline="", width=0)
                rect = self.canvas.create_rectangle(
                    x, y, x2, y2,
                    fill=bg, outline=bord, width=2)
                txt = self.canvas.create_text(
                    x + TILE_SIZE//2, y + TILE_SIZE//2,
                    text=str(val), font=FONT_TILE, fill=fg)
                self.tile_items[i] = (sh, rect, txt)

    # ── SLIDING ANIMATION ─────────────────────────────────────────────

    def _slide_tile(self, from_idx, to_idx, state_after, callback):
        """Smoothly slide the tile at from_idx into to_idx."""
        # grab existing canvas items for the moving tile
        ids = self.tile_items.get(from_idx, ())
        fx, fy = self._tile_xy(from_idx)
        tx, ty = self._tile_xy(to_idx)
        dx = (tx - fx) / SLIDE_STEPS
        dy = (ty - fy) / SLIDE_STEPS

        # hide destination slot drawing
        for item in self.tile_items.get(to_idx, ()):
            self.canvas.delete(item)
        self.tile_items.pop(to_idx, None)

        step = [0]
        def tick():
            step[0] += 1
            for item in ids:
                self.canvas.move(item, dx, dy)
            if step[0] < SLIDE_STEPS:
                self.after(SLIDE_MS, tick)
            else:
                # clean up and redraw final state
                for item in ids:
                    self.canvas.delete(item)
                self.tile_items.pop(from_idx, None)
                self._draw_board(state_after)
                self._sliding = False
                if callback: callback()
        tick()

    def _move_tile(self, tile_idx, callback=None):
        """Move tile at tile_idx into the blank, with animation."""
        blank = find_blank(self.state)
        new_state = swap(self.state, blank, tile_idx)
        self._sliding = True
        self.state = new_state
        self._slide_tile(tile_idx, blank, new_state, callback)

    # ── INTERACTIONS ─────────────────────────────────────────────────

    def _on_click(self, event):
        if self._play_job or self._sliding: return
        col = (event.x - GAP) // (TILE_SIZE + GAP)
        row = (event.y - GAP) // (TILE_SIZE + GAP)
        if not (0 <= col < 3 and 0 <= row < 3): return
        idx = row * 3 + col
        if idx in get_moves(self.state):
            self.solution = []; self.play_idx = 0
            self._clear_solution_ui()
            self._set_status("idle", "")
            self._move_tile(idx)

    def _solve(self):
        if self._play_job or self._sliding: return
        if self.state == GOAL:
            self._set_status("done", "Already at goal state.")
            return

        self._set_status("computing", "Running BFS…")
        self.lbl_status.config(fg="#ffaa00")
        self.update_idletasks()

        t0 = time.perf_counter()
        path, nodes = bfs(self.state)
        elapsed = time.perf_counter() - t0

        if not path:
            self._set_status("error", "No solution found.")
            return

        self.solution = path
        self.play_idx = 0
        steps = len(path) - 1

        self.lbl_steps.config(text=str(steps))
        self.lbl_nodes.config(text=f"{nodes:,}")
        self.lbl_time.config(text=f"{elapsed*1000:.1f}")
        self._set_status("done", f"Solved in {steps} moves  ·  {elapsed*1000:.0f} ms")

        self._fill_list(path)
        self._enable_controls()
        self._show_step(0)
        self._neon_flash()

    def _neon_flash(self, times=4):
        """Quick neon flash on tile borders to celebrate solve."""
        board_size = 3 * TILE_SIZE + 4 * GAP
        overlay = self.canvas.create_rectangle(
            0, 0, board_size, board_size,
            fill="", outline=HL_BORD, width=4)
        def flash(n):
            if n <= 0:
                self.canvas.delete(overlay); return
            vis = self.canvas.itemcget(overlay, "outline")
            self.canvas.itemconfig(overlay,
                outline=HL_BORD if vis == "" else "")
            self.after(120, lambda: flash(n-1))
        flash(times * 2)

    def _fill_list(self, path):
        self.listbox.delete(0, tk.END)
        self.listbox.insert(tk.END, "  [START]")
        for i in range(1, len(path)):
            prev, cur = path[i-1], path[i]
            moved = next(v for j, v in enumerate(cur) if v != prev[j] and v != 0)
            self.listbox.insert(tk.END, f"  step {i:>2}  →  tile {moved}")

    def _on_list_select(self, event):
        sel = self.listbox.curselection()
        if sel and self.solution:
            self._show_step(sel[0])

    def _show_step(self, idx):
        if not self.solution: return
        idx = max(0, min(idx, len(self.solution)-1))
        self.play_idx = idx
        cur = self.solution[idx]
        hl = []
        if idx > 0:
            prev = self.solution[idx-1]
            hl = [i for i, v in enumerate(cur) if v != prev[i] and v != 0]
        self._draw_board(cur, hl)
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(idx)
        self.listbox.see(idx)
        total = len(self.solution)-1
        self.btn_prev.config(state="disabled" if idx == 0 else "normal")
        self.btn_next.config(state="disabled" if idx == total else "normal")
        self.lbl_step_counter.config(text=f"{idx} / {total}")

    def _step_back(self):
        if self._play_job: self._stop_play()
        self._show_step(self.play_idx - 1)

    def _step_fwd(self):
        if self._play_job: self._stop_play()
        self._show_step(self.play_idx + 1)

    def _auto_play(self):
        if self._play_job: self._stop_play(); return
        self.btn_play.config(text="⏸ PAUSE")
        self._tick_play()

    def _tick_play(self):
        if self.play_idx >= len(self.solution) - 1:
            self._stop_play(); return
        self._show_step(self.play_idx + 1)
        delay = self._anim_delay.get()
        self._play_job = self.after(delay, self._tick_play)

    def _stop_play(self):
        if self._play_job:
            self.after_cancel(self._play_job)
            self._play_job = None
        self.btn_play.config(text="▶ PLAY")

    def _enable_controls(self):
        self.btn_prev.config(state="disabled")
        self.btn_next.config(state="normal")
        self.btn_play.config(state="normal")

    def _clear_solution_ui(self):
        self.listbox.delete(0, tk.END)
        self.lbl_steps.config(text="—")
        self.lbl_nodes.config(text="—")
        self.lbl_time.config(text="—")
        self.lbl_step_counter.config(text="")
        self.btn_prev.config(state="disabled")
        self.btn_next.config(state="disabled")
        self.btn_play.config(state="disabled")
        self._stop_play()

    def _shuffle(self):
        if self._sliding: return
        self._stop_play()
        self.state = shuffle_puzzle()
        self.solution = []; self.play_idx = 0
        self._draw_board(self.state)
        self._clear_solution_ui()
        self._set_status("idle", "")

    def _reset(self):
        if self._sliding: return
        self._stop_play()
        self.state = GOAL
        self.solution = []; self.play_idx = 0
        self._draw_board(self.state)
        self._clear_solution_ui()
        self._set_status("idle", "")


# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = PuzzleApp()
    app.mainloop()