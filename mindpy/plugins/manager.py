"""
Plugin manager for MindPy.

Handles plugin discovery, loading, dependency resolution, and lifecycle management.
"""

import asyncio
import importlib
import inspect
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Type, Any
from collections import defaultdict

from mindpy.plugins.plugin import Plugin, PluginMetadata
from mindpy.events import EventBus, Event, EventTypes


class PluginManager:
    """
    Manages the plugin lifecycle for MindPy.
    
    Handles discovery, loading, dependency resolution, and
    enables/disables plugins.
    """
    
    def __init__(self, event_bus: EventBus):
        """
        Initialize the plugin manager.
        
        Args:
            event_bus: The event bus for plugin events
        """
        self._event_bus = event_bus
        self._plugins: Dict[str, Plugin] = {}
        self._plugin_paths: List[Path] = []
        self._enabled_plugins: Set[str] = set()
        self._disabled_plugins: Set[str] = set()
        self._loading = False
    
    def add_plugin_path(self, path: Path) -> None:
        """
        Add a path to search for plugins.
        
        Args:
            path: Directory path to search
        """
        path = Path(path)
        if path.exists() and path.is_dir():
            self._plugin_paths.append(path)
            if str(path) not in sys.path:
                sys.path.insert(0, str(path))
    
    async def discover(self) -> List[Type[Plugin]]:
        """
        Discover all available plugins in plugin paths.
        
        Returns:
            List of discovered plugin classes
        """
        discovered = []
        
        for plugin_path in self._plugin_paths:
            for module_file in plugin_path.glob("**/plugin.py"):
                # Import the module
                module_name = module_file.stem
                parent_dir = module_file.parent
                
                if str(parent_dir) not in sys.path:
                    sys.path.insert(0, str(parent_dir))
                
                try:
                    module = importlib.import_module(module_name)
                    
                    # Find Plugin subclasses
                    for name, obj in inspect.getmembers(module):
                        if (
                            inspect.isclass(obj) and
                            issubclass(obj, Plugin) and
                            obj is not Plugin
                        ):
                            discovered.append(obj)
                except Exception as e:
                    print(f"Error loading plugin module {module_name}: {e}")
        
        return discovered
    
    async def load_plugin(self, plugin_class: Type[Plugin]) -> Optional[Plugin]:
        """
        Load a plugin instance.
        
        Args:
            plugin_class: The plugin class to load
            
        Returns:
            Plugin instance or None if loading failed
        """
        metadata = plugin_class().metadata
        name = metadata.name
        
        # Check if already loaded
        if name in self._plugins:
            return self._plugins[name]
        
        # Check dependencies
        for dep in metadata.dependencies:
            if dep not in self._plugins:
                print(f"Plugin {name} requires {dep} which is not loaded")
                return None
        
        try:
            plugin = plugin_class()
            await plugin.on_load()
            
            self._plugins[name] = plugin
            
            # Publish event
            await self._event_bus.publish(Event(
                event_type=EventTypes.PLUGIN_LOADED,
                data={
                    "plugin_name": name,
                    "version": metadata.version
                },
                source="plugin_manager"
            ))
            
            return plugin
        except Exception as e:
            print(f"Error loading plugin {name}: {e}")
            return None
    
    async def enable_plugin(self, plugin_name: str) -> bool:
        """
        Enable a loaded plugin.
        
        Args:
            plugin_name: Name of the plugin to enable
            
        Returns:
            True if successful, False otherwise
        """
        if plugin_name not in self._plugins:
            return False
        
        plugin = self._plugins[plugin_name]
        
        if plugin.enabled:
            return True
        
        try:
            await plugin.on_enable()
            self._enabled_plugins.add(plugin_name)
            self._disabled_plugins.discard(plugin_name)
            return True
        except Exception as e:
            print(f"Error enabling plugin {plugin_name}: {e}")
            return False
    
    async def disable_plugin(self, plugin_name: str) -> bool:
        """
        Disable an enabled plugin.
        
        Args:
            plugin_name: Name of the plugin to disable
            
        Returns:
            True if successful, False otherwise
        """
        if plugin_name not in self._plugins:
            return False
        
        plugin = self._plugins[plugin_name]
        
        if not plugin.enabled:
            return True
        
        try:
            await plugin.on_disable()
            self._enabled_plugins.discard(plugin_name)
            self._disabled_plugins.add(plugin_name)
            return True
        except Exception as e:
            print(f"Error disabling plugin {plugin_name}: {e}")
            return False
    
    async def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin.
        
        Args:
            plugin_name: Name of the plugin to unload
            
        Returns:
            True if successful, False otherwise
        """
        if plugin_name not in self._plugins:
            return False
        
        plugin = self._plugins[plugin_name]
        
        # Disable if enabled
        if plugin.enabled:
            await self.disable_plugin(plugin_name)
        
        try:
            await plugin.on_unload()
            del self._plugins[plugin_name]
            
            # Publish event
            await self._event_bus.publish(Event(
                event_type=EventTypes.PLUGIN_UNLOADED,
                data={"plugin_name": plugin_name},
                source="plugin_manager"
            ))
            
            return True
        except Exception as e:
            print(f"Error unloading plugin {plugin_name}: {e}")
            return False
    
    async def load_all(self) -> None:
        """Load all discovered plugins."""
        if self._loading:
            return
        
        self._loading = True
        
        try:
            plugin_classes = await self.discover()
            
            # Sort by dependencies (topological sort)
            sorted_plugins = self._sort_by_dependencies(plugin_classes)
            
            for plugin_class in sorted_plugins:
                await self.load_plugin(plugin_class)
        finally:
            self._loading = False
    
    def _sort_by_dependencies(self, plugin_classes: List[Type[Plugin]]) -> List[Type[Plugin]]:
        """
        Sort plugins by dependencies using topological sort.
        
        Args:
            plugin_classes: List of plugin classes
            
        Returns:
            Sorted list of plugin classes
        """
        # Build dependency graph
        graph = defaultdict(list)
        in_degree = {}
        
        for plugin_class in plugin_classes:
            metadata = plugin_class().metadata
            name = metadata.name
            in_degree[name] = len(metadata.dependencies)
            
            for dep in metadata.dependencies:
                graph[dep].append(name)
        
        # Topological sort
        queue = [name for name, degree in in_degree.items() if degree == 0]
        result = []
        
        plugin_map = {pc().metadata.name: pc for pc in plugin_classes}
        
        while queue:
            node = queue.pop(0)
            result.append(plugin_map[node])
            
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return result
    
    def get_plugin(self, name: str) -> Optional[Plugin]:
        """
        Get a plugin by name.
        
        Args:
            name: Plugin name
            
        Returns:
            Plugin instance or None
        """
        return self._plugins.get(name)
    
    def get_enabled_plugins(self) -> List[Plugin]:
        """Get all enabled plugins."""
        return [self._plugins[name] for name in self._enabled_plugins]
    
    def get_disabled_plugins(self) -> List[Plugin]:
        """Get all disabled plugins."""
        return [self._plugins[name] for name in self._disabled_plugins]
    
    def get_all_plugins(self) -> List[Plugin]:
        """Get all loaded plugins."""
        return list(self._plugins.values())
    
    def is_enabled(self, plugin_name: str) -> bool:
        """Check if a plugin is enabled."""
        return plugin_name in self._enabled_plugins
    
    def is_loaded(self, plugin_name: str) -> bool:
        """Check if a plugin is loaded."""
        return plugin_name in self._plugins
