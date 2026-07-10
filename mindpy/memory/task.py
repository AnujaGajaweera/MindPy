"""
Task memory implementation for MindPy.

Task memory stores information about tasks, their status, and history.
"""

from typing import Any, Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from mindpy.memory.base import Memory, MemoryEntry


class TaskStatus(Enum):
    """Status of a task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"


@dataclass
class TaskRecord:
    """Record of a task."""
    task_id: str
    task_type: str
    description: str
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class TaskMemory(Memory):
    """
    Task memory for storing task information and history.
    
    Tracks tasks, their status, results, and execution history.
    """
    
    def __init__(self, capacity: int = 500, persistence_enabled: bool = True):
        """
        Initialize task memory.
        
        Args:
            capacity: Maximum number of entries (default: 500)
            persistence_enabled: Whether to persist to disk
        """
        super().__init__(capacity=capacity, persistence_enabled=persistence_enabled)
        self._task_index: Dict[str, str] = {}  # task_id -> entry_id
    
    def add(self, content: Any, entry_type: str = "task", **metadata) -> MemoryEntry:
        """
        Add task information to memory.
        
        Args:
            content: The content to store
            entry_type: Type of the entry
            **metadata: Additional metadata
            
        Returns:
            The created memory entry
        """
        if self.is_full():
            self._evict_oldest()
        
        entry = MemoryEntry(
            content=content,
            entry_type=entry_type,
            metadata=metadata,
            importance=metadata.get("importance", 0.7)
        )
        
        self._entries[entry.entry_id] = entry
        
        # Index by task
        if entry_type == "task_record" and isinstance(content, TaskRecord):
            self._task_index[content.task_id] = entry.entry_id
        
        return entry
    
    def create_task(
        self,
        task_id: str,
        task_type: str,
        description: str,
        **metadata
    ) -> MemoryEntry:
        """
        Create a new task record.
        
        Args:
            task_id: Unique task identifier
            task_type: Type of task
            description: Task description
            **metadata: Additional metadata
            
        Returns:
            The memory entry
        """
        task_record = TaskRecord(
            task_id=task_id,
            task_type=task_type,
            description=description,
            status=TaskStatus.PENDING,
            created_at=datetime.utcnow(),
            metadata=metadata
        )
        return self.add(task_record, "task_record", importance=0.8)
    
    def get_task(self, task_id: str) -> Optional[TaskRecord]:
        """
        Get a task by ID.
        
        Args:
            task_id: Task identifier
            
        Returns:
            TaskRecord or None if not found
        """
        entry_id = self._task_index.get(task_id)
        if entry_id:
            entry = self.get(entry_id)
            if entry:
                return entry.content
        return None
    
    def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        result: Optional[Any] = None,
        error: Optional[str] = None
    ) -> bool:
        """
        Update task status.
        
        Args:
            task_id: Task identifier
            status: New status
            result: Optional result
            error: Optional error message
            
        Returns:
            True if updated, False if not found
        """
        task = self.get_task(task_id)
        if not task:
            return False
        
        task.status = status
        
        if status == TaskStatus.IN_PROGRESS and not task.started_at:
            task.started_at = datetime.utcnow()
        elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            task.completed_at = datetime.utcnow()
        
        if result is not None:
            task.result = result
        if error is not None:
            task.error = error
        
        return True
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[TaskRecord]:
        """
        Get all tasks with a specific status.
        
        Args:
            status: Task status to filter by
            
        Returns:
            List of task records
        """
        tasks = self.get_by_type("task_record")
        matching = [t for t in tasks if t.content.status == status]
        return [t.content for t in matching]
    
    def get_tasks_by_type(self, task_type: str) -> List[TaskRecord]:
        """
        Get all tasks of a specific type.
        
        Args:
            task_type: Task type to filter by
            
        Returns:
            List of task records
        """
        tasks = self.get_by_type("task_record")
        matching = [t for t in tasks if t.content.task_type == task_type]
        return [t.content for t in matching]
    
    def get_recent_tasks(self, limit: int = 20) -> List[TaskRecord]:
        """
        Get recent tasks.
        
        Args:
            limit: Maximum number of tasks
            
        Returns:
            List of recent task records
        """
        tasks = self.get_by_type("task_record")
        tasks.sort(key=lambda e: e.content.created_at, reverse=True)
        
        for task in tasks[:limit]:
            task.access()
        
        return [t.content for t in tasks[:limit]]
    
    def get_failed_tasks(self, limit: int = 20) -> List[TaskRecord]:
        """
        Get failed tasks.
        
        Args:
            limit: Maximum number of tasks
            
        Returns:
            List of failed task records
        """
        return self.get_tasks_by_status(TaskStatus.FAILED)[:limit]
    
    def get_task_statistics(self) -> Dict[str, int]:
        """
        Get task statistics.
        
        Returns:
            Dictionary with task counts by status
        """
        stats = {
            "total": 0,
            "pending": 0,
            "in_progress": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0,
            "suspended": 0
        }
        
        tasks = self.get_by_type("task_record")
        stats["total"] = len(tasks)
        
        for task in tasks:
            status = task.content.status.value
            if status in stats:
                stats[status] += 1
        
        return stats
