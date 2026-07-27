import tkinter as tk
from tkinter import messagebox
import collections
import random
import time
fromtyping import List, Tuple, Optional
class PuzzleState:
    def __init__(self, board: List[List[int]], moves: int = 0, prev: Optional['PuzzleState'] = None):
        self.board = board
        self.moves = moves
        self.prev = prev
        
        self.blank_pos = self.find_blank()

    def find_blank(self) -> Tuple[int, int]:
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == 0:
                    return (i, j)
        return (-1, - 1)

    def __eq__(self, other):
        return self.board == other.board

    def __hash__(self):
        return hash(tuple(tuple(row) for row in self.board))

    def __repr__(self):
        return f"State(moves={self.moves})\n{self.board}"

    def get_neighbors(self) -> List['PuzzleState']:
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  
        i, j = self.blank_pos
        for di, dj in directions:
            ni, nj = i + di, j + dj
            if 0 <= ni < 3 and 0 <= nj < 3:
                new_board = [row[:] for row in self.board]
                new_board[i][j], new_board[ni][nj] = new_board[ni][nj], new_board[i][j]
                neighbors.append(PuzzleState(new_board, self.moves + 1, self))
        return neighbors

def solve_8puzzle(initial_board: List[List[int]], method: str = 'bfs') -> Optional[PuzzleState]:
    goal_board = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    
    initial_state = PuzzleState(initial_board)
    
    if initial_state.board == goal_board:
        return initial_state
    
    if method.lower() == 'bfs':
        queue = collections.deque([initial_state])
        visited = set([initial_state])
    elif method.lower() == 'dfs':
        stack = [initial_state]
        visited = set([initial_state])
    else:
        raise ValueError("Method must be 'bfs' or 'dfs'")
    
    while True:
        if not (queue if method.lower() == 'bfs' else stack):
            return None  
        
        if method.lower() == 'bfs':
            current = queue.popleft()
        else:
            current = stack.pop()
        
        if current.board == goal_board:
            return current
        
        neighbors = current.get_neighbors()
        if method.lower() == 'dfs':
            random.shuffle(neighbors)  
        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                if method.lower() == 'bfs':
                    queue.append(neighbor)
                else:
                    stack.append(neighbor)

class EightPuzzleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver - BFS & DFS")
        self.root.geometry("400x500")
        
        self.goal_board = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
        self.current_board = [row[:] for row in self.goal_board]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.solution_path = []
        self.anim_index = 0
        self.is_animating = False
        
        self.manual_moves = 0
        self.move_history = [] 
        self.is_solvable = True
        self.hint_active = False
        self.difficulty_var = tk.StringVar(value="Medium")
        
        self.setup_ui()
        self.update_board()
        
    def setup_ui(self):
       
        grid_frame = tk.Frame(self.root)
        grid_frame.pack(pady=10)
        
        for i in range(3):
            for j in range(3):
                btn = tk.Button(grid_frame, width=4, height=2, font=('Arial', 16, 'bold'),
                               command=lambda row=i, col=j: self.move_tile(row, col),
                               bg='lightblue', fg='black')
                btn.grid(row=i, column=j, padx=2, pady=2)
                self.buttons[i][j] = btn
        

        ctrl_frame = tk.Frame(self.root)
        ctrl_frame.pack(pady=10)
        
        
        diff_frame = tk.Frame(ctrl_frame)
        diff_frame.pack(side=tk.LEFT, padx=5)
        tk.Label(diff_frame, text="Diff:").pack()
        tk.OptionMenu(diff_frame, self.difficulty_var, "Easy", "Medium", "Hard").pack()
        
        tk.Button(ctrl_frame, text="Shuffle", command=self.shuffle, bg='orange', width=8).pack(side=tk.LEFT, padx=5)
        tk.Button(ctrl_frame, text="Hint", command=self.show_hint, bg='purple', width=8).pack(side=tk.LEFT, padx=5)
        tk.Button(ctrl_frame, text="Undo", command=self.undo_move, bg='gray', width=8).pack(side=tk.LEFT, padx=5)
        tk.Button(ctrl_frame, text="Solve BFS", command=lambda: self.solve('bfs'), bg='green', width=8).pack(side=tk.LEFT, padx=2)
        tk.Button(ctrl_frame, text="Solve DFS", command=lambda: self.solve('dfs'), bg='green', width=8).pack(side=tk.LEFT, padx=2)
        tk.Button(ctrl_frame, text="Reset", command=self.reset, bg='red', width=8).pack(side=tk.LEFT, padx=5)
        
    
        self.status_label = tk.Label(self.root, text="Ready - Click Shuffle to start!", font=('Arial', 12))
        self.status_label.pack(pady=10)
        
        self.anim_frame = tk.Frame(self.root)
        tk.Button(self.anim_frame, text="Next Step", command=self.next_step, state=tk.DISABLED).pack(side=tk.LEFT)
        tk.Button(self.anim_frame, text="Play", command=self.play_animation, state=tk.DISABLED).pack(side=tk.LEFT)
        tk.Button(self.anim_frame, text="Stop", command=self.stop_animation, state=tk.DISABLED).pack(side=tk.LEFT)
        
    def update_board(self):
        for i in range(3):
            for j in range(3):
                num = self.current_board[i][j]
                bg = 'white' if num == 0 else 'lightblue'
                if self.hint_active:
                    blank_i, blank_j = self.find_blank()
                    directions = [(-1,0),(1,0),(0,-1),(0,1)]
                    for di,dj in directions:
                        ni,nj = blank_i + di, blank_j + dj
                        if 0<=ni<3 and 0<=nj<3 and (ni,nj)==(i,j):
                            bg = 'yellow' 
                self.buttons[i][j].config(text=str(num) if num != 0 else '', bg=bg)
        
        sol_moves = 0
        if self.solution_path:
            sol_moves = self.solution_path[-1].moves if self.solution_path[-1] else 0
        method_str = getattr(self, 'last_method', 'None')
        status = f"Manual: {self.manual_moves} | Sol: {sol_moves} ({method_str}) | {'Solvable' if self.is_solvable else 'Unsolvable'}"
        self.status_label.config(text=status)
    
    def move_tile(self, row, col):
        if self.is_animating:
            return
        blank_i, blank_j = self.find_blank()
        if abs(row - blank_i) + abs(col - blank_j) == 1:  
            
            self.move_history.append([row[:] for row in self.current_board])
            self.manual_moves += 1
           
            self.current_board[blank_i][blank_j], self.current_board[row][col] = self.current_board[row][col], self.current_board[blank_i][blank_j]
            self.is_solvable = self._is_solvable()
            self.update_board()
            self.hint_active = False
    
    def find_blank(self):
        for i in range(3):
            for j in range(3):
                if self.current_board[i][j] == 0:
                    return (i, j)
        return (-1, -1)
    
    def _is_solvable(self) -> bool:
        """Check if puzzle is solvable using inversion count."""
        flat = []
        for row in self.current_board:
            flat.extend(row)
        inv_count = 0
        blank_pos = flat.index(0)
        for i in range(len(flat)):
            if flat[i] == 0: continue
            for j in range(i+1, len(flat)):
                if flat[j] != 0 and flat[i] > flat[j]:
                    inv_count += 1
        grid_dist = blank_pos // 3 + blank_pos % 3  
        return (inv_count + grid_dist) % 2 == 0
    
    def undo_move(self):
        if self.move_history:
            self.current_board = self.move_history.pop()
            self.manual_moves -= 1
            self.is_solvable = self._is_solvable()
            self.update_board()
    
    def show_hint(self):
        self.hint_active = True
        self.update_board()
        self.root.after(1500, lambda: setattr(self, 'hint_active', False) or self.update_board())
    
    def shuffle(self):
        diff_moves = {"Easy":50, "Medium":100, "Hard":150}[self.difficulty_var.get()]
        blank_i, blank_j = self.find_blank()
        for _ in range(diff_moves):
            neighbors = []
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for di, dj in directions:
                ni, nj = blank_i + di, blank_j + dj
                if 0 <= ni < 3 and 0 <= nj < 3:
                    neighbors.append((ni, nj))
            if neighbors:
                ni, nj = random.choice(neighbors)
                self.current_board[blank_i][blank_j], self.current_board[ni][nj] = self.current_board[ni][nj], self.current_board[blank_i][blank_j]
                blank_i, blank_j = ni, nj
        self.manual_moves = 0
        self.move_history = []
        self.is_solvable = self._is_solvable()
        if not self.is_solvable:
            messagebox.showwarning("Warning", "Generated unsolvable puzzle. Reset and try again.")
        self.update_board()
        self.solution_path = []
        self.hide_anim_controls()
    
    def solve(self, method):
        if not self.is_solvable:
            messagebox.showwarning("Unsolvable", "This puzzle configuration is unsolvable!")
            return
        if self.is_animating:
            return
        self.solution_path = []
        solution = solve_8puzzle(self.current_board, method)
        if solution:
            path = []
            current = solution
            while current:
                path.append(current)
                current = current.prev
            self.solution_path = path
            self.anim_index = 0  
            self.last_method = method.upper()
            self.status_label.config(text=f"Solved with {method.upper()} ({solution.moves} moves) - Play/Next!")
            self.show_anim_controls()
            
            self.current_board = [row[:] for row in self.solution_path[0].board]
            self.update_board()
        else:
            messagebox.showinfo("No Solution", "No solution found (should not happen for solvable puzzles).")
    
    def reset(self):
        self.current_board = [row[:] for row in self.goal_board]
        self.manual_moves = 0
        self.move_history = []
        self.solution_path = []
        self.last_method = 'None'
        self.is_solvable = True
        self.update_board()
        self.hide_anim_controls()
    
    def next_step(self):
        if self.anim_index < len(self.solution_path):
            self.current_board = [row[:] for row in self.solution_path[self.anim_index].board]
            self.update_board()
            self.anim_index += 1
        else:
            self.hide_anim_controls()
    
    def play_animation(self):
        self.is_animating = True
        self.animate_step()
    
    def animate_step(self):
        if self.anim_index < len(self.solution_path):
            self.next_step()
            self.root.after(500, self.animate_step)  
        else:
            self.stop_animation()
    
    def stop_animation(self):
        self.is_animating = False
    
    def show_anim_controls(self):
        self.anim_frame.pack(pady=10)
        for widget in self.anim_frame.winfo_children():
            widget.config(state=tk.NORMAL)
    
    def hide_anim_controls(self):
        self.is_animating = False
        self.anim_frame.pack_forget()
        self.anim_index = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = EightPuzzleGUI(root)
    root.mainloop()
