"""
Entity manager for MindPy.

Provides entity tracking, player tracking, mob tracking, and entity interaction.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from mindpy.navigation.movement import Position
from mindpy.logging import get_logger


class EntityType(Enum):
    """Types of entities."""
    PLAYER = "player"
    ZOMBIE = "zombie"
    SKELETON = "skeleton"
    CREEPER = "creeper"
    SPIDER = "spider"
    ENDERMAN = "enderman"
    PIG = "pig"
    COW = "cow"
    CHICKEN = "chicken"
    SHEEP = "sheep"
    VILLAGER = "villillager"
    IRON_GOLEM = "iron_golem"
    ITEM = "item"
    EXPERIENCE_ORB = "experience_orb"


@dataclass
class Entity:
    """
    Represents an entity in the world.
    
    Contains position, type, health, and other entity properties.
    """
    entity_id: str
    entity_type: EntityType
    position: Position
    health: float = 20.0
    max_health: float = 20.0
    name: Optional[str] = None
    custom_name: Optional[str] = None
    is_hostile: bool = False
    first_seen: datetime = None
    last_seen: datetime = None
    
    def __post_init__(self):
        if self.first_seen is None:
            self.first_seen = datetime.utcnow()
        if self.last_seen is None:
            self.last_seen = datetime.utcnow()
        
        # Set hostile based on type
        if self.entity_type in [EntityType.ZOMBIE, EntityType.SKELETON, 
                                EntityType.CREEPER, EntityType.SPIDER]:
            self.is_hostile = True
    
    def update_position(self, new_position: Position) -> None:
        """Update the entity's position."""
        self.position = new_position
        self.last_seen = datetime.utcnow()
    
    def is_alive(self) -> bool:
        """Check if the entity is alive."""
        return self.health > 0
    
    def get_health_percentage(self) -> float:
        """Get health as a percentage."""
        return (self.health / self.max_health) * 100 if self.max_health > 0 else 0
    
    def distance_to(self, other: Position) -> float:
        """Calculate distance to a position."""
        return self.position.distance_to(other)
    
    def __repr__(self) -> str:
        name = self.name or self.custom_name or self.entity_type.value
        return f"Entity({name} at {self.position})"


class EntityManager:
    """
    Manages entities in the world.
    
    Tracks players, mobs, items, and other entities.
    """
    
    def __init__(self):
        """Initialize the entity manager."""
        self._entities: Dict[str, Entity] = {}
        self._entities_by_type: Dict[EntityType, List[str]] = {}
        self._logger = get_logger(__name__)
    
    def add_entity(self, entity: Entity) -> None:
        """
        Add an entity to tracking.
        
        Args:
            entity: Entity to track
        """
        self._entities[entity.entity_id] = entity
        
        if entity.entity_type not in self._entities_by_type:
            self._entities_by_type[entity.entity_type] = []
        self._entities_by_type[entity.entity_type].append(entity.entity_id)
        
        self._logger.debug(f"Added entity: {entity}")
    
    def remove_entity(self, entity_id: str) -> bool:
        """
        Remove an entity from tracking.
        
        Args:
            entity_id: Entity ID to remove
            
        Returns:
            True if removed
        """
        entity = self._entities.get(entity_id)
        if not entity:
            return False
        
        # Remove from type index
        if entity.entity_type in self._entities_by_type:
            self._entities_by_type[entity.entity_type].remove(entity_id)
        
        del self._entities[entity_id]
        self._logger.debug(f"Removed entity: {entity_id}")
        return True
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """
        Get an entity by ID.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Entity or None
        """
        return self._entities.get(entity_id)
    
    def update_entity_position(self, entity_id: str, position: Position) -> bool:
        """
        Update an entity's position.
        
        Args:
            entity_id: Entity ID
            position: New position
            
        Returns:
            True if updated
        """
        entity = self._entities.get(entity_id)
        if entity:
            entity.update_position(position)
            return True
        return False
    
    def get_entities_by_type(self, entity_type: EntityType) -> List[Entity]:
        """
        Get all entities of a specific type.
        
        Args:
            entity_type: Entity type
            
        Returns:
            List of entities
        """
        entity_ids = self._entities_by_type.get(entity_type, [])
        return [self._entities[eid] for eid in entity_ids if eid in self._entities]
    
    def get_hostile_entities(self) -> List[Entity]:
        """Get all hostile entities."""
        return [e for e in self._entities.values() if e.is_hostile]
    
    def get_players(self) -> List[Entity]:
        """Get all player entities."""
        return self.get_entities_by_type(EntityType.PLAYER)
    
    def find_nearest_entity(
        self,
        position: Position,
        entity_type: Optional[EntityType] = None,
        max_distance: float = 50.0
    ) -> Optional[Entity]:
        """
        Find the nearest entity to a position.
        
        Args:
            position: Reference position
            entity_type: Optional entity type filter
            max_distance: Maximum search distance
            
        Returns:
            Nearest entity or None
        """
        candidates = list(self._entities.values())
        
        if entity_type:
            candidates = [e for e in candidates if e.entity_type == entity_type]
        
        if not candidates:
            return None
        
        # Sort by distance
        candidates.sort(key=lambda e: e.distance_to(position))
        
        nearest = candidates[0]
        if nearest.distance_to(position) <= max_distance:
            return nearest
        
        return None
    
    def find_entities_in_radius(
        self,
        position: Position,
        radius: float,
        entity_type: Optional[EntityType] = None
    ) -> List[Entity]:
        """
        Find all entities within a radius.
        
        Args:
            position: Center position
            radius: Search radius
            entity_type: Optional entity type filter
            
        Returns:
            List of entities
        """
        entities = []
        
        for entity in self._entities.values():
            if entity_type and entity.entity_type != entity_type:
                continue
            
            if entity.distance_to(position) <= radius:
                entities.append(entity)
        
        return entities
    
    def get_entity_count(self) -> int:
        """Get the total number of tracked entities."""
        return len(self._entities)
    
    def get_entity_count_by_type(self, entity_type: EntityType) -> int:
        """
        Get the count of entities of a specific type.
        
        Args:
            entity_type: Entity type
            
        Returns:
            Entity count
        """
        return len(self._entities_by_type.get(entity_type, []))
    
    def cleanup_old_entities(self, max_age_seconds: int = 300) -> int:
        """
        Remove entities that haven't been seen recently.
        
        Args:
            max_age_seconds: Maximum age in seconds
            
        Returns:
            Number of entities removed
        """
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(seconds=max_age_seconds)
        
        to_remove = [
            eid for eid, entity in self._entities.items()
            if entity.last_seen < cutoff
        ]
        
        for eid in to_remove:
            self.remove_entity(eid)
        
        return len(to_remove)
    
    def clear(self) -> None:
        """Clear all entities."""
        self._entities.clear()
        self._entities_by_type.clear()
    
    def __repr__(self) -> str:
        return f"EntityManager(entities={self.get_entity_count()})"
