"""
Long-term memory implementation for MindPy.

Long-term memory stores persistent information and learned patterns.
"""

from typing import Any, Dict, Optional, List
from pathlib import Path
import json
from mindpy.memory.base import Memory, MemoryEntry


class LongTermMemory(Memory):
    """
    Long-term memory for persistent information and learned patterns.
    
    Long-term memory has unlimited capacity and persists to disk.
    It stores important information that should be retained across sessions.
    """
    
    def __init__(self, persistence_path: str = "data/memory/long_term.json"):
        """
        Initialize long-term memory.
        
        Args:
            persistence_path: Path to the persistence file
        """
        super().__init__(capacity=None, persistence_enabled=True)
        self._persistence_path = Path(persistence_path)
        self._persistence_path.parent.mkdir(parents=True, exist_ok=True)
    
    def add(self, content: Any, entry_type: str = "general", **metadata) -> MemoryEntry:
        """
        Add an entry to long-term memory.
        
        Args:
            content: The content to store
            entry_type: Type of the entry
            **metadata: Additional metadata
            
        Returns:
            The created memory entry
        """
        entry = MemoryEntry(
            content=content,
            entry_type=entry_type,
            metadata=metadata,
            importance=metadata.get("importance", 0.7)
        )
        
        self._entries[entry.entry_id] = entry
        return entry
    
    def add_fact(self, fact: str, category: str = "general") -> MemoryEntry:
        """
        Add a fact to long-term memory.
        
        Args:
            fact: The fact to store
            category: Category of the fact
            
        Returns:
            The memory entry
        """
        return self.add(fact, "fact", category=category, importance=0.8)
    
    def add_pattern(self, pattern: str, description: str) -> MemoryEntry:
        """
        Add a learned pattern to long-term memory.
        
        Args:
            pattern: The pattern description
            description: Detailed description
            
        Returns:
            The memory entry
        """
        return self.add(
            {"pattern": pattern, "description": description},
            "pattern",
            importance=0.9
        )
    
    def get_facts(self, category: Optional[str] = None) -> List[str]:
        """
        Get facts, optionally filtered by category.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of facts
        """
        facts = self.get_by_type("fact")
        
        if category:
            facts = [f for f in facts if f.metadata.get("category") == category]
        
        return [f.content for f in facts]
    
    def get_patterns(self) -> List[Dict[str, Any]]:
        """
        Get all learned patterns.
        
        Returns:
            List of pattern dictionaries
        """
        patterns = self.get_by_type("pattern")
        return [p.content for p in patterns]
    
    async def load(self) -> None:
        """Load memory from persistence file."""
        if not self._persistence_path.exists():
            self._loaded = True
            return
        
        try:
            with open(self._persistence_path, 'r') as f:
                data = json.load(f)
            
            for entry_data in data:
                entry = MemoryEntry(**entry_data)
                self._entries[entry.entry_id] = entry
            
            self._loaded = True
        except Exception as e:
            print(f"Error loading long-term memory: {e}")
            self._loaded = True
    
    async def save(self) -> None:
        """Save memory to persistence file."""
        try:
            data = []
            for entry in self._entries.values():
                entry_dict = {
                    "content": entry.content,
                    "entry_type": entry.entry_type,
                    "timestamp": entry.timestamp.isoformat(),
                    "metadata": entry.metadata,
                    "importance": entry.importance,
                    "access_count": entry.access_count,
                    "last_accessed": entry.last_accessed.isoformat() if entry.last_accessed else None,
                    "entry_id": entry.entry_id
                }
                data.append(entry_dict)
            
            with open(self._persistence_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving long-term memory: {e}")
