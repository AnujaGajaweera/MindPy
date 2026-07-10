"""
Waypoint management for MindPy.

Provides waypoint storage, management, and navigation between waypoints.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from mindpy.navigation.movement import Position
from mindpy.logging import get_logger


class WaypointType(Enum):
    """Types of waypoints."""
    HOME = "home"
    SPAWN = "spawn"
    CHEST = "chest"
    FARM = "farm"
    MINE = "mine"
    BUILDING = "building"
    INTEREST = "interest"
    CUSTOM = "custom"


@dataclass
class Waypoint:
    """
    A waypoint in the world.
    
    Represents a named location with optional metadata.
    """
    name: str
    position: Position
    waypoint_type: WaypointType = WaypointType.CUSTOM
    description: str = ""
    dimension: str = "minecraft:overworld"
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, any] = field(default_factory=dict)
    
    def __repr__(self) -> str:
        return f"Waypoint(name={self.name}, type={self.waypoint_type.value}, pos={self.position})"


class WaypointManager:
    """
    Manages waypoints for navigation.
    
    Stores, retrieves, and organizes waypoints for efficient navigation.
    """
    
    def __init__(self):
        """Initialize the waypoint manager."""
        self._waypoints: Dict[str, Waypoint] = {}
        self._waypoints_by_type: Dict[WaypointType, List[str]] = {}
        self._logger = get_logger(__name__)
    
    def add_waypoint(
        self,
        name: str,
        position: Position,
        waypoint_type: WaypointType = WaypointType.CUSTOM,
        description: str = "",
        dimension: str = "minecraft:overworld",
        **metadata
    ) -> Waypoint:
        """
        Add a new waypoint.
        
        Args:
            name: Waypoint name
            position: Position
            waypoint_type: Type of waypoint
            description: Description
            dimension: Dimension identifier
            **metadata: Additional metadata
            
        Returns:
            The created waypoint
        """
        waypoint = Waypoint(
            name=name,
            position=position,
            waypoint_type=waypoint_type,
            description=description,
            dimension=dimension,
            metadata=metadata
        )
        
        self._waypoints[name] = waypoint
        
        # Add to type index
        if waypoint_type not in self._waypoints_by_type:
            self._waypoints_by_type[waypoint_type] = []
        self._waypoints_by_type[waypoint_type].append(name)
        
        self._logger.info(f"Added waypoint: {name}")
        return waypoint
    
    def get_waypoint(self, name: str) -> Optional[Waypoint]:
        """
        Get a waypoint by name.
        
        Args:
            name: Waypoint name
            
        Returns:
            Waypoint or None if not found
        """
        return self._waypoints.get(name)
    
    def remove_waypoint(self, name: str) -> bool:
        """
        Remove a waypoint.
        
        Args:
            name: Waypoint name
            
        Returns:
            True if removed, False if not found
        """
        waypoint = self._waypoints.get(name)
        if not waypoint:
            return False
        
        # Remove from type index
        if waypoint.waypoint_type in self._waypoints_by_type:
            self._waypoints_by_type[waypoint.waypoint_type].remove(name)
        
        del self._waypoints[name]
        self._logger.info(f"Removed waypoint: {name}")
        return True
    
    def get_waypoints_by_type(self, waypoint_type: WaypointType) -> List[Waypoint]:
        """
        Get all waypoints of a specific type.
        
        Args:
            waypoint_type: Type to filter by
            
        Returns:
            List of waypoints
        """
        names = self._waypoints_by_type.get(waypoint_type, [])
        return [self._waypoints[name] for name in names if name in self._waypoints]
    
    def get_waypoints_in_dimension(self, dimension: str) -> List[Waypoint]:
        """
        Get all waypoints in a specific dimension.
        
        Args:
            dimension: Dimension identifier
            
        Returns:
            List of waypoints
        """
        return [
            wp for wp in self._waypoints.values()
            if wp.dimension == dimension
        ]
    
    def find_nearest_waypoint(
        self,
        position: Position,
        waypoint_type: Optional[WaypointType] = None,
        max_distance: Optional[float] = None
    ) -> Optional[Waypoint]:
        """
        Find the nearest waypoint to a position.
        
        Args:
            position: Reference position
            waypoint_type: Optional type filter
            max_distance: Optional maximum distance
            
        Returns:
            Nearest waypoint or None
        """
        candidates = list(self._waypoints.values())
        
        if waypoint_type:
            candidates = [wp for wp in candidates if wp.waypoint_type == waypoint_type]
        
        if not candidates:
            return None
        
        # Sort by distance
        candidates.sort(key=lambda wp: wp.position.distance_to(position))
        
        nearest = candidates[0]
        
        if max_distance and nearest.position.distance_to(position) > max_distance:
            return None
        
        return nearest
    
    def find_waypoints_within_distance(
        self,
        position: Position,
        distance: float,
        waypoint_type: Optional[WaypointType] = None
    ) -> List[Waypoint]:
        """
        Find all waypoints within a distance of a position.
        
        Args:
            position: Reference position
            distance: Maximum distance
            waypoint_type: Optional type filter
            
        Returns:
            List of waypoints
        """
        candidates = list(self._waypoints.values())
        
        if waypoint_type:
            candidates = [wp for wp in candidates if wp.waypoint_type == waypoint_type]
        
        return [
            wp for wp in candidates
            if wp.position.distance_to(position) <= distance
        ]
    
    def search_waypoints(self, query: str) -> List[Waypoint]:
        """
        Search waypoints by name or description.
        
        Args:
            query: Search query
            
        Returns:
            List of matching waypoints
        """
        query_lower = query.lower()
        return [
            wp for wp in self._waypoints.values()
            if query_lower in wp.name.lower() or query_lower in wp.description.lower()
        ]
    
    def get_all_waypoints(self) -> List[Waypoint]:
        """Get all waypoints."""
        return list(self._waypoints.values())
    
    def get_waypoint_names(self) -> List[str]:
        """Get all waypoint names."""
        return list(self._waypoints.keys())
    
    def clear(self) -> None:
        """Clear all waypoints."""
        self._waypoints.clear()
        self._waypoints_by_type.clear()
    
    def get_waypoint_count(self) -> int:
        """Get the total number of waypoints."""
        return len(self._waypoints)
    
    def __repr__(self) -> str:
        return f"WaypointManager(waypoints={self.get_waypoint_count()})"
