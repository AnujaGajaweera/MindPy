"""
Short-term memory implementation for MindPy.

Short-term memory holds recent events and information for a limited time.
"""

from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from mindpy.memory.base import Memory, MemoryEntry


class ShortTermMemory(Memory):
    """
    Short-term memory for recent events and information.
    
    Short-term memory has a larger capacity than working memory
    and holds information for a limited time before it expires.
    """
    
    def __init__(
        self,
        capacity: int = 100,
        max_age_hours: float = 24.0,
        persistence_enabled: bool = False
    ):
        """
        Initialize short-term memory.
        
        Args:
            capacity: Maximum number of entries (default: 100)
            max_age_hours: Maximum age of entries in hours
            persistence_enabled: Whether to persist to disk
        """
        super().__init__(capacity=capacity, persistence_enabled=persistence_enabled)
        self._max_age = timedelta(hours=max_age_hours)
    
    def add(self, content: Any, entry_type: str = "general", **metadata) -> MemoryEntry:
        """
        Add an entry to short-term memory.
        
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
            importance=metadata.get("importance", 0.5)
        )
        
        self._entries[entry.entry_id] = entry
        return entry
    
    def add_event(self, event_type: str, event_data: Dict[str, Any]) -> MemoryEntry:
        """
        Add an event to short-term memory.
        
        Args:
            event_type: Type of event
            event_data: Event data
            
        Returns:
            The memory entry
        """
        return self.add(
            {"type": event_type, "data": event_data},
            entry_type="event",
            importance=0.6
        )
    
    def get_recent_events(self, event_type: Optional[str] = None, limit: int = 10) -> list:
        """
        Get recent events.
        
        Args:
            event_type: Optional event type filter
            limit: Maximum number of events
            
        Returns:
            List of recent events
        """
        events = self.get_by_type("event")
        
        if event_type:
            events = [e for e in events if e.content.get("type") == event_type]
        
        events.sort(key=lambda e: e.timestamp, reverse=True)
        return [e.content for e in events[:limit]]
    
    def cleanup_expired(self) -> int:
        """
        Remove expired entries.
        
        Returns:
            Number of entries removed
        """
        now = datetime.utcnow()
        expired_ids = [
            entry_id for entry_id, entry in self._entries.items()
            if now - entry.timestamp > self._max_age
        ]
        
        for entry_id in expired_ids:
            self.remove(entry_id)
        
        return len(expired_ids)
    
    def get_entries_since(self, since: datetime) -> list:
        """
        Get entries since a specific time.
        
        Args:
            since: The cutoff time
            
        Returns:
            List of entries since the cutoff
        """
        return [
            entry for entry in self._entries.values()
            if entry.timestamp >= since
        ]
