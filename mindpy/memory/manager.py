"""
Memory manager for MindPy.

Manages all memory types and provides a unified interface.
"""

from typing import Optional, Dict, Any
from mindpy.memory.base import Memory
from mindpy.memory.working import WorkingMemory
from mindpy.memory.short_term import ShortTermMemory
from mindpy.memory.long_term import LongTermMemory
from mindpy.memory.conversation import ConversationMemory
from mindpy.memory.world import WorldMemory
from mindpy.memory.player import PlayerMemory
from mindpy.memory.task import TaskMemory
from mindpy.memory.knowledge import KnowledgeBase
from mindpy.logging import get_logger


class MemoryManager:
    """
    Manages all memory types for a bot.
    
    Provides a unified interface for accessing different memory types
    and handles loading/saving persistence.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the memory manager.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = get_logger(__name__)
        
        # Initialize memory types
        self.working = WorkingMemory(
            capacity=self.config.get("working_memory_size", 10),
            persistence_enabled=False
        )
        
        self.short_term = ShortTermMemory(
            capacity=self.config.get("short_term_memory_size", 100),
            max_age_hours=24.0,
            persistence_enabled=self.config.get("persistence_enabled", True)
        )
        
        self.long_term = LongTermMemory(
            persistence_path=self.config.get("persistence_path", "data/memory/long_term.json")
        )
        
        self.conversation = ConversationMemory(
            capacity=500,
            persistence_enabled=self.config.get("persistence_enabled", True)
        )
        
        self.world = WorldMemory(
            capacity=1000,
            persistence_enabled=self.config.get("persistence_enabled", True)
        )
        
        self.player = PlayerMemory(
            capacity=200,
            persistence_enabled=self.config.get("persistence_enabled", True)
        )
        
        self.task = TaskMemory(
            capacity=500,
            persistence_enabled=self.config.get("persistence_enabled", True)
        )
        
        self.knowledge = KnowledgeBase(
            capacity=1000,
            persistence_enabled=self.config.get("persistence_enabled", True)
        )
    
    async def load_all(self) -> None:
        """Load all persistent memories."""
        self.logger.info("Loading memories...")
        
        await self.long_term.load()
        await self.conversation.load()
        await self.world.load()
        await self.player.load()
        await self.task.load()
        await self.knowledge.load()
        
        self.logger.info("Memories loaded")
    
    async def save_all(self) -> None:
        """Save all persistent memories."""
        self.logger.info("Saving memories...")
        
        await self.long_term.save()
        await self.conversation.save()
        await self.world.save()
        await self.player.save()
        await self.task.save()
        await self.knowledge.save()
        
        self.logger.info("Memories saved")
    
    def get_memory(self, memory_type: str) -> Optional[Memory]:
        """
        Get a memory by type name.
        
        Args:
            memory_type: Name of the memory type
            
        Returns:
            Memory instance or None if not found
        """
        memory_map = {
            "working": self.working,
            "short_term": self.short_term,
            "long_term": self.long_term,
            "conversation": self.conversation,
            "world": self.world,
            "player": self.player,
            "task": self.task,
            "knowledge": self.knowledge
        }
        return memory_map.get(memory_type)
    
    def cleanup(self) -> None:
        """Perform cleanup operations on all memories."""
        self.short_term.cleanup_expired()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics for all memory types.
        
        Returns:
            Dictionary with memory statistics
        """
        return {
            "working": {
                "size": self.working.size(),
                "capacity": self.working._capacity
            },
            "short_term": {
                "size": self.short_term.size(),
                "capacity": self.short_term._capacity
            },
            "long_term": {
                "size": self.long_term.size(),
                "capacity": self.long_term._capacity
            },
            "conversation": {
                "size": self.conversation.size(),
                "capacity": self.conversation._capacity
            },
            "world": {
                "size": self.world.size(),
                "capacity": self.world._capacity
            },
            "player": {
                "size": self.player.size(),
                "capacity": self.player._capacity
            },
            "task": {
                "size": self.task.size(),
                "capacity": self.task._capacity
            },
            "knowledge": {
                "size": self.knowledge.size(),
                "capacity": self.knowledge._capacity
            }
        }
    
    def __repr__(self) -> str:
        return f"MemoryManager(memories=8)"
