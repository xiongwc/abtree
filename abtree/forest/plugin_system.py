"""
Behavior Forest Plugin System

This module provides a plugin system for extending behavior forest functionality
with custom middleware, nodes, utilities, and other components.
"""

import asyncio
import importlib
import inspect
import logging
import os
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, Union

from typing_extensions import Protocol

from .core import BehaviorForest, ForestNode, ForestNodeType


class PluginInterface(Protocol):
    """Protocol defining the interface for forest plugins."""
    
    def initialize(self, forest: BehaviorForest) -> None:
        """Initialize the plugin with a forest."""
        ...
    
    def cleanup(self) -> None:
        """Clean up plugin resources."""
        ...
    
    def get_name(self) -> str:
        """Get the plugin name."""
        ...
    
    def get_version(self) -> str:
        """Get the plugin version."""
        ...


class BasePlugin(ABC):
    """Base class for all forest plugins."""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.forest: Optional[BehaviorForest] = None
        self.logger = logging.getLogger(f"Plugin.{name}")
        
    @abstractmethod
    def initialize(self, forest: BehaviorForest) -> None:
        """Initialize the plugin with a forest."""
        self.forest = forest
        self.logger.info(f"Initialized plugin '{self.name}' v{self.version}")
        
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up plugin resources."""
        self.logger.info(f"Cleaned up plugin '{self.name}'")
        
    def get_name(self) -> str:
        """Get the plugin name."""
        return self.name
        
    def get_version(self) -> str:
        """Get the plugin version."""
        return self.version


@dataclass
class PluginInfo:
    """Information about a plugin."""
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    plugin_class: Optional[Type[BasePlugin]] = None


class MiddlewarePlugin(BasePlugin):
    """Base class for middleware plugins."""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        super().__init__(name, version)
        self.middleware = None
        
    def initialize(self, forest: BehaviorForest) -> None:
        """Initialize the middleware plugin."""
        super().initialize(forest)
        self.middleware = self.create_middleware()
        if self.middleware:
            forest.add_middleware(self.middleware)
            
    @abstractmethod
    def create_middleware(self) -> Any:
        """Create the middleware instance."""
        raise NotImplementedError


class NodePlugin(BasePlugin):
    """Base class for custom node plugins."""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        super().__init__(name, version)
        self.custom_nodes: Dict[str, Type] = {}
        
    def initialize(self, forest: BehaviorForest) -> None:
        """Initialize the node plugin."""
        super().initialize(forest)
        self.register_custom_nodes()
        
    @abstractmethod
    def register_custom_nodes(self) -> None:
        """Register custom node types."""
        raise NotImplementedError


class UtilityPlugin(BasePlugin):
    """Base class for utility plugins."""
    
    def initialize(self, forest: BehaviorForest) -> None:
        """Initialize the utility plugin."""
        super().initialize(forest)
        self.setup_utilities()
        
    @abstractmethod
    def setup_utilities(self) -> None:
        """Setup utility functions."""
        raise NotImplementedError


class PluginManager:
    """
    Manager for behavior forest plugins.
    
    Handles plugin discovery, loading, initialization, and lifecycle management.
    """
    
    def __init__(self):
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_info: Dict[str, PluginInfo] = {}
        self.plugin_paths: List[Path] = []
        self.logger = logging.getLogger("PluginManager")
        
    def add_plugin_path(self, path: Union[str, Path]) -> None:
        """Add a path for plugin discovery."""
        plugin_path = Path(path)
        if plugin_path.exists() and plugin_path.is_dir():
            self.plugin_paths.append(plugin_path)
            self.logger.info(f"Added plugin path: {plugin_path}")
        else:
            self.logger.warning(f"Plugin path does not exist: {plugin_path}")
            
    def discover_plugins(self) -> List[PluginInfo]:
        """Discover available plugins in plugin paths."""
        discovered_plugins = []
        
        for plugin_path in self.plugin_paths:
            for plugin_file in plugin_path.glob("*.py"):
                if plugin_file.name.startswith("_"):
                    continue
                    
                try:
                    plugin_info = self._load_plugin_info(plugin_file)
                    if plugin_info:
                        discovered_plugins.append(plugin_info)
                        self.plugin_info[plugin_info.name] = plugin_info
                except Exception as e:
                    self.logger.error(f"Failed to load plugin from {plugin_file}: {e}")
                    
        return discovered_plugins
    
    def _load_plugin_info(self, plugin_file: Path) -> Optional[PluginInfo]:
        """Load plugin information from a file."""
        try:
            # Create a temporary module
            spec = importlib.util.spec_from_file_location(  # type: ignore[attr-defined]
                f"plugin_{plugin_file.stem}", plugin_file
            )
            if spec.loader is None:
                return None
            module = importlib.util.module_from_spec(spec)  # type: ignore[attr-defined]
            spec.loader.exec_module(module)
            
            # Look for plugin class
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BasePlugin) and 
                    obj != BasePlugin):
                    plugin_class = obj
                    break
            
            # If no plugin class found, return None
            if plugin_class is None:
                return None
                
            # Create plugin info
            plugin_info = PluginInfo(
                name=getattr(plugin_class, 'PLUGIN_NAME', plugin_class.__name__),
                version=getattr(plugin_class, 'PLUGIN_VERSION', '1.0.0'),
                description=getattr(plugin_class, 'PLUGIN_DESCRIPTION', ''),
                author=getattr(plugin_class, 'PLUGIN_AUTHOR', 'Unknown'),
                dependencies=getattr(plugin_class, 'PLUGIN_DEPENDENCIES', []),
                tags=getattr(plugin_class, 'PLUGIN_TAGS', []),
                plugin_class=plugin_class
            )
            
            return plugin_info
            
        except Exception as e:
            self.logger.error(f"Error loading plugin info from {plugin_file}: {e}")
            return None
    
    def load_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Load a specific plugin by name."""
        if plugin_name in self.plugins:
            return self.plugins[plugin_name]
            
        if plugin_name not in self.plugin_info:
            self.logger.error(f"Plugin '{plugin_name}' not found")
            return None
            
        plugin_info = self.plugin_info[plugin_name]
        
        try:
            if plugin_info.plugin_class is None:
                return None
            plugin = plugin_info.plugin_class(plugin_name)
            self.plugins[plugin_name] = plugin
            self.logger.info(f"Loaded plugin '{plugin_name}' v{plugin.version}")
            return plugin
        except Exception as e:
            self.logger.error(f"Failed to load plugin '{plugin_name}': {e}")
            return None
    
    def load_all_plugins(self) -> List[BasePlugin]:
        """Load all discovered plugins."""
        loaded_plugins = []
        
        for plugin_name in self.plugin_info:
            plugin = self.load_plugin(plugin_name)
            if plugin:
                loaded_plugins.append(plugin)
                
        return loaded_plugins
    
    def initialize_plugin(self, plugin: BasePlugin, forest: BehaviorForest) -> bool:
        """Initialize a plugin with a forest."""
        try:
            plugin.initialize(forest)
            self.logger.info(f"Initialized plugin '{plugin.name}' with forest '{forest.name}'")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize plugin '{plugin.name}': {e}")
            return False
    
    def initialize_all_plugins(self, forest: BehaviorForest) -> List[BasePlugin]:
        """Initialize all loaded plugins with a forest."""
        initialized_plugins = []
        
        for plugin in self.plugins.values():
            if self.initialize_plugin(plugin, forest):
                initialized_plugins.append(plugin)
                
        return initialized_plugins
    
    def cleanup_plugin(self, plugin_name: str) -> bool:
        """Clean up a specific plugin."""
        if plugin_name not in self.plugins:
            return False
            
        plugin = self.plugins[plugin_name]
        try:
            plugin.cleanup()
            del self.plugins[plugin_name]
            self.logger.info(f"Cleaned up plugin '{plugin_name}'")
            return True
        except Exception as e:
            self.logger.error(f"Failed to cleanup plugin '{plugin_name}': {e}")
            return False
    
    def cleanup_all_plugins(self) -> None:
        """Clean up all loaded plugins."""
        plugin_names = list(self.plugins.keys())
        for plugin_name in plugin_names:
            self.cleanup_plugin(plugin_name)
    
    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """Get information about a plugin."""
        return self.plugin_info.get(plugin_name)
    
    def list_plugins(self) -> List[PluginInfo]:
        """List all available plugins."""
        return list(self.plugin_info.values())
    
    def list_loaded_plugins(self) -> List[str]:
        """List all loaded plugin names."""
        return list(self.plugins.keys())


# Example plugins
class ExampleMiddlewarePlugin(MiddlewarePlugin):
    """Example middleware plugin."""
    
    PLUGIN_NAME = "ExampleMiddleware"
    PLUGIN_VERSION = "1.0.0"
    PLUGIN_DESCRIPTION = "Example middleware plugin for demonstration"
    PLUGIN_AUTHOR = "ABTree Team"
    PLUGIN_TAGS = ["example", "middleware"]
    
    def create_middleware(self) -> Any:
        """Create example middleware."""
        from .communication import CommunicationMiddleware
        return CommunicationMiddleware("ExampleCommunication")
    
    def cleanup(self) -> None:
        """Clean up plugin resources."""
        super().cleanup()


class ExampleNodePlugin(NodePlugin):
    """Example node plugin."""
    
    PLUGIN_NAME = "ExampleNodes"
    PLUGIN_VERSION = "1.0.0"
    PLUGIN_DESCRIPTION = "Example custom nodes for demonstration"
    PLUGIN_AUTHOR = "ABTree Team"
    PLUGIN_TAGS = ["example", "nodes"]
    
    def register_custom_nodes(self) -> None:
        """Register custom node types."""
        from abtree.core import Status
        from abtree.nodes.action import Action
        
        class ExampleAction(Action):
            """Example custom action node."""
            
            def __init__(self, name: str, message: str = "Hello from plugin!"):
                super().__init__(name)
                self.message = message
                
            async def execute(self, blackboard) -> Status:
                print(f"Plugin Action: {self.message}")
                return Status.SUCCESS
        
        self.custom_nodes["ExampleAction"] = ExampleAction
    
    def cleanup(self) -> None:
        """Clean up plugin resources."""
        super().cleanup()


def create_plugin_manager() -> PluginManager:
    """Create a plugin manager instance."""
    return PluginManager()


def load_plugin_from_file(file_path: str) -> Optional[BasePlugin]:
    """Load a plugin from a file."""
    plugin_file = Path(file_path)
    if not plugin_file.exists():
        return None
        
    manager = PluginManager()
    manager.add_plugin_path(plugin_file.parent)
    plugins = manager.discover_plugins()
    
    if plugins:
        return manager.load_plugin(plugins[0].name)
    return None 