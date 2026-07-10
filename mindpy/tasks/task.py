"""
Task base class and related utilities.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, Callable
from uuid import uuid4
import json


class TaskStatus(Enum):
    """Status of a task."""
    PENDING = "pending"
    RUNNING = "running"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Priority levels for tasks."""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


@dataclass
class Task:
    """
    A task that can be executed by the bot.
    
    Tasks are interruptible, suspendable, serializable, cancelable, and restartable.
    """
    
    task_id: str = field(default_factory=lambda: str(uuid4()))
    task_type: str = ""
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    suspended_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    progress: float = 0.0
    checkpoint: Optional[Dict[str, Any]] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        """Validate task after initialization."""
        if not self.task_type:
            raise ValueError("Task type cannot be empty")
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Any:
        """
        Execute the task.
        
        Args:
            context: Execution context
            
        Returns:
            Task result
        """
        pass
    
    @abstractmethod
    async def interrupt(self) -> None:
        """Interrupt the task execution."""
        pass
    
    @abstractmethod
    async def suspend(self) -> Dict[str, Any]:
        """
        Suspend the task and save state.
        
        Returns:
            Checkpoint data for resuming
        """
        pass
    
    @abstractmethod
    async def resume(self, checkpoint: Dict[str, Any]) -> None:
        """
        Resume the task from a checkpoint.
        
        Args:
            checkpoint: Checkpoint data from suspension
        """
        pass
    
    @abstractmethod
    async def cancel(self) -> None:
        """Cancel the task."""
        pass
    
    def mark_started(self) -> None:
        """Mark the task as started."""
        if self.status == TaskStatus.PENDING:
            self.status = TaskStatus.RUNNING
            self.started_at = datetime.utcnow()
    
    def mark_completed(self, result: Optional[Any] = None) -> None:
        """
        Mark the task as completed.
        
        Args:
            result: Optional task result
        """
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.progress = 1.0
        if result is not None:
            self.result = result
    
    def mark_failed(self, error: str) -> None:
        """
        Mark the task as failed.
        
        Args:
            error: Error message
        """
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error = error
        self.retry_count += 1
    
    def mark_suspended(self) -> None:
        """Mark the task as suspended."""
        self.status = TaskStatus.SUSPENDED
        self.suspended_at = datetime.utcnow()
    
    def mark_cancelled(self) -> None:
        """Mark the task as cancelled."""
        self.status = TaskStatus.CANCELLED
        self.cancelled_at = datetime.utcnow()
    
    def update_progress(self, progress: float) -> None:
        """
        Update task progress.
        
        Args:
            progress: Progress value (0.0 to 1.0)
        """
        self.progress = max(0.0, min(1.0, progress))
    
    def can_retry(self) -> bool:
        """Check if the task can be retried."""
        return self.retry_count < self.max_retries
    
    def get_duration(self) -> Optional[float]:
        """
        Get the duration of the task in seconds.
        
        Returns:
            Duration in seconds or None if not started
        """
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        elif self.started_at:
            return (datetime.utcnow() - self.started_at).total_seconds()
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize task to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "suspended_at": self.suspended_at.isoformat() if self.suspended_at else None,
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
            "result": self.result,
            "error": self.error,
            "metadata": self.metadata,
            "progress": self.progress,
            "checkpoint": self.checkpoint,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """
        Deserialize task from dictionary.
        
        Args:
            data: Dictionary representation
            
        Returns:
            Task instance
        """
        # Convert datetime strings back to datetime objects
        for field_name in ["created_at", "started_at", "completed_at", "suspended_at", "cancelled_at"]:
            if data.get(field_name):
                data[field_name] = datetime.fromisoformat(data[field_name])
        
        # Convert status and priority strings back to enums
        data["status"] = TaskStatus(data["status"])
        data["priority"] = TaskPriority(data["priority"])
        
        return cls(**data)
    
    def __repr__(self) -> str:
        return f"Task(id={self.task_id[:8]}, type={self.task_type}, status={self.status.value})"


class BaseTask(Task):
    """
    Base implementation of a task.
    
    Provides default implementations for task lifecycle methods.
    """
    
    def __init__(self, **kwargs):
        """Initialize the base task."""
        super().__init__(**kwargs)
        self._interrupted = False
        self._cancelled = False
    
    async def execute(self, context: Dict[str, Any]) -> Any:
        """
        Execute the task (to be overridden by subclasses).
        
        Args:
            context: Execution context
            
        Returns:
            Task result
        """
        raise NotImplementedError("Subclasses must implement execute()")
    
    async def interrupt(self) -> None:
        """Interrupt the task execution."""
        self._interrupted = True
    
    async def suspend(self) -> Dict[str, Any]:
        """
        Suspend the task and save state.
        
        Returns:
            Checkpoint data
        """
        self.mark_suspended()
        return {
            "progress": self.progress,
            "metadata": self.metadata.copy()
        }
    
    async def resume(self, checkpoint: Dict[str, Any]) -> None:
        """
        Resume the task from a checkpoint.
        
        Args:
            checkpoint: Checkpoint data
        """
        self.checkpoint = checkpoint
        self.status = TaskStatus.RUNNING
        self._interrupted = False
    
    async def cancel(self) -> None:
        """Cancel the task."""
        self._cancelled = True
        self.mark_cancelled()
    
    def is_interrupted(self) -> bool:
        """Check if the task was interrupted."""
        return self._interrupted
    
    def is_cancelled(self) -> bool:
        """Check if the task was cancelled."""
        return self._cancelled
