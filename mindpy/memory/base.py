"""
Base memory classes for MindPy.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum


class MemoryType(Enum):
    """Types of memory."""
    WORKING = "working"
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    CONVERSATION = "conversation"
    WORLD = "world"
    PLAYER = "player"
    TASK = "task"
    KNOWLEDGE = "knowledge"


@dataclass
class MemoryEntry:
    """
    A single memory entry.
    
    Contains the content, metadata, and timing information.
    """
    content: Any
    entry_type: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    importance: float = 1.0
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    entry_id: str = field(default_factory=lambda: str(hash(datetime.utcnow().timestamp())))
    
    def access(self) -> None:
        """Record an access to this memory entry."""
        self.access_count += 1
        self.last_accessed = datetime.utcnow()
    
    def update_importance(self, importance: float) -> None:
        """
        Update the importance score.
        
        Args:
            importance: New importance score (0.0 to 1.0)
        """
        self.importance = max(0.0, min(1.0, importance))
    
    def __repr__(self) -> str:
        return f"MemoryEntry(type={self.entry_type}, id={self.entry_id[:8]}, importance={self.importance})"


class Memory(ABC):
    """
    Base class for all memory types.
    
    Provides common functionality for storing, retrieving, and managing
    memory entries with configurable persistence.
    """
    
    def __init__(self, capacity: Optional[int] = None, persistence_enabled: bool = False):
        """
        Initialize the memory.
        
        Args:
            capacity: Maximum number of entries (None for unlimited)
            persistence_enabled: Whether to persist memory to disk
        """
        self._entries: Dict[str, MemoryEntry] = {}
        self._capacity = capacity
        self._persistence_enabled = persistence_enabled
        self._loaded = False
    
    @abstractmethod
    def add(self, content: Any, entry_type: str, **metadata) -> MemoryEntry:
        """
        Add a new memory entry.
        
        Args:
            content: The content to store
            entry_type: Type of the entry
            **metadata: Additional metadata
            
        Returns:
            The created memory entry
        """
        pass
    
    def get(self, entry_id: str) -> Optional[MemoryEntry]:
        """
        Get a memory entry by ID.
        
        Args:
            entry_id: The entry ID
            
        Returns:
            Memory entry or None if not found
        """
        entry = self._entries.get(entry_id)
        if entry:
            entry.access()
        return entry
    
    def get_by_type(self, entry_type: str) -> List[MemoryEntry]:
        """
        Get all entries of a specific type.
        
        Args:
            entry_type: The entry type to filter by
            
        Returns:
            List of matching entries
        """
        return [entry for entry in self._entries.values() if entry.entry_type == entry_type]
    
    def search(self, query: str, limit: Optional[int] = None) -> List[MemoryEntry]:
        """
        Search memory entries by content.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching entries
        """
        results = []
        for entry in self._entries.values():
            if query.lower() in str(entry.content).lower():
                results.append(entry)
                entry.access()
                if limit and len(results) >= limit:
                    break
        return results
    
    def remove(self, entry_id: str) -> bool:
        """
        Remove a memory entry.
        
        Args:
            entry_id: The entry ID
            
        Returns:
            True if removed, False if not found
        """
        if entry_id in self._entries:
            del self._entries[entry_id]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all memory entries."""
        self._entries.clear()
    
    def size(self) -> int:
        """Get the number of entries."""
        return len(self._entries)
    
    def is_full(self) -> bool:
        """Check if memory is at capacity."""
        return self._capacity is not None and len(self._entries) >= self._capacity
    
    def _evict_oldest(self) -> None:
        """Evict the oldest entry based on timestamp."""
        if not self._entries:
            return
        
        oldest_entry = min(self._entries.values(), key=lambda e: e.timestamp)
        self.remove(oldest_entry.entry_id)
    
    def _evict_least_important(self) -> None:
        """Evict the least important entry."""
        if not self._entries:
            return
        
        least_important = min(self._entries.values(), key=lambda e: e.importance)
        self.remove(least_important.entry_id)
    
    def _evict_least_accessed(self) -> None:
        """Evict the least accessed entry."""
        if not self._entries:
            return
        
        least_accessed = min(self._entries.values(), key=lambda e: e.access_count)
        self.remove(least_accessed.entry_id)
    
    async def load(self) -> None:
        """Load memory from persistence if enabled."""
        if not self._persistence_enabled or self._loaded:
            return
        
        # TODO: Implement persistence loading
        self._loaded = True
    
    async def save(self) -> None:
        """Save memory to persistence if enabled."""
        if not self._persistence_enabled:
            return
        
        # TODO: Implement persistence saving
    
    def get_all(self) -> List[MemoryEntry]:
        """Get all memory entries."""
        return list(self._entries.values())
    
    def __len__(self) -> int:
        return self.size()
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(entries={self.size()}, capacity={self._capacity})"
