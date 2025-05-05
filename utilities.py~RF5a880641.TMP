from raylibpy import Vector2, check_collision_point_rec, vector2_subtract, vector2_length, vector2_normalize
from raylibpy import Rectangle
import heapq
from typing import List, Tuple, Optional

def center_of_rect(rect: Rectangle):
    cx = rect.x + (rect.width/2.0)
    cy = rect.y + (rect.height/2.0)
    return Vector2(cx, cy)

def direction_between_rects(a: Rectangle, b: Rectangle):
    va = center_of_rect(a)
    vb = center_of_rect(b)
    return vector2_normalize(vector2_subtract(vb, va))

def has_line_of_sight(source_rect: Rectangle,
                     target_rect: Rectangle,
                     obstacles: list[Rectangle],
                     step: float = 10.0) -> bool:
    """
    Returns True if the straight line from source to target does not hit
    any of the obstacle rectangles.
    """
    start = center_of_rect(source_rect)
    end = center_of_rect(target_rect)
    delta = vector2_subtract(end, start)
    dist = vector2_length(delta)
    if dist == 0:
        return True

    dir_norm = vector2_normalize(delta)
    num_steps = int(dist // step)
    for i in range(num_steps + 1):
        px = start.x + dir_norm.x * i * step
        py = start.y + dir_norm.y * i * step
        for obs in obstacles:
            if check_collision_point_rec(Vector2(px, py), obs):
                return False
    return True

# --------------------------
# A* Pathfinding Utilities
# --------------------------

def create_pathfinding_grid(obstacles: List[Rectangle], 
                          world_width: int, 
                          world_height: int, 
                          cell_size: int) -> List[List[int]]:
    """
    Creates a 2D grid for pathfinding where:
    1 = walkable, 0 = obstacle
    
    Parameters:
        obstacles: List of obstacle rectangles
        world_width: Total width of game world in pixels
        world_height: Total height of game world in pixels
        cell_size: Size of each grid cell in pixels
    
    Returns:
        2D list representing the walkable grid
    """
    grid_width = (world_width // cell_size) + 1
    grid_height = (world_height // cell_size) + 1
    grid = [[1 for _ in range(grid_width)] for _ in range(grid_height)]
    
    for obstacle in obstacles:
        start_x = max(0, int(obstacle.x / cell_size))
        start_y = max(0, int(obstacle.y / cell_size))
        end_x = min(grid_width - 1, int((obstacle.x + obstacle.width) / cell_size))
        end_y = min(grid_height - 1, int((obstacle.y + obstacle.height) / cell_size))
        
        for y in range(start_y, end_y + 1):
            for x in range(start_x, end_x + 1):
                grid[y][x] = 0
                
    return grid

def a_star_find_path(grid: List[List[int]], 
                    start_pos: Vector2, 
                    goal_pos: Vector2, 
                    cell_size: int) -> List[Vector2]:
    """
    A* pathfinding algorithm that returns world-space positions
    
    Parameters:
        grid: 2D grid from create_pathfinding_grid()
        start_pos: Starting position in world coordinates
        goal_pos: Target position in world coordinates
        cell_size: Size used when creating the grid
    
    Returns:
        List of Vector2 waypoints in world space (empty if no path)
    """
    def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    # Convert world positions to grid coordinates
    start_node = (int(start_pos.x / cell_size), int(start_pos.y / cell_size))
    goal_node = (int(goal_pos.x / cell_size), int(goal_pos.y / cell_size))
    
    # Check bounds
    grid_height = len(grid)
    grid_width = len(grid[0]) if grid_height > 0 else 0
    
    if (not (0 <= start_node[0] < grid_width and 0 <= start_node[1] < grid_height) or
        not (0 <= goal_node[0] < grid_width and 0 <= goal_node[1] < grid_height)):
        return []
    
    # Check if start or goal is blocked
    if grid[start_node[1]][start_node[0]] == 0 or grid[goal_node[1]][goal_node[0]] == 0:
        return []
    
    # A* algorithm
    open_set = []
    heapq.heappush(open_set, (0, start_node))
    came_from = {}
    g_score = {start_node: 0}
    f_score = {start_node: heuristic(start_node, goal_node)}
    
    while open_set:
        current = heapq.heappop(open_set)[1]
        
        if current == goal_node:
            # Reconstruct path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            
            # Convert grid coordinates to world positions
            return [Vector2(
                x * cell_size + cell_size // 2,
                y * cell_size + cell_size // 2
            ) for x, y in path]
        
        # Check all 4 directions
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            neighbor = (current[0] + dx, current[1] + dy)
            
            # Check if neighbor is walkable
            if (0 <= neighbor[0] < grid_width and 
                0 <= neighbor[1] < grid_height and 
                grid[neighbor[1]][neighbor[0]] == 1):
                
                tentative_g = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor, goal_node)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
    
    return []  # No path found

class Pathfinder:
    """
    Class-based pathfinding utility that maintains grid state
    """
    def __init__(self, cell_size: int = 64):
        self.cell_size = cell_size
        self.grid = None
        self.grid_width = 0
        self.grid_height = 0
    
    def update_grid(self, obstacles: List[Rectangle], world_width: int, world_height: int):
        """
        Updates the internal grid with current obstacles
        """
        self.grid_width = (world_width // self.cell_size) + 1
        self.grid_height = (world_height // self.cell_size) + 1
        self.grid = [[1 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        for obstacle in obstacles:
            start_x = max(0, int(obstacle.x / self.cell_size))
            start_y = max(0, int(obstacle.y / self.cell_size))
            end_x = min(self.grid_width - 1, int((obstacle.x + obstacle.width) / self.cell_size))
            end_y = min(self.grid_height - 1, int((obstacle.y + obstacle.height) / self.cell_size))
            
            for y in range(start_y, end_y + 1):
                for x in range(start_x, end_x + 1):
                    self.grid[y][x] = 0
    
    def find_path(self, start_pos: Vector2, goal_pos: Vector2) -> List[Vector2]:
        """
        Finds path using the current grid state
        """
        if self.grid is None:
            return []
        
        return a_star_find_path(self.grid, start_pos, goal_pos, self.cell_size)