"""
Movement controller for MindPy.

Handles basic movement operations: walking, jumping, swimming, etc.
"""

from typing import Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio

from mindpy.logging import get_logger


class MovementState(Enum):
    """States of movement."""
    IDLE = "idle"
    WALKING = "walking"
    RUNNING = "running"
    JUMPING = "jumping"
    SWIMMING = "swimming"
    CLIMBING = "climbing"
    FLYING = "flying"


@dataclass
class Position:
    """3D position in the world."""
    x: float
    y: float
    z: float
    
    def distance_to(self, other: 'Position') -> float:
        """Calculate distance to another position."""
        return (
            (self.x - other.x) ** 2 +
            (self.y - other.y) ** 2 +
            (self.z - other.z) ** 2
        ) ** 0.5
    
    def __add__(self, other: 'Position') -> 'Position':
        return Position(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other: 'Position') -> 'Position':
        return Position(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __repr__(self) -> str:
        return f"Position({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"


class MovementController:
    """
    Controls bot movement in the Minecraft world.
    
    Handles walking, jumping, swimming, climbing, and other movement types.
    """
    
    def __init__(self):
        """Initialize the movement controller."""
        self._current_position = Position(0.0, 0.0, 0.0)
        self._target_position: Optional[Position] = None
        self._movement_state = MovementState.IDLE
        self._speed = 0.1
        self._logger = get_logger(__name__)
    
    async def move_to(self, target: Position, timeout: float = 30.0) -> bool:
        """
        Move to a target position.
        
        Args:
            target: Target position
            timeout: Maximum time to reach target
            
        Returns:
            True if reached, False if timeout
        """
        self._target_position = target
        self._movement_state = MovementState.WALKING
        
        self._logger.info(f"Moving to {target}")
        
        # TODO: Implement actual movement via PyCraft
        # This is a placeholder for the actual implementation
        await asyncio.sleep(0.1)
        
        self._current_position = target
        self._movement_state = MovementState.IDLE
        self._target_position = None
        
        return True
    
    async def walk(self, direction: Tuple[float, float], distance: float) -> None:
        """
        Walk in a direction.
        
        Args:
            direction: Direction vector (x, z)
            distance: Distance to walk
        """
        dx, dz = direction
        target = Position(
            self._current_position.x + dx * distance,
            self._current_position.y,
            self._current_position.z + dz * distance
        )
        await self.move_to(target)
    
    async def jump(self) -> None:
        """Make the bot jump."""
        self._movement_state = MovementState.JUMPING
        self._logger.info("Jumping")
        
        # TODO: Implement jump via PyCraft
        await asyncio.sleep(0.1)
        
        self._movement_state = MovementState.IDLE
    
    async def sprint(self, enabled: bool = True) -> None:
        """
        Enable or disable sprinting.
        
        Args:
            enabled: Whether to sprint
        """
        if enabled:
            self._movement_state = MovementState.RUNNING
            self._speed = 0.2
        else:
            self._movement_state = MovementState.WALKING
            self._speed = 0.1
        
        # TODO: Implement sprint via PyCraft
    
    async def swim(self, direction: Tuple[float, float, float]) -> None:
        """
        Swim in a direction.
        
        Args:
            direction: Direction vector (x, y, z)
        """
        self._movement_state = MovementState.SWIMMING
        self._logger.info(f"Swimming in direction {direction}")
        
        # TODO: Implement swimming via PyCraft
        await asyncio.sleep(0.1)
    
    async def climb(self, direction: Tuple[float, float]) -> None:
        """
        Climb a ladder or vine.
        
        Args:
            direction: Direction (up/down)
        """
        self._movement_state = MovementState.CLIMBING
        self._logger.info(f"Climbing {direction}")
        
        # TODO: Implement climbing via PyCraft
        await asyncio.sleep(0.1)
    
    async def fly(self, enabled: bool = True) -> None:
        """
        Enable or disable flying (creative mode).
        
        Args:
            enabled: Whether to fly
        """
        if enabled:
            self._movement_state = MovementState.FLYING
        else:
            self._movement_state = MovementState.IDLE
        
        # TODO: Implement flying via PyCraft
    
    async def stop(self) -> None:
        """Stop all movement."""
        self._target_position = None
        self._movement_state = MovementState.IDLE
        
        # TODO: Stop movement via PyCraft
    
    def get_position(self) -> Position:
        """Get current position."""
        return self._current_position
    
    def set_position(self, position: Position) -> None:
        """
        Set current position (teleport).
        
        Args:
            position: New position
        """
        self._current_position = position
    
    def get_movement_state(self) -> MovementState:
        """Get current movement state."""
        return self._movement_state
    
    def is_moving(self) -> bool:
        """Check if the bot is currently moving."""
        return self._movement_state != MovementState.IDLE
    
    def __repr__(self) -> str:
        return f"MovementController(pos={self._current_position}, state={self._movement_state.value})"
