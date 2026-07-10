"""
Player memory implementation for MindPy.

Player memory stores information about other players in the server.
"""

from typing import Any, Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime
from mindpy.memory.base import Memory, MemoryEntry


@dataclass
class PlayerInfo:
    """Information about a player."""
    username: str
    uuid: Optional[str] = None
    first_seen: datetime = None
    last_seen: datetime = None
    position: tuple[float, float, float] = (0.0, 0.0, 0.0)
    health: float = 20.0
    game_mode: str = "survival"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.first_seen is None:
            self.first_seen = datetime.utcnow()
        if self.last_seen is None:
            self.last_seen = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class PlayerInteraction:
    """Record of an interaction with a player."""
    username: str
    interaction_type: str  # chat, trade, combat, team, etc.
    timestamp: datetime
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}


class PlayerMemory(Memory):
    """
    Player memory for storing information about other players.
    
    Tracks player identities, interactions, and relationships.
    """
    
    def __init__(self, capacity: int = 200, persistence_enabled: bool = True):
        """
        Initialize player memory.
        
        Args:
            capacity: Maximum number of entries (default: 200)
            persistence_enabled: Whether to persist to disk
        """
        super().__init__(capacity=capacity, persistence_enabled=persistence_enabled)
        self._player_index: Dict[str, str] = {}  # username -> entry_id
        self._uuid_index: Dict[str, str] = {}  # uuid -> entry_id
    
    def add(self, content: Any, entry_type: str = "player", **metadata) -> MemoryEntry:
        """
        Add player information to memory.
        
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
            importance=metadata.get("importance", 0.6)
        )
        
        self._entries[entry.entry_id] = entry
        
        # Index by type
        if entry_type == "player_info" and isinstance(content, PlayerInfo):
            self._player_index[content.username] = entry.entry_id
            if content.uuid:
                self._uuid_index[content.uuid] = entry.entry_id
        
        return entry
    
    def add_or_update_player(
        self,
        username: str,
        uuid: Optional[str] = None,
        **kwargs
    ) -> MemoryEntry:
        """
        Add or update player information.
        
        Args:
            username: Player username
            uuid: Optional player UUID
            **kwargs: Additional player info
            
        Returns:
            The memory entry
        """
        existing = self.get_player(username)
        
        if existing:
            # Update existing
            existing.last_seen = datetime.utcnow()
            for key, value in kwargs.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            return self.get(self._player_index[username])
        else:
            # Create new
            player_info = PlayerInfo(
                username=username,
                uuid=uuid,
                **kwargs
            )
            return self.add(player_info, "player_info", importance=0.7)
    
    def get_player(self, username: str) -> Optional[PlayerInfo]:
        """
        Get player information by username.
        
        Args:
            username: Player username
            
        Returns:
            PlayerInfo or None if not found
        """
        entry_id = self._player_index.get(username)
        if entry_id:
            entry = self.get(entry_id)
            if entry:
                return entry.content
        return None
    
    def get_player_by_uuid(self, uuid: str) -> Optional[PlayerInfo]:
        """
        Get player information by UUID.
        
        Args:
            uuid: Player UUID
            
        Returns:
            PlayerInfo or None if not found
        """
        entry_id = self._uuid_index.get(uuid)
        if entry_id:
            entry = self.get(entry_id)
            if entry:
                return entry.content
        return None
    
    def add_interaction(
        self,
        username: str,
        interaction_type: str,
        details: Optional[Dict[str, Any]] = None
    ) -> MemoryEntry:
        """
        Record an interaction with a player.
        
        Args:
            username: Player username
            interaction_type: Type of interaction
            details: Interaction details
            
        Returns:
            The memory entry
        """
        interaction = PlayerInteraction(
            username=username,
            interaction_type=interaction_type,
            timestamp=datetime.utcnow(),
            details=details or {}
        )
        return self.add(interaction, "interaction", importance=0.5)
    
    def get_interactions(
        self,
        username: str,
        interaction_type: Optional[str] = None,
        limit: int = 20
    ) -> List[PlayerInteraction]:
        """
        Get interactions with a player.
        
        Args:
            username: Player username
            interaction_type: Optional interaction type filter
            limit: Maximum number of results
            
        Returns:
            List of interactions
        """
        interactions = self.get_by_type("interaction")
        player_interactions = [i for i in interactions if i.content.username == username]
        
        if interaction_type:
            player_interactions = [i for i in player_interactions if i.content.interaction_type == interaction_type]
        
        player_interactions.sort(key=lambda e: e.timestamp, reverse=True)
        
        for interaction in player_interactions[:limit]:
            interaction.access()
        
        return [i.content for i in player_interactions[:limit]]
    
    def get_all_players(self) -> List[PlayerInfo]:
        """Get all known players."""
        players = self.get_by_type("player_info")
        return [p.content for p in players]
    
    def get_recent_players(self, hours: int = 24) -> List[PlayerInfo]:
        """
        Get players seen recently.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of recently seen players
        """
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        players = self.get_by_type("player_info")
        recent = [p for p in players if p.content.last_seen >= cutoff]
        
        return [p.content for p in recent]
    
    def set_relationship(self, username: str, relationship: str) -> None:
        """
        Set relationship status with a player.
        
        Args:
            username: Player username
            relationship: Relationship type (friend, neutral, enemy, etc.)
        """
        player = self.get_player(username)
        if player:
            player.metadata["relationship"] = relationship
    
    def get_relationship(self, username: str) -> Optional[str]:
        """
        Get relationship status with a player.
        
        Args:
            username: Player username
            
        Returns:
            Relationship type or None
        """
        player = self.get_player(username)
        if player:
            return player.metadata.get("relationship")
        return None
