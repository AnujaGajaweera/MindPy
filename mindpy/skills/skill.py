"""
Skill base class for MindPy.

Provides the foundation for reusable high-level behaviors.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime


class SkillState(Enum):
    """States of a skill."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class SkillResult:
    """
    Result of a skill execution.
    
    Contains the outcome, any data produced, and metadata.
    """
    success: bool
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    duration: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __repr__(self) -> str:
        return f"SkillResult(success={self.success}, message={self.message})"


class Skill(ABC):
    """
    Base class for skills.
    
    Skills are reusable high-level behaviors that the bot can perform.
    """
    
    def __init__(self):
        """Initialize the skill."""
        self._state = SkillState.IDLE
        self._started_at: Optional[datetime] = None
        self._completed_at: Optional[datetime] = None
        self._progress: float = 0.0
        self._context: Dict[str, Any] = {}
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Get the skill name.
        
        Returns:
            Skill name
        """
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """
        Get the skill description.
        
        Returns:
            Skill description
        """
        pass
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> SkillResult:
        """
        Execute the skill.
        
        Args:
            context: Execution context
            
        Returns:
            Skill result
        """
        pass
    
    @abstractmethod
    async def pause(self) -> None:
        """Pause the skill execution."""
        pass
    
    @abstractmethod
    async def resume(self) -> None:
        """Resume the skill execution."""
        pass
    
    @abstractmethod
    async def cancel(self) -> None:
        """Cancel the skill execution."""
        pass
    
    def get_state(self) -> SkillState:
        """Get the current skill state."""
        return self._state
    
    def get_progress(self) -> float:
        """Get the current progress (0.0 to 1.0)."""
        return self._progress
    
    def update_progress(self, progress: float) -> None:
        """
        Update the skill progress.
        
        Args:
            progress: Progress value (0.0 to 1.0)
        """
        self._progress = max(0.0, min(1.0, progress))
    
    def get_duration(self) -> Optional[float]:
        """
        Get the skill execution duration.
        
        Returns:
            Duration in seconds or None if not started
        """
        if self._started_at and self._completed_at:
            return (self._completed_at - self._started_at).total_seconds()
        elif self._started_at:
            return (datetime.utcnow() - self._started_at).total_seconds()
        return None
    
    def _set_state(self, state: SkillState) -> None:
        """
        Set the skill state.
        
        Args:
            state: New state
        """
        self._state = state
        
        if state == SkillState.RUNNING and self._started_at is None:
            self._started_at = datetime.utcnow()
        elif state in [SkillState.COMPLETED, SkillState.FAILED, SkillState.CANCELLED]:
            self._completed_at = datetime.utcnow()
            self._progress = 1.0 if state == SkillState.COMPLETED else self._progress
    
    def is_running(self) -> bool:
        """Check if the skill is running."""
        return self._state == SkillState.RUNNING
    
    def is_paused(self) -> bool:
        """Check if the skill is paused."""
        return self._state == SkillState.PAUSED
    
    def is_completed(self) -> bool:
        """Check if the skill is completed."""
        return self._state == SkillState.COMPLETED
    
    def __repr__(self) -> str:
        return f"Skill({self.name}, state={self._state.value})"
