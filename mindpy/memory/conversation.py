"""
Conversation memory implementation for MindPy.

Conversation memory tracks chat history and conversations with players.
"""

from typing import Any, Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime
from mindpy.memory.base import Memory, MemoryEntry


@dataclass
class Message:
    """A chat message."""
    sender: str
    content: str
    timestamp: datetime
    message_type: str = "chat"  # chat, private_message, system


class ConversationMemory(Memory):
    """
    Conversation memory for tracking chat history.
    
    Stores messages from chat, private messages, and system messages,
    organized by conversation and player.
    """
    
    def __init__(self, capacity: int = 500, persistence_enabled: bool = True):
        """
        Initialize conversation memory.
        
        Args:
            capacity: Maximum number of messages (default: 500)
            persistence_enabled: Whether to persist to disk
        """
        super().__init__(capacity=capacity, persistence_enabled=persistence_enabled)
        self._conversations: Dict[str, List[str]] = {}  # player_id -> list of entry_ids
    
    def add(self, content: Any, entry_type: str = "message", **metadata) -> MemoryEntry:
        """
        Add a message to conversation memory.
        
        Args:
            content: The message content (Message object or dict)
            entry_type: Type of the entry
            **metadata: Additional metadata
            
        Returns:
            The created memory entry
        """
        if self.is_full():
            self._evict_oldest()
        
        # Convert dict to Message if needed
        if isinstance(content, dict):
            content = Message(
                sender=content.get("sender", "unknown"),
                content=content.get("content", ""),
                timestamp=datetime.fromisoformat(content.get("timestamp", datetime.utcnow().isoformat())),
                message_type=content.get("message_type", "chat")
            )
        
        entry = MemoryEntry(
            content=content,
            entry_type=entry_type,
            metadata=metadata,
            importance=metadata.get("importance", 0.5)
        )
        
        self._entries[entry.entry_id] = entry
        
        # Add to conversation tracking
        sender = content.sender
        if sender not in self._conversations:
            self._conversations[sender] = []
        self._conversations[sender].append(entry.entry_id)
        
        return entry
    
    def add_message(
        self,
        sender: str,
        content: str,
        message_type: str = "chat"
    ) -> MemoryEntry:
        """
        Add a chat message.
        
        Args:
            sender: The sender of the message
            content: The message content
            message_type: Type of message
            
        Returns:
            The memory entry
        """
        message = Message(
            sender=sender,
            content=content,
            timestamp=datetime.utcnow(),
            message_type=message_type
        )
        return self.add(message, "message", importance=0.5)
    
    def get_conversation(self, player: str, limit: int = 50) -> List[Message]:
        """
        Get conversation history with a specific player.
        
        Args:
            player: The player name
            limit: Maximum number of messages
            
        Returns:
            List of messages
        """
        if player not in self._conversations:
            return []
        
        entry_ids = self._conversations[player][-limit:]
        messages = []
        
        for entry_id in entry_ids:
            entry = self.get(entry_id)
            if entry:
                messages.append(entry.content)
                entry.access()
        
        return messages
    
    def get_recent_messages(self, limit: int = 20) -> List[Message]:
        """
        Get recent messages from all conversations.
        
        Args:
            limit: Maximum number of messages
            
        Returns:
            List of recent messages
        """
        messages = self.get_by_type("message")
        messages.sort(key=lambda e: e.timestamp, reverse=True)
        
        for msg in messages[:limit]:
            msg.access()
        
        return [m.content for m in messages[:limit]]
    
    def get_messages_from(self, sender: str, limit: int = 20) -> List[Message]:
        """
        Get messages from a specific sender.
        
        Args:
            sender: The sender name
            limit: Maximum number of messages
            
        Returns:
            List of messages
        """
        messages = self.get_by_type("message")
        from_sender = [m for m in messages if m.content.sender == sender]
        from_sender.sort(key=lambda e: e.timestamp, reverse=True)
        
        for msg in from_sender[:limit]:
            msg.access()
        
        return [m.content for m in from_sender[:limit]]
    
    def search_messages(self, query: str, limit: int = 20) -> List[Message]:
        """
        Search messages by content.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching messages
        """
        messages = self.get_by_type("message")
        matching = [m for m in messages if query.lower() in m.content.content.lower()]
        matching.sort(key=lambda e: e.timestamp, reverse=True)
        
        entry_results = matching[:limit]
        for entry in entry_results:
            entry.access()
        
        return [m.content for m in entry_results]
    
    def get_conversation_partners(self) -> List[str]:
        """
        Get list of all conversation partners.
        
        Returns:
            List of player names
        """
        return list(self._conversations.keys())
