import random

DEFAULT_GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)
GRID_SIZE = 3


class PuzzleModel:
    def __init__(self):
        self.goal = DEFAULT_GOAL
        self._state = DEFAULT_GOAL
        self.start_state = DEFAULT_GOAL
        self.shuffle()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        self._state = tuple(new_state)

    def is_goal(self):
        return self._state == self.goal

    def reset(self):
        # Reset về lại trạng thái ban đầu trước khi nhấn Giải
        self._state = self.start_state

    @staticmethod
    def find_blank(state):
        return state.index(0)

    @staticmethod
    def get_moves(state):
        b = state.index(0)
        r, c = divmod(b, GRID_SIZE)
        moves = []
        if r > 0: moves.append(b - GRID_SIZE)
        if r < 2: moves.append(b + GRID_SIZE)
        if c > 0: moves.append(b - 1)
        if c < 2: moves.append(b + 1)
        return moves

    @staticmethod
    def swap(state, i, j):
        lst = list(state)
        lst[i], lst[j] = lst[j], lst[i]
        return tuple(lst)

    def move(self, tile_idx):
        blank = self._state.index(0)
        if tile_idx in PuzzleModel.get_moves(self._state):
            self._state = PuzzleModel.swap(self._state, blank, tile_idx)
            return True
        return False

    def shuffle(self, steps=120):
        # Luôn luôn xáo trộn bắt đầu xuất phát từ trạng thái đích (Goal) hiện tại
        s = self.goal
        prev = None
        for _ in range(steps):
            moves = [m for m in PuzzleModel.get_moves(s) if m != prev]
            b = s.index(0)
            m = random.choice(moves)
            prev = b
            s = PuzzleModel.swap(s, b, m)
        self._state = s
        self.start_state = s  # Ghi nhớ cấu hình này để phục vụ Reset