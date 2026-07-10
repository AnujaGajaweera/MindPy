"""
Chat responder plugin example for MindPy.

This plugin responds to chat messages with predefined responses.
"""

import asyncio
from mindpy.plugins import Plugin, PluginMetadata
from mindpy.events import Event, EventTypes
from mindpy.logging import get_logger


class ChatResponderPlugin(Plugin):
    """Plugin that responds to chat messages."""
    
    @property
    def metadata(self):
        """Return plugin metadata."""
        return PluginMetadata(
            name="chat_responder",
            version="1.0.0",
            description="Responds to chat messages with predefined responses",
            author="MindPy",
            dependencies=[]
        )
    
    async def on_enable(self):
        """Called when the plugin is enabled."""
        self._logger = get_logger(__name__)
        self._logger.info("ChatResponderPlugin enabled!")
        
        # Define responses
        self._responses = {
            "hello": "Hi there!",
            "hi": "Hello!",
            "help": "I'm a MindPy bot. Try saying 'hello' or 'status'!",
            "status": "I'm running normally!",
            "who are you": "I'm a MindPy AI-powered Minecraft bot!",
            "time": lambda: f"The current time is {asyncio.get_event_loop().time():.0f}"
        }
        
        # Subscribe to chat events
        self._event_bus.subscribe(
            EventTypes.CHAT_MESSAGE,
            self._on_chat
        )
    
    async def on_disable(self):
        """Called when the plugin is disabled."""
        self._logger.info("ChatResponderPlugin disabled!")
        
        # Unsubscribe from events
        self._event_bus.unsubscribe(
            EventTypes.CHAT_MESSAGE,
            self._on_chat
        )
    
    async def _on_chat(self, event: Event):
        """Handle chat messages."""
        message = event.data.get("message", "").lower().strip()
        sender = event.data.get("sender", "Unknown")
        bot_id = event.data.get("bot_id")
        
        # Get the bot instance
        bot = self._bot_manager.get_bot(bot_id)
        if not bot:
            return
        
        # Check for matching response
        response = None
        for key, value in self._responses.items():
            if key in message:
                if callable(value):
                    response = value()
                else:
                    response = value
                break
        
        if response:
            self._logger.info(f"Responding to {sender}: {response}")
            await bot.chat(response)


# Required for plugin discovery
plugin = ChatResponderPlugin
