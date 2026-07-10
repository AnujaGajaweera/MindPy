"""
Working memory implementation for MindPy.

Working memory holds immediate context and current task information.
"""

from typing import Any, Dict, Optional
from mindpy.memory.base import Memory, MemoryEntry


class WorkingMemory(Memory):
    """
    Working memory for immediate context and current tasks.
    
    Working memory has a small capacity and holds information
    that is currently relevant to the bot's activities.
    """
    
    def __init__(self, capacity: int = 10, persistence_enabled: bool = False):
        """
        Initialize working memory.
        
        Args:
            capacity: Maximum number of entries (default: 10)
            persistence_enabled: Whether to persist to disk
        """
        super().__init__(capacity=capacity, persistence_enabled=persistence_enabled)
    
    def add(self, content: Any, entry_type: str = "general", **metadata) -> MemoryEntry:
        """
        Add an entry to working memory.
        
        Args:
            content: The content to store
            entry_type: Type of the entry
            **metadata: Additional metadata
            
        Returns:
            The created memory entry
        """
        if self.is_full():
            self._evict_least_accessed()
        
        entry = MemoryEntry(
            content=content,
            entry_type=entry_type,
            metadata=metadata,
            importance=metadata.get("importance", 1.0)
        )
        
        self._entries[entry.entry_id] = entry
        return entry
    
    def set_current_task(self, task: str) -> MemoryEntry:
        """
        Set the current task.
        
        Args:
            task: Description of the current task
            
        Returns:
            The memory entry
        """
        # Remove any existing current task
        for entry in self.get_by_type("current_task"):
            self.remove(entry.entry_id)
        
        return self.add(task, "current_task", importance=1.0)
    
    def get_current_task(self) -> Optional[str]:
        """
        Get the current task.
        
        Returns:
            Current task description or None
        """
        tasks = self.get_by_type("current_task")
        if tasks:
            return tasks[0].content
        return None
    
    def add_context(self, context: str, importance: float = 0.8) -> MemoryEntry:
        """
        Add contextual information.
        
        Args:
            context: Context information
            importance: Importance score
            
        Returns:
            The memory entry
        """
        return self.add(context, "context", importance=importance)
    
    def get_recent_context(self, limit: int = 5) -> list:
        """
        Get recent context entries.
        
        Args:
            limit: Maximum number of entries
            
        Returns:
            List of recent context entries
        """
        contexts = self.get_by_type("context")
        contexts.sort(key=lambda e: e.timestamp, reverse=True)
        return [c.content for c in contexts[:limit]]
