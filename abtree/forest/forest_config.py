"""
Forest Configuration - Configuration management for behavior forests

Provides configuration classes and utilities for setting up behavior forests
with different communication patterns and middleware configurations.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set

from .communication import CommunicationType
from .core import ForestNodeType


class MiddlewareConfig(Enum):
    """Middleware configuration enumeration"""
    ENABLED = auto()
    DISABLED = auto()
    CUSTOM = auto()


@dataclass
class CommunicationConfig:
    """Communication pattern configuration"""
    pattern: CommunicationType
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NodeConfig:
    """Forest node configuration"""
    name: str
    node_type: ForestNodeType
    capabilities: Set[str] = field(default_factory=set)
    dependencies: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ForestConfig:
    """
    Behavior Forest Configuration
    
    Configuration class for setting up behavior forests with different
    communication patterns and middleware configurations.
    
    Attributes:
        name: Forest name
        tick_rate: Execution frequency
        enabled_middleware: List of enabled middleware types
        communication_configs: Communication pattern configurations
        node_configs: Node configurations
        global_settings: Global forest settings
    """
    
    name: str = "BehaviorForest"
    tick_rate: float = 60.0
    enabled_middleware: List[CommunicationType] = field(default_factory=list)
    communication_configs: Dict[CommunicationType, CommunicationConfig] = field(default_factory=dict)
    node_configs: List[NodeConfig] = field(default_factory=list)
    global_settings: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Initialize default configurations after creation"""
        if not self.enabled_middleware:
            # Enable all communication patterns by default
            self.enabled_middleware = list(CommunicationType)
        
        # Initialize default communication configs
        for pattern in CommunicationType:
            if pattern not in self.communication_configs:
                self.communication_configs[pattern] = CommunicationConfig(pattern=pattern)
    
    def enable_middleware(self, pattern: CommunicationType) -> None:
        """
        Enable specific middleware pattern
        
        Args:
            pattern: Communication pattern to enable
        """
        if pattern not in self.enabled_middleware:
            self.enabled_middleware.append(pattern)
    
    def disable_middleware(self, pattern: CommunicationType) -> None:
        """
        Disable specific middleware pattern
        
        Args:
            pattern: Communication pattern to disable
        """
        if pattern in self.enabled_middleware:
            self.enabled_middleware.remove(pattern)
    
    def is_middleware_enabled(self, pattern: CommunicationType) -> bool:
        """
        Check if middleware pattern is enabled
        
        Args:
            pattern: Communication pattern to check
            
        Returns:
            True if pattern is enabled
        """
        return pattern in self.enabled_middleware
    
    def configure_communication(self, pattern: CommunicationType, config: Dict[str, Any]) -> None:
        """
        Configure specific communication pattern
        
        Args:
            pattern: Communication pattern to configure
            config: Configuration dictionary
        """
        if pattern not in self.communication_configs:
            self.communication_configs[pattern] = CommunicationConfig(pattern=pattern)
        
        self.communication_configs[pattern].config.update(config)
    
    def add_node_config(self, node_config: NodeConfig) -> None:
        """
        Add node configuration
        
        Args:
            node_config: Node configuration to add
        """
        self.node_configs.append(node_config)
    
    def get_node_config(self, node_name: str) -> Optional[NodeConfig]:
        """
        Get node configuration by name
        
        Args:
            node_name: Name of the node
            
        Returns:
            Node configuration or None if not found
        """
        for config in self.node_configs:
            if config.name == node_name:
                return config
        return None
    
    def set_global_setting(self, key: str, value: Any) -> None:
        """
        Set global forest setting
        
        Args:
            key: Setting key
            value: Setting value
        """
        self.global_settings[key] = value
    
    def get_global_setting(self, key: str, default: Any = None) -> Any:
        """
        Get global forest setting
        
        Args:
            key: Setting key
            default: Default value
            
        Returns:
            Setting value
        """
        return self.global_settings.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary
        
        Returns:
            Configuration dictionary
        """
        return {
            "name": self.name,
            "tick_rate": self.tick_rate,
            "enabled_middleware": [pattern.name for pattern in self.enabled_middleware],
            "communication_configs": {
                pattern.name: {
                    "enabled": config.enabled,
                    "config": config.config
                }
                for pattern, config in self.communication_configs.items()
            },
            "node_configs": [
                {
                    "name": config.name,
                    "node_type": config.node_type.name,
                    "capabilities": list(config.capabilities),
                    "dependencies": list(config.dependencies),
                    "metadata": config.metadata
                }
                for config in self.node_configs
            ],
            "global_settings": self.global_settings
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ForestConfig":
        """
        Create configuration from dictionary
        
        Args:
            data: Configuration dictionary
            
        Returns:
            Forest configuration
        """
        config = cls(
            name=data.get("name", "BehaviorForest"),
            tick_rate=data.get("tick_rate", 60.0)
        )
        
        # Load enabled middleware
        enabled_middleware = data.get("enabled_middleware", [])
        config.enabled_middleware = [
            CommunicationType[pattern] for pattern in enabled_middleware
        ]
        
        # Load communication configs
        communication_configs = data.get("communication_configs", {})
        for pattern_name, pattern_config in communication_configs.items():
            pattern = CommunicationType[pattern_name]
            config.communication_configs[pattern] = CommunicationConfig(
                pattern=pattern,
                enabled=pattern_config.get("enabled", True),
                config=pattern_config.get("config", {})
            )
        
        # Load node configs
        node_configs = data.get("node_configs", [])
        for node_data in node_configs:
            node_config = NodeConfig(
                name=node_data["name"],
                node_type=ForestNodeType[node_data["node_type"]],
                capabilities=set(node_data.get("capabilities", [])),
                dependencies=set(node_data.get("dependencies", [])),
                metadata=node_data.get("metadata", {})
            )
            config.add_node_config(node_config)
        
        # Load global settings
        global_settings = data.get("global_settings", {})
        for key, value in global_settings.items():
            config.set_global_setting(key, value)
        
        return config
    
    def validate(self) -> List[str]:
        """
        Validate configuration
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate name
        if not self.name or not self.name.strip():
            errors.append("Forest name cannot be empty")
        
        # Validate tick rate
        if self.tick_rate <= 0:
            errors.append("Tick rate must be positive")
        
        # Validate node configs
        node_names = set()
        for config in self.node_configs:
            if not config.name or not config.name.strip():
                errors.append("Node name cannot be empty")
            elif config.name in node_names:
                errors.append(f"Duplicate node name: {config.name}")
            else:
                node_names.add(config.name)
        
        # Validate dependencies
        for config in self.node_configs:
            for dependency in config.dependencies:
                if dependency not in node_names:
                    errors.append(f"Node '{config.name}' depends on unknown node '{dependency}'")
        
        return errors
    
    def __repr__(self) -> str:
        return f"ForestConfig(name='{self.name}', nodes={len(self.node_configs)}, middleware={len(self.enabled_middleware)})"


# Predefined configurations
class ForestConfigPresets:
    """Predefined forest configurations"""
    
    @staticmethod
    def basic() -> ForestConfig:
        """Basic forest configuration with all middleware enabled"""
        return ForestConfig(
            name="BasicForest",
            tick_rate=60.0,
            enabled_middleware=list(CommunicationType)
        )
    
    @staticmethod
    def pubsub_only() -> ForestConfig:
        """Forest configuration with only Pub/Sub middleware"""
        return ForestConfig(
            name="PubSubForest",
            tick_rate=60.0,
            enabled_middleware=[CommunicationType.PUB_SUB]
        )
    
    @staticmethod
    def task_oriented() -> ForestConfig:
        """Forest configuration optimized for task distribution"""
        return ForestConfig(
            name="TaskOrientedForest",
            tick_rate=30.0,
            enabled_middleware=[
                CommunicationType.TASK_BOARD,
                CommunicationType.SHARED_BLACKBOARD,
                CommunicationType.STATE_WATCHING
            ]
        )
    
    @staticmethod
    def service_oriented() -> ForestConfig:
        """Forest configuration optimized for service calls"""
        return ForestConfig(
            name="ServiceOrientedForest",
            tick_rate=60.0,
            enabled_middleware=[
                CommunicationType.REQ_RESP,
                CommunicationType.BEHAVIOR_CALL,
                CommunicationType.SHARED_BLACKBOARD
            ]
        )
    
    @staticmethod
    def monitoring() -> ForestConfig:
        """Forest configuration optimized for system monitoring"""
        return ForestConfig(
            name="MonitoringForest",
            tick_rate=10.0,
            enabled_middleware=[
                CommunicationType.STATE_WATCHING,
                CommunicationType.PUB_SUB,
                CommunicationType.SHARED_BLACKBOARD
            ]
        ) 