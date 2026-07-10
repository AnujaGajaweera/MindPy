"""
Plugin system for MindPy.

Provides automatic discovery, dependency management, and lifecycle for plugins.
"""

from mindpy.plugins.plugin import Plugin, PluginMetadata
from mindpy.plugins.manager import PluginManager

__all__ = [
    "Plugin",
    "PluginMetadata",
    "PluginManager",
]
