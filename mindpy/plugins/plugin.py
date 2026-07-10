"""
Plugin base class and metadata.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any
from datetime import datetime


@dataclass
class PluginMetadata:
    """
    Metadata for a plugin.
    
    Plugins should provide this metadata to describe themselves.
    """
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    min_mindpy_version: Optional[str] = None
    max_mindpy_version: Optional[str] = None
    config_schema: Optional[Dict[str, Any]] = None


class Plugin(ABC):
    """
    Base class for MindPy plugins.
    
    All plugins must inherit from this class and implement
    the required lifecycle methods.
    """
    
    def __init__(self):
        """Initialize the plugin."""
        self._enabled = False
        self._loaded = False
        self._config: Dict[str, Any] = {}
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """
        Return plugin metadata.
        
        Returns:
            PluginMetadata instance
        """
        pass
    
    async def on_load(self) -> None:
        """
        Called when the plugin is loaded.
        
        Override this method to perform initialization.
        """
        self._loaded = True
    
    async def on_enable(self) -> None:
        """
        Called when the plugin is enabled.
        
        Override this method to start plugin functionality.
        """
        self._enabled = True
    
    async def on_disable(self) -> None:
        """
        Called when the plugin is disabled.
        
        Override this method to stop plugin functionality.
        """
        self._enabled = False
    
    async def on_unload(self) -> None:
        """
        Called when the plugin is unloaded.
        
        Override this method to perform cleanup.
        """
        self._loaded = False
    
    @property
    def enabled(self) -> bool:
        """Check if the plugin is enabled."""
        return self._enabled
    
    @property
    def loaded(self) -> bool:
        """Check if the plugin is loaded."""
        return self._loaded
    
    def set_config(self, config: Dict[str, Any]) -> None:
        """
        Set plugin configuration.
        
        Args:
            config: Configuration dictionary
        """
        self._config = config
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self._config.get(key, default)
    
    def __repr__(self) -> str:
        return f"Plugin(name={self.metadata.name}, version={self.metadata.version})"
