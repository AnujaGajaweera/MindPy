"""
Core Bot class for MindPy.

Manages bot connection, lifecycle, and core functionality.
"""

import asyncio
from typing import Optional, Dict, Any
from dataclasses import dataclass

from mindpy.events import EventBus, Event, EventTypes
from mindpy.config import Config
from mindpy.plugins import PluginManager
from mindpy.logging import get_logger


@dataclass
class BotState:
    """Represents the current state of the bot."""
    connected: bool = False
    health: float = 20.0
    hunger: float = 20.0
    experience: int = 0
    level: int = 0
    position: tuple[float, float, float] = (0.0, 0.0, 0.0)
    dimension: str = "minecraft:overworld"


class Bot:
    """
    Main bot class for MindPy.
    
    Manages connection to Minecraft servers, event handling,
    and provides the main interface for bot control.
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 25565,
        username: str = "MindPyBot",
        password: Optional[str] = None,
        config: Optional[Config] = None
    ):
        """
        Initialize the bot.
        
        Args:
            host: Server host address
            port: Server port
            username: Bot username
            password: Optional password for authentication
            config: Optional configuration object
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        
        self.config = config or Config()
        self.event_bus = EventBus()
        self.plugin_manager = PluginManager(self.event_bus)
        self.logger = get_logger(__name__)
        
        self.state = BotState()
        self._running = False
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 5
        self._reconnect_delay = 5.0
        
        # PyCraft connection (placeholder - will be integrated)
        self._connection = None
    
    async def connect(self) -> None:
        """
        Connect to the Minecraft server.
        
        Raises:
            ConnectionError: If connection fails
        """
        if self.state.connected:
            self.logger.warning("Bot is already connected")
            return
        
        self.logger.info(f"Connecting to {self.host}:{self.port} as {self.username}")
        
        try:
            # TODO: Integrate with PyCraft here
            # This is a placeholder for the actual PyCraft connection
            await asyncio.sleep(0.1)  # Simulate connection
            
            self.state.connected = True
            self._running = True
            self._reconnect_attempts = 0
            
            # Start event bus
            await self.event_bus.start()
            
            # Publish connected event
            await self.event_bus.publish(Event(
                event_type=EventTypes.BOT_CONNECTED,
                data={
                    "host": self.host,
                    "port": self.port,
                    "username": self.username
                },
                source="bot"
            ))
            
            self.logger.info("Successfully connected to server")
            
        except Exception as e:
            self.logger.error(f"Failed to connect: {e}")
            await self._handle_connection_error(e)
            raise ConnectionError(f"Connection failed: {e}")
    
    async def disconnect(self) -> None:
        """
        Disconnect from the Minecraft server.
        """
        if not self.state.connected:
            self.logger.warning("Bot is not connected")
            return
        
        self.logger.info("Disconnecting from server")
        
        try:
            self._running = False
            
            # Stop event bus
            await self.event_bus.stop()
            
            # TODO: Close PyCraft connection
            if self._connection:
                await self._connection.close()
                self._connection = None
            
            self.state.connected = False
            
            # Publish disconnected event
            await self.event_bus.publish(Event(
                event_type=EventTypes.BOT_DISCONNECTED,
                data={
                    "host": self.host,
                    "port": self.port,
                    "username": self.username
                },
                source="bot"
            ))
            
            self.logger.info("Successfully disconnected from server")
            
        except Exception as e:
            self.logger.error(f"Error during disconnect: {e}")
    
    async def reconnect(self) -> None:
        """
        Attempt to reconnect to the server.
        
        Will retry up to max_reconnect_attempts with exponential backoff.
        """
        if self._reconnect_attempts >= self._max_reconnect_attempts:
            self.logger.error("Max reconnect attempts reached")
            return
        
        self._reconnect_attempts += 1
        delay = self._reconnect_delay * (2 ** (self._reconnect_attempts - 1))
        
        self.logger.info(f"Reconnecting in {delay}s (attempt {self._reconnect_attempts})")
        
        await self.event_bus.publish(Event(
            event_type=EventTypes.BOT_RECONNECTING,
            data={
                "attempt": self._reconnect_attempts,
                "delay": delay
            },
            source="bot"
        ))
        
        await asyncio.sleep(delay)
        
        try:
            await self.disconnect()
            await self.connect()
        except Exception as e:
            self.logger.error(f"Reconnect failed: {e}")
            await self.reconnect()
    
    async def _handle_connection_error(self, error: Exception) -> None:
        """
        Handle connection errors.
        
        Args:
            error: The connection error
        """
        await self.event_bus.publish(Event(
            event_type=EventTypes.BOT_ERROR,
            data={
                "error": str(error),
                "error_type": type(error).__name__
            },
            source="bot"
        ))
    
    async def run(self) -> None:
        """
        Run the bot main loop.
        
        This method blocks until the bot is disconnected.
        """
        if not self.state.connected:
            await self.connect()
        
        while self._running:
            try:
                # Main bot loop
                await asyncio.sleep(0.1)
                
                # TODO: Process PyCraft packets
                # TODO: Update bot state
                # TODO: Handle events
                
            except asyncio.CancelledError:
                self.logger.info("Bot run cancelled")
                break
            except Exception as e:
                self.logger.error(f"Error in bot main loop: {e}")
                await self._handle_connection_error(e)
                await self.reconnect()
    
    async def chat(self, message: str) -> None:
        """
        Send a chat message.
        
        Args:
            message: The message to send
        """
        if not self.state.connected:
            self.logger.warning("Cannot send chat: not connected")
            return
        
        self.logger.info(f"Chat: {message}")
        
        # TODO: Send chat message via PyCraft
        # await self._connection.chat(message)
    
    async def say(self, message: str) -> None:
        """
        Alias for chat.
        
        Args:
            message: The message to send
        """
        await self.chat(message)
    
    def get_position(self) -> tuple[float, float, float]:
        """
        Get the bot's current position.
        
        Returns:
            Tuple of (x, y, z) coordinates
        """
        return self.state.position
    
    def get_health(self) -> float:
        """
        Get the bot's current health.
        
        Returns:
            Current health value
        """
        return self.state.health
    
    def get_hunger(self) -> float:
        """
        Get the bot's current hunger.
        
        Returns:
            Current hunger value
        """
        return self.state.hunger
    
    def is_connected(self) -> bool:
        """
        Check if the bot is connected.
        
        Returns:
            True if connected, False otherwise
        """
        return self.state.connected
    
    def __repr__(self) -> str:
        return f"Bot(username={self.username}, host={self.host}, connected={self.state.connected})"
