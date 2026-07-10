"""
MindPy - A Python AI framework for controlling Minecraft bots.

This package provides a comprehensive framework for building intelligent
Minecraft bots using PyCraft as the backend.
"""

__version__ = "0.1.0"
__author__ = "MindPy Contributors"
__license__ = "MIT"

from mindpy.bot import Bot
from mindpy.events import EventBus, Event
from mindpy.config import Config
from mindpy.plugins import Plugin, PluginManager

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "Bot",
    "EventBus",
    "Event",
    "Config",
    "Plugin",
    "PluginManager",
]
