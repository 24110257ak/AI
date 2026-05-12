import random
import copy

class ModelBasedReflexAgent:
    def __init__(self):
        self.state = None
    
    def find_blank(self):
        for i in range(3):
            for j in range(3):
                if self.state[i][j] == 0:
                    return i, j
    
    def get_best_action(self):
        """Model-Based Reflex Agent - Rule Match"""
        i, j = self.find_blank()
        directions = [(-1, 0, "Up"), (0, -1, "Left"), (0, 1, "Right"), (1, 0, "Down")]
        best_action = None
        best_score = float('inf')
        
        for di, dj, action in directions:
            ni, nj = i + di, j + dj
            if 0 <= ni < 3 and 0 <= nj < 3:
                tile = self.state[ni][nj]
                goal_i = (tile - 1) // 3 if tile != 0 else 2
                goal_j = (tile - 1) % 3 if tile != 0 else 2
                score = abs(ni - goal_i) + abs(nj - goal_j)
                if score < best_score:
                    best_score = score
                    best_action = action
        return best_action
    
    def apply_action(self, action):
        i, j = self.find_blank()
        moves = {"Up": (-1,0), "Down":(1,0), "Left":(0,-1), "Right":(0,1)}
        di, dj = moves[action]
        ni, nj = i + di, j + dj
        self.state[i][j], self.state[ni][nj] = self.state[ni][nj], self.state[i][j]


# ====================== HIỂN THỊ ======================
def print_board(state, title=""):
    print(title)
    print("╔═══╦═══╦═══╗")
    for row in state:
        print("║", end="")
        for num in row:
            print(f" {num if num != 0 else ' ':1} ", end="║")
        print()
        print("╠═══╬═══╬═══╣")
    print("╚═══╩═══╩═══╝\n")


# ====================== MAIN ======================
if __name__ == "__main__":
    # Tạo bàn cờ ngẫu nhiên
    goal = [[1,2,3],[4,5,6],[7,8,0]]
    state = copy.deepcopy(goal)
    
    # Trộn bàn cờ
    for _ in range(25):
        i, j = [(x,y) for x in range(3) for y in range(3) if state[x][y]==0][0]
        moves = []
        if i>0: moves.append((i-1,j))
        if i<2: moves.append((i+1,j))
        if j>0: moves.append((i,j-1))
        if j<2: moves.append((i,j+1))
        ni, nj = random.choice(moves)
        state[i][j], state[ni][nj] = state[ni][nj], state[i][j]
    
    agent = ModelBasedReflexAgent()
    agent.state = copy.deepcopy(state)
    
    actions = []
    max_actions = 10   # ← Giới hạn chỉ 10 action
    
    print("=== 8-PUZZLE - MODEL-BASED REFLEX AGENT ===\n")
    print_board(state, "BÀN CỜ BAN ĐẦU:")
    
    # Thực hiện tối đa 10 action
    for step in range(max_actions):
        action = agent.get_best_action()
        if not action:
            break
        actions.append(action)
        agent.apply_action(action)
    
    # Kết quả cuối cùng
    print_board(agent.state, "BÀN CỜ SAU 10 ACTION:")
    
    print("DANH SÁCH ACTION:")
    print(actions)
    print(f"Tổng số action: {len(actions)} / 10")