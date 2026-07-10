"""
Bot manager for managing multiple bot instances.
"""

import asyncio
from typing import Dict, List, Optional
from mindpy.bot.bot import Bot
from mindpy.logging import get_logger


class BotManager:
    """
    Manages multiple bot instances.
    
    Provides functionality for creating, tracking, and managing
    multiple bots simultaneously.
    """
    
    def __init__(self):
        """Initialize the bot manager."""
        self._bots: Dict[str, Bot] = {}
        self.logger = get_logger(__name__)
    
    def create_bot(
        self,
        bot_id: str,
        host: str = "localhost",
        port: int = 25565,
        username: str = "MindPyBot",
        password: Optional[str] = None
    ) -> Bot:
        """
        Create a new bot instance.
        
        Args:
            bot_id: Unique identifier for the bot
            host: Server host address
            port: Server port
            username: Bot username
            password: Optional password for authentication
            
        Returns:
            Bot instance
            
        Raises:
            ValueError: If bot_id already exists
        """
        if bot_id in self._bots:
            raise ValueError(f"Bot with id {bot_id} already exists")
        
        bot = Bot(
            host=host,
            port=port,
            username=username,
            password=password
        )
        
        self._bots[bot_id] = bot
        self.logger.info(f"Created bot {bot_id}")
        
        return bot
    
    def get_bot(self, bot_id: str) -> Optional[Bot]:
        """
        Get a bot by ID.
        
        Args:
            bot_id: Bot identifier
            
        Returns:
            Bot instance or None if not found
        """
        return self._bots.get(bot_id)
    
    def remove_bot(self, bot_id: str) -> bool:
        """
        Remove a bot from management.
        
        Args:
            bot_id: Bot identifier
            
        Returns:
            True if bot was removed, False if not found
        """
        if bot_id in self._bots:
            del self._bots[bot_id]
            self.logger.info(f"Removed bot {bot_id}")
            return True
        return False
    
    async def connect_bot(self, bot_id: str) -> bool:
        """
        Connect a specific bot.
        
        Args:
            bot_id: Bot identifier
            
        Returns:
            True if successful, False otherwise
        """
        bot = self.get_bot(bot_id)
        if bot:
            try:
                await bot.connect()
                return True
            except Exception as e:
                self.logger.error(f"Failed to connect bot {bot_id}: {e}")
                return False
        return False
    
    async def disconnect_bot(self, bot_id: str) -> bool:
        """
        Disconnect a specific bot.
        
        Args:
            bot_id: Bot identifier
            
        Returns:
            True if successful, False otherwise
        """
        bot = self.get_bot(bot_id)
        if bot:
            try:
                await bot.disconnect()
                return True
            except Exception as e:
                self.logger.error(f"Failed to disconnect bot {bot_id}: {e}")
                return False
        return False
    
    async def connect_all(self) -> None:
        """Connect all managed bots."""
        tasks = [self.connect_bot(bot_id) for bot_id in self._bots]
        await asyncio.gather(*tasks)
    
    async def disconnect_all(self) -> None:
        """Disconnect all managed bots."""
        tasks = [self.disconnect_bot(bot_id) for bot_id in self._bots]
        await asyncio.gather(*tasks)
    
    async def run_bot(self, bot_id: str) -> None:
        """
        Run a specific bot's main loop.
        
        Args:
            bot_id: Bot identifier
        """
        bot = self.get_bot(bot_id)
        if bot:
            await bot.run()
    
    async def run_all(self) -> None:
        """Run all managed bots concurrently."""
        tasks = [self.run_bot(bot_id) for bot_id in self._bots]
        await asyncio.gather(*tasks)
    
    def get_all_bots(self) -> List[Bot]:
        """Get all managed bots."""
        return list(self._bots.values())
    
    def get_connected_bots(self) -> List[Bot]:
        """Get all connected bots."""
        return [bot for bot in self._bots.values() if bot.is_connected()]
    
    def get_bot_count(self) -> int:
        """Get the total number of managed bots."""
        return len(self._bots)
    
    def get_connected_count(self) -> int:
        """Get the number of connected bots."""
        return len(self.get_connected_bots())
    
    def __repr__(self) -> str:
        return f"BotManager(bots={self.get_bot_count()}, connected={self.get_connected_count()})"
