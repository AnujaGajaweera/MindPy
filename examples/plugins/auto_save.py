"""
Auto-save plugin example for MindPy.

This plugin periodically saves bot state to prevent data loss.
"""

import asyncio
from mindpy.plugins import Plugin, PluginMetadata
from mindpy.logging import get_logger


class AutoSavePlugin(Plugin):
    """Plugin that periodically saves bot state."""
    
    @property
    def metadata(self):
        """Return plugin metadata."""
        return PluginMetadata(
            name="auto_save",
            version="1.0.0",
            description="Periodically saves bot state to prevent data loss",
            author="MindPy",
            dependencies=[]
        )
    
    async def on_enable(self):
        """Called when the plugin is enabled."""
        self._logger = get_logger(__name__)
        self._logger.info("AutoSavePlugin enabled!")
        
        # Get save interval from config (default 5 minutes)
        config = self._config.get("plugins.auto_save", {})
        self._save_interval = config.get("interval", 300)
        
        self._save_task = asyncio.create_task(self._save_loop())
        self._logger.info(f"Auto-save interval: {self._save_interval} seconds")
    
    async def on_disable(self):
        """Called when the plugin is disabled."""
        self._logger.info("AutoSavePlugin disabled!")
        
        # Cancel the save task
        if self._save_task:
            self._save_task.cancel()
            try:
                await self._save_task
            except asyncio.CancelledError:
                pass
    
    async def _save_loop(self):
        """Periodically save bot state."""
        while True:
            try:
                await asyncio.sleep(self._save_interval)
                await self._save_state()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(f"Error in save loop: {e}")
    
    async def _save_state(self):
        """Save current bot state."""
        self._logger.info("Saving bot state...")
        
        # Save memory state
        await self._memory_manager.save_all()
        
        # Save bot position
        for bot_id, bot in self._bot_manager._bots.items():
            position = bot.get_position()
            self._logger.info(f"Bot {bot_id} position: {position}")
        
        self._logger.info("Bot state saved successfully")


# Required for plugin discovery
plugin = AutoSavePlugin
