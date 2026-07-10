"""
Pathfinding system for MindPy.

Provides A* pathfinding and navigation in the Minecraft world.
"""

from typing import List, Tuple, Optional, Callable, Set, Dict
from dataclasses import dataclass, field
from heapq import heappush, heappop
import math

from mindpy.navigation.movement import Position
from mindpy.logging import get_logger


@dataclass(order=True)
class PathNode:
    """
    A node in the pathfinding graph.
    
    Represents a position in the world with pathfinding costs.
    """
    position: Position
    g_cost: float = field(default=float('inf'))  # Cost from start
    h_cost: float = field(default=0.0)  # Heuristic to goal
    f_cost: float = field(default=float('inf'))  # Total cost
    parent: Optional['PathNode'] = None
    walkable: bool = True
    
    def __eq__(self, other: 'PathNode') -> bool:
        return self.position == other.position
    
    def __hash__(self) -> int:
        return hash((self.position.x, self.position.y, self.position.z))
    
    def update_costs(self, g: float, h: float) -> None:
        """Update the costs."""
        self.g_cost = g
        self.h_cost = h
        self.f_cost = g + h
    
    def get_path(self) -> List[Position]:
        """
        Get the path from start to this node.
        
        Returns:
            List of positions
        """
        path = []
        current = self
        while current:
            path.append(current.position)
            current = current.parent
        return path[::-1]


class PathFinder:
    """
    A* pathfinding implementation for Minecraft navigation.
    
    Finds optimal paths between positions while avoiding obstacles.
    """
    
    def __init__(self):
        """Initialize the path finder."""
        self._logger = get_logger(__name__)
        self._max_iterations = 10000
        self._allow_diagonal = True
        self._allow_breaking = False
        self._allow_placing = False
    
    async def find_path(
        self,
        start: Position,
        goal: Position,
        is_walkable: Optional[Callable[[Position], bool]] = None,
        get_neighbors: Optional[Callable[[Position], List[Position]]] = None
    ) -> List[Position]:
        """
        Find a path from start to goal using A*.
        
        Args:
            start: Starting position
            goal: Goal position
            is_walkable: Optional function to check if a position is walkable
            get_neighbors: Optional function to get neighbor positions
            
        Returns:
            List of positions representing the path
        """
        # Default walkable check
        if is_walkable is None:
            is_walkable = lambda pos: True
        
        # Default neighbor generation
        if get_neighbors is None:
            get_neighbors = self._get_default_neighbors
        
        # Initialize
        start_node = PathNode(position=start, g_cost=0, h_cost=self._heuristic(start, goal))
        start_node.update_costs(0, start_node.h_cost)
        
        open_set = [start_node]
        closed_set: Set[PathNode] = set()
        node_map: Dict[Tuple[float, float, float], PathNode] = {
            (start.x, start.y, start.z): start_node
        }
        
        iterations = 0
        
        while open_set and iterations < self._max_iterations:
            iterations += 1
            
            # Get node with lowest f_cost
            current = heappop(open_set)
            
            # Check if we reached the goal
            if current.position.distance_to(goal) < 0.5:
                self._logger.info(f"Path found in {iterations} iterations")
                return current.get_path()
            
            closed_set.add(current)
            
            # Explore neighbors
            for neighbor_pos in get_neighbors(current.position):
                if not is_walkable(neighbor_pos):
                    continue
                
                neighbor_key = (neighbor_pos.x, neighbor_pos.y, neighbor_pos.z)
                
                if neighbor_key in node_map:
                    neighbor = node_map[neighbor_key]
                else:
                    neighbor = PathNode(position=neighbor_pos)
                    node_map[neighbor_key] = neighbor
                
                if neighbor in closed_set:
                    continue
                
                # Calculate costs
                tentative_g = current.g_cost + current.position.distance_to(neighbor_pos)
                h = self._heuristic(neighbor_pos, goal)
                
                if tentative_g < neighbor.g_cost:
                    neighbor.parent = current
                    neighbor.update_costs(tentative_g, h)
                    
                    if neighbor not in open_set:
                        heappush(open_set, neighbor)
        
        self._logger.warning(f"No path found after {iterations} iterations")
        return []
    
    def _heuristic(self, a: Position, b: Position) -> float:
        """
        Calculate heuristic cost between two positions.
        
        Uses Euclidean distance for 3D movement.
        
        Args:
            a: First position
            b: Second position
            
        Returns:
            Heuristic cost
        """
        return a.distance_to(b)
    
    def _get_default_neighbors(self, position: Position) -> List[Position]:
        """
        Get default neighbor positions for pathfinding.
        
        Args:
            position: Current position
            
        Returns:
            List of neighbor positions
        """
        neighbors = []
        
        # Cardinal directions
        directions = [
            (1, 0, 0), (-1, 0, 0),
            (0, 0, 1), (0, 0, -1),
            (0, 1, 0), (0, -1, 0)
        ]
        
        # Add diagonal if enabled
        if self._allow_diagonal:
            diagonals = [
                (1, 0, 1), (1, 0, -1),
                (-1, 0, 1), (-1, 0, -1),
                (1, 1, 0), (1, -1, 0),
                (-1, 1, 0), (-1, -1, 0)
            ]
            directions.extend(diagonals)
        
        for dx, dy, dz in directions:
            neighbor = Position(
                position.x + dx,
                position.y + dy,
                position.z + dz
            )
            neighbors.append(neighbor)
        
        return neighbors
    
    def set_max_iterations(self, max_iterations: int) -> None:
        """
        Set the maximum number of pathfinding iterations.
        
        Args:
            max_iterations: Maximum iterations
        """
        self._max_iterations = max_iterations
    
    def set_allow_diagonal(self, allow: bool) -> None:
        """
        Enable or disable diagonal movement.
        
        Args:
            allow: Whether to allow diagonal movement
        """
        self._allow_diagonal = allow
    
    def set_allow_breaking(self, allow: bool) -> None:
        """
        Enable or allow breaking blocks during pathfinding.
        
        Args:
            allow: Whether to allow breaking blocks
        """
        self._allow_breaking = allow
    
    def set_allow_placing(self, allow: bool) -> None:
        """
        Enable or allow placing blocks during pathfinding.
        
        Args:
            allow: Whether to allow placing blocks
        """
        self._allow_placing = allow
    
    def smooth_path(self, path: List[Position]) -> List[Position]:
        """
        Smooth a path by removing unnecessary waypoints.
        
        Args:
            path: Original path
            
        Returns:
            Smoothed path
        """
        if len(path) <= 2:
            return path
        
        smoothed = [path[0]]
        i = 0
        
        while i < len(path) - 1:
            # Find the furthest visible point
            j = len(path) - 1
            while j > i + 1:
                if self._is_line_of_sight(path[i], path[j]):
                    smoothed.append(path[j])
                    i = j
                    break
                j -= 1
            else:
                smoothed.append(path[i + 1])
                i += 1
        
        return smoothed
    
    def _is_line_of_sight(self, a: Position, b: Position) -> bool:
        """
        Check if there is a clear line of sight between two positions.
        
        Args:
            a: First position
            b: Second position
            
        Returns:
            True if line of sight is clear
        """
        # TODO: Implement actual line of sight check using world data
        return True
