"""
Goal base class and related utilities.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Callable
from uuid import uuid4


class GoalStatus(Enum):
    """Status of a goal."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"
    BLOCKED = "blocked"


class GoalPriority(Enum):
    """Priority levels for goals."""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


@dataclass
class Goal:
    """
    A goal in the hierarchical goal system.
    
    Goals can have sub-goals and are decomposed into tasks.
    """
    
    goal_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    status: GoalStatus = GoalStatus.PENDING
    priority: GoalPriority = GoalPriority.NORMAL
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    parent_goal_id: Optional[str] = None
    sub_goal_ids: List[str] = field(default_factory=list)
    task_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    progress: float = 0.0
    error_message: Optional[str] = None
    
    def __post_init__(self):
        """Validate goal after initialization."""
        if not self.name:
            raise ValueError("Goal name cannot be empty")
    
    def add_sub_goal(self, goal_id: str) -> None:
        """
        Add a sub-goal.
        
        Args:
            goal_id: ID of the sub-goal
        """
        if goal_id not in self.sub_goal_ids:
            self.sub_goal_ids.append(goal_id)
    
    def add_task(self, task_id: str) -> None:
        """
        Add a task.
        
        Args:
            task_id: ID of the task
        """
        if task_id not in self.task_ids:
            self.task_ids.append(task_id)
    
    def update_progress(self, progress: float) -> None:
        """
        Update goal progress.
        
        Args:
            progress: Progress value (0.0 to 1.0)
        """
        self.progress = max(0.0, min(1.0, progress))
    
    def mark_started(self) -> None:
        """Mark the goal as started."""
        if self.status == GoalStatus.PENDING:
            self.status = GoalStatus.IN_PROGRESS
            self.started_at = datetime.utcnow()
    
    def mark_completed(self) -> None:
        """Mark the goal as completed."""
        self.status = GoalStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.progress = 1.0
    
    def mark_failed(self, error_message: Optional[str] = None) -> None:
        """
        Mark the goal as failed.
        
        Args:
            error_message: Optional error message
        """
        self.status = GoalStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error_message = error_message
    
    def mark_aborted(self) -> None:
        """Mark the goal as aborted."""
        self.status = GoalStatus.ABORTED
        self.completed_at = datetime.utcnow()
    
    def mark_blocked(self) -> None:
        """Mark the goal as blocked."""
        self.status = GoalStatus.BLOCKED
    
    def is_leaf(self) -> bool:
        """Check if this is a leaf goal (no sub-goals)."""
        return len(self.sub_goal_ids) == 0
    
    def is_root(self) -> bool:
        """Check if this is a root goal (no parent)."""
        return self.parent_goal_id is None
    
    def get_duration(self) -> Optional[float]:
        """
        Get the duration of the goal in seconds.
        
        Returns:
            Duration in seconds or None if not started
        """
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        elif self.started_at:
            return (datetime.utcnow() - self.started_at).total_seconds()
        return None
    
    def __repr__(self) -> str:
        return f"Goal(id={self.goal_id[:8]}, name={self.name}, status={self.status.value})"
