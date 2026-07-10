"""
Event base class and related utilities.
"""

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Any, Dict
from uuid import uuid4


class EventPriority(Enum):
    """Priority levels for event handling."""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


@dataclass
class Event:
    """
    Base class for all events in MindPy.
    
    Events are the primary communication mechanism between components.
    All events are immutable and carry a timestamp and unique ID.
    """
    
    event_type: str
    data: Dict[str, Any] = field(default_factory=dict)
    priority: EventPriority = EventPriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_id: str = field(default_factory=lambda: str(uuid4()))
    source: str = "unknown"
    
    def __post_init__(self):
        """Validate event after initialization."""
        if not self.event_type:
            raise ValueError("event_type cannot be empty")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from event data."""
        return self.data.get(key, default)
    
    def has(self, key: str) -> bool:
        """Check if event data contains a key."""
        return key in self.data
    
    def __repr__(self) -> str:
        return f"Event(type={self.event_type}, id={self.event_id[:8]}, source={self.source})"


class EventTypes:
    """Standard event types used throughout MindPy."""
    
    # Bot lifecycle
    BOT_CONNECTED = "bot.connected"
    BOT_DISCONNECTED = "bot.disconnected"
    BOT_RECONNECTING = "bot.reconnecting"
    BOT_ERROR = "bot.error"
    
    # Player events
    PLAYER_JOINED = "player.joined"
    PLAYER_LEFT = "player.left"
    PLAYER_CHAT = "player.chat"
    PLAYER_DEATH = "player.death"
    PLAYER_RESPAWN = "player.respawn"
    
    # Block events
    BLOCK_BROKEN = "block.broken"
    BLOCK_PLACED = "block.placed"
    BLOCK_UPDATED = "block.updated"
    
    # Inventory events
    INVENTORY_CHANGED = "inventory.changed"
    INVENTORY_OPENED = "inventory.opened"
    INVENTORY_CLOSED = "inventory.closed"
    ITEM_PICKED_UP = "item.picked_up"
    ITEM_DROPPED = "item.dropped"
    
    # Entity events
    ENTITY_SPAWNED = "entity.spawned"
    ENTITY_DESPAWNED = "entity.despawned"
    ENTITY_MOVED = "entity.moved"
    ENTITY_DAMAGED = "entity.damaged"
    ENTITY_DIED = "entity.died"
    
    # Health and status
    HEALTH_CHANGED = "health.changed"
    HUNGER_CHANGED = "hunger.changed"
    EXPERIENCE_CHANGED = "experience.changed"
    
    # Task and goal events
    TASK_STARTED = "task.started"
    TASK_FINISHED = "task.finished"
    TASK_FAILED = "task.failed"
    TASK_CANCELLED = "task.cancelled"
    TASK_SUSPENDED = "task.suspended"
    TASK_RESUMED = "task.resumed"
    
    GOAL_CREATED = "goal.created"
    GOAL_COMPLETED = "goal.completed"
    GOAL_FAILED = "goal.failed"
    GOAL_ABORTED = "goal.aborted"
    
    # AI events
    AI_DECISION = "ai.decision"
    AI_REFLECTION = "ai.reflection"
    AI_TOOL_CALL = "ai.tool_call"
    
    # Plugin events
    PLUGIN_LOADED = "plugin.loaded"
    PLUGIN_UNLOADED = "plugin.unloaded"
    PLUGIN_ERROR = "plugin.error"
    
    # World events
    CHUNK_LOADED = "chunk.loaded"
    CHUNK_UNLOADED = "chunk.unloaded"
    WORLD_CHANGED = "world.changed"
