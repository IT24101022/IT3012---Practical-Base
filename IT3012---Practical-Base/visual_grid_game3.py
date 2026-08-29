import random
import tkinter as tk


class VisualGridHuntGame:
    """A flexible Pacman-style grid environment with support for configurable opponents and larger scales."""

    def __init__(self, width=10, height=10, num_food=10, num_opponents=2, custom_walls=None):

        self.width = width
        self.height = height
        self.agent_pos = [0, 0]

        if custom_walls is not None:
            self.walls = set(custom_walls)

        else:
            self.walls = {
                (2,2),
                (2,3),
                (5,5),
                (6,5),
                (3,7)
            }


        self.food_positions = set()

        while len(self.food_positions) < num_food:

            fx = random.randint(0,self.width-1)
            fy = random.randint(0,self.height-1)

            if (fx,fy) != (0,0) and (fx,fy) not in self.walls:
                self.food_positions.add((fx,fy))


        self.opponents=[]

        while len(self.opponents)<num_opponents:

            ox=random.randint(0,self.width-1)
            oy=random.randint(0,self.height-1)

            if ((ox,oy)!=(0,0)
                and (ox,oy) not in self.walls
                and (ox,oy) not in self.food_positions):

                self.opponents.append([ox,oy])


        self.toxic_traps=set()

        while len(self.toxic_traps)<3:

            tx=random.randint(0,self.width-1)
            ty=random.randint(0,self.height-1)

            trap=(tx,ty)

            if trap!=(0,0) and trap not in self.walls and trap not in self.food_positions:
                self.toxic_traps.add(trap)


        self.score=0
        self.steps=0
        self.collision=False



    # Full Observable Percept (updated for Practical 3 - Search / Planning Agent)
    def get_percept(self):

        x,y=self.agent_pos


        # Agent only sees front cell
        front_x=min(self.width-1,x+1)
        front_y=y


        wall_ahead=(front_x,front_y) in self.walls

        food_here=(x,y) in self.food_positions

        toxin_here=(x,y) in self.toxic_traps


        return {

            "wall_ahead":wall_ahead,
            "food_here":food_here,
            "toxin_here":toxin_here,

            # --- New keys added in Practical 3, Step 1.1 ---
            "grid_size": (self.width, self.height),
            "walls": list(self.walls),
            "all_food": list(self.food_positions),
            "agent_pos": tuple(self.agent_pos)

        }

    def execute_action(self, action: str):
        self.steps += 1
        new_pos = list(self.agent_pos)

        if action == 'Up':
            new_pos[1] = min(self.height - 1, new_pos[1] + 1)
        elif action == 'Down':
            new_pos[1] = max(0, new_pos[1] - 1)
        elif action == 'Left':
            new_pos[0] = max(0, new_pos[0] - 1)
        elif action == 'Right':
            new_pos[0] = min(self.width - 1, new_pos[0] + 1)

        if tuple(new_pos) in self.walls:
            self.score -= 5
        else:
            self.agent_pos = new_pos

        tuple_pos = tuple(self.agent_pos)
        if tuple_pos in self.food_positions:
            self.food_positions.remove(tuple_pos)
            self.score += 20

        # Check if the agent stepped on a toxic trap
        if tuple_pos in self.toxic_traps:
            self.score -= 15

        for op in self.opponents:
            move = random.choice(['Up', 'Down', 'Left', 'Right', 'Stay'])
            if move == 'Up' and op[1] < self.height - 1:
                op[1] += 1
            elif move == 'Down' and op[1] > 0:
                op[1] -= 1
            elif move == 'Left' and op[0] > 0:
                op[0] -= 1
            elif move == 'Right' and op[0] < self.width - 1:
                op[0] += 1

            if op == self.agent_pos:
                self.score -= 50
                self.collision = True

    def is_done(self) -> bool:
        return len(self.food_positions) == 0 or self.steps >= 60 or self.collision

# Simple Reflex Agent

class SimpleReflexAgent:

    def sense_and_act(self, percept):

        if percept["food_here"]:
            return "Stay"

        elif percept["wall_ahead"]:
            return "Up"

        elif percept["toxin_here"]:
            return "Left"

        else:
            return "Right"



# Model Based Agent

class ModelBasedAgent:

    def __init__(self):

        self.visited_cells = set()
        self.last_action = None


    def sense_and_act(self, percept):

        self.visited_cells.add(str(percept))


        if percept["food_here"]:

            action = "Stay"


        elif percept["wall_ahead"]:

            action = "Up"


        elif percept["toxin_here"]:

            action = "Left"


        else:

            action = "Right"


        self.last_action = action

        return action


# Search-Based Planning Agent (Practical 3)
from collections import deque
import heapq


class SearchAgent:
    """Goal-Based / Planning Agent that uses uninformed search (BFS, DFS, UCS)
    to plan a path to the nearest food before acting."""

    def __init__(self):
        self.plan = []
        self.active_algo = 'BFS'   # Change to 'DFS' or 'UCS' to compare

    # ---------- Helper: valid neighbour cells ----------
    def get_neighbors(self, pos, grid_size, walls):
        x, y = pos
        width, height = grid_size
        neighbors = []

        # (action_name, dx, dy) -- must match execute_action above
        moves = [
            ("Up", 0, 1),
            ("Down", 0, -1),
            ("Left", -1, 0),
            ("Right", 1, 0)
        ]

        for action, dx, dy in moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                if (nx, ny) not in walls:
                    neighbors.append((action, (nx, ny)))

        return neighbors

    # ---------- Helper: rebuild the action sequence from a goal node ----------
    def reconstruct_path(self, came_from, start, goal):
        actions = []
        current = goal

        while current != start:
            prev_state, action = came_from[current]
            actions.append(action)
            current = prev_state

        actions.reverse()
        return actions

    # ---------- BFS: FIFO queue -> shallowest node first (optimal on unit-cost grids) ----------
    def bfs_search(self, start, goal, grid_size, walls):
        frontier = deque([start])
        reached = {start}
        came_from = {}

        while frontier:
            current = frontier.popleft()

            if current == goal:
                return self.reconstruct_path(came_from, start, goal)

            for action, next_state in self.get_neighbors(current, grid_size, walls):
                if next_state not in reached:
                    reached.add(next_state)
                    came_from[next_state] = (current, action)
                    frontier.append(next_state)

        return []   # no path found

    # ---------- DFS: LIFO stack -> deepest node first (not optimal) ----------
    def dfs_search(self, start, goal, grid_size, walls):
        frontier = [start]
        reached = {start}
        came_from = {}

        while frontier:
            current = frontier.pop()

            if current == goal:
                return self.reconstruct_path(came_from, start, goal)

            for action, next_state in self.get_neighbors(current, grid_size, walls):
                if next_state not in reached:
                    reached.add(next_state)
                    came_from[next_state] = (current, action)
                    frontier.append(next_state)

        return []

    # ---------- UCS: priority queue ordered by cumulative path cost g(n) ----------
    def ucs_search(self, start, goal, grid_size, walls):
        counter = 0  # tie-breaker so heapq never compares tuples directly
        frontier = [(0, counter, start)]
        reached = {start: 0}
        came_from = {}

        while frontier:
            cost, _, current = heapq.heappop(frontier)

            if current == goal:
                return self.reconstruct_path(came_from, start, goal)

            for action, next_state in self.get_neighbors(current, grid_size, walls):
                new_cost = cost + 1   # every step costs 1 in this grid

                if next_state not in reached or new_cost < reached[next_state]:
                    reached[next_state] = new_cost
                    came_from[next_state] = (current, action)
                    counter += 1
                    heapq.heappush(frontier, (new_cost, counter, next_state))

        return []

    # ---------- Find the closest food using simple Manhattan distance ----------
    def find_closest_food(self, agent_pos, all_food):
        if not all_food:
            return None

        return min(
            all_food,
            key=lambda f: abs(f[0] - agent_pos[0]) + abs(f[1] - agent_pos[1])
        )

    # ---------- Main decision loop ----------
    def sense_and_act(self, percept):

        if not self.plan:
            agent_pos = percept["agent_pos"]
            grid_size = percept["grid_size"]
            walls = set(percept["walls"])
            all_food = percept["all_food"]

            goal = self.find_closest_food(agent_pos, all_food)

            if goal is None:
                return "Stay"

            if self.active_algo == 'BFS':
                self.plan = self.bfs_search(agent_pos, goal, grid_size, walls)
            elif self.active_algo == 'DFS':
                self.plan = self.dfs_search(agent_pos, goal, grid_size, walls)
            elif self.active_algo == 'UCS':
                self.plan = self.ucs_search(agent_pos, goal, grid_size, walls)

            if not self.plan:
                return "Stay"   # no reachable food

        return self.plan.pop(0)


class GridGameGUI:
    """Tkinter wrapper that dynamically scales cell sizes to keep larger grids on screen."""

    def __init__(self, root, width=10, height=10, num_food=12, num_opponents=2, walls=None):
        self.root = root
        self.root.title("IT3012 - Scalable Multi-Agent Grid Hunt")

        self.env = VisualGridHuntGame(width=width, height=height, num_food=num_food, num_opponents=num_opponents,
                                      custom_walls=walls)

        # Dynamically calculate cell size so the total canvas fits nicely within a 600x600 window ceiling
        max_canvas_dim = 600
        self.cell_size = max(20, min(max_canvas_dim // self.env.width, max_canvas_dim // self.env.height))

        canvas_w = self.env.width * self.cell_size
        canvas_h = self.env.height * self.cell_size

        self.canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg="white")
        self.canvas.pack()

        self.label = tk.Label(root, text="Score: 0 | Steps: 0", font=("Arial", 14))
        self.label.pack(pady=10)

        self.btn = tk.Button(root, text="Start Simulation", command=self.run_loop, font=("Arial", 12), bg="#000066",
                             fg="white")
        self.btn.pack(pady=5)

        self.draw_grid()

        # Swap between ModelBasedAgent() and SearchAgent() to compare behaviours.
        # SearchAgent.active_algo can be set to 'BFS', 'DFS', or 'UCS'.
        self.agent = SearchAgent()

    def draw_grid(self):
        self.canvas.delete("all")

        for x in range(self.env.width):
            for y in range(self.env.height):
                x1 = x * self.cell_size
                y1 = (self.env.height - 1 - y) * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color = "#f1f5f9" if (x, y) not in self.env.walls else "#64748b"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#cbd5e1")

                # Only draw text if cell is large enough
                if self.cell_size >= 40 and (x, y) in self.env.walls:
                    self.canvas.create_text(x1 + self.cell_size / 2, y1 + self.cell_size / 2, text="W", fill="white",
                                            font=("Arial", 8, "bold"))

        for fx, fy in self.env.food_positions:
            offset = self.cell_size * 0.25
            x1 = fx * self.cell_size + offset
            y1 = (self.env.height - 1 - fy) * self.cell_size + offset
            self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.5, y1 + self.cell_size * 0.5, fill="#f59e0b",
                                    outline="#d97706")

        # Draw toxic traps
        for tx, ty in self.env.toxic_traps:
            offset = self.cell_size * 0.2
            x1 = tx * self.cell_size + offset
            y1 = (self.env.height - 1 - ty) * self.cell_size + offset

            self.canvas.create_rectangle(
                x1,
                y1,
                x1 + self.cell_size * 0.6,
                y1 + self.cell_size * 0.6,
                fill="purple",
                outline="black"
            )

        for ox, oy in self.env.opponents:
            offset = self.cell_size * 0.2
            x1 = ox * self.cell_size + offset
            y1 = (self.env.height - 1 - oy) * self.cell_size + offset
            self.canvas.create_rectangle(x1, y1, x1 + self.cell_size * 0.6, y1 + self.cell_size * 0.6, fill="#990000",
                                         outline="#7a0000")

        ax, ay = self.env.agent_pos
        offset = self.cell_size * 0.15
        x1 = ax * self.cell_size + offset
        y1 = (self.env.height - 1 - ay) * self.cell_size + offset
        self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.7, y1 + self.cell_size * 0.7, fill="#000066",
                                outline="#1e3a8a")

    def run_loop(self):
        self.btn.config(state="disabled")

        def step():
            if not self.env.is_done():
                percept = self.env.get_percept()

                action = self.agent.sense_and_act(percept)

                self.env.execute_action(action)

                self.draw_grid()

                self.label.config(text=f"Score: {self.env.score} | Steps: {self.env.steps} | Action: {action}")
                
                self.root.after(250, step)
                
            else:
                end_text = f"Collision! Game Over! Final Score: {self.env.score}" if self.env.collision else f"Finished! Final Score: {self.env.score}"
                self.label.config(text=end_text)
                self.btn.config(state="normal")

        step()


if __name__ == "__main__":
    root = tk.Tk()
    # Try a larger grid size like 12x12 with 15 food and 3 opponents!
    app = GridGameGUI(root, width=12, height=12, num_food=15, num_opponents=0)
    root.mainloop()
