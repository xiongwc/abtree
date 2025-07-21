"""
Behavior Forest - Multi-Behavior Tree Collaboration Framework

A high-performance asynchronous behavior forest framework that enables multiple behavior trees
to collaborate through various communication patterns, supporting complex multi-agent systems.
"""

from typing import Any

from .core import BehaviorForest, ForestNode, ForestNodeType
from .forest_config import ForestConfig, ForestConfigPresets
from .forest_manager import ForestManager

# Advanced features
try:
    from .visualization import (
        ForestDashboard,
        ForestVisualizer,
        create_forest_dashboard,
        create_forest_visualizer,
    )
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    ForestVisualizer: Any = None  # type: ignore[no-redef]
    ForestDashboard: Any = None  # type: ignore[no-redef]
    create_forest_visualizer: Any = None  # type: ignore[no-redef]
    create_forest_dashboard: Any = None  # type: ignore[no-redef]

try:
    from .plugin_system import (
        BasePlugin,
        PluginInfo,
        PluginManager,
        create_plugin_manager,
    )
    PLUGIN_SYSTEM_AVAILABLE = True
except ImportError:
    PLUGIN_SYSTEM_AVAILABLE = False
    PluginManager: Any = None  # type: ignore[no-redef]
    BasePlugin: Any = None  # type: ignore[no-redef]
    PluginInfo: Any = None  # type: ignore[no-redef]
    create_plugin_manager: Any = None  # type: ignore[no-redef]

try:
    from .performance import (
        PerformanceMonitor,
        create_performance_monitor,
        monitor_forest_performance,
    )
    PERFORMANCE_MONITORING_AVAILABLE = True
except ImportError:
    PERFORMANCE_MONITORING_AVAILABLE = False
    PerformanceMonitor: Any = None  # type: ignore[no-redef]
    create_performance_monitor: Any = None  # type: ignore[no-redef]
    monitor_forest_performance: Any = None  # type: ignore[no-redef]

__all__ = [
    # Core classes
    "BehaviorForest",
    "ForestNode",
    "ForestNodeType",
    
    # Management
    "ForestManager",
    
    # Configuration
    "ForestConfig",
    "ForestConfigPresets",
    
    # Advanced features (conditional)
    "ForestVisualizer",
    "ForestDashboard", 
    "create_forest_visualizer",
    "create_forest_dashboard",
    "PluginManager",
    "BasePlugin",
    "PluginInfo",
    "create_plugin_manager",
    "PerformanceMonitor",
    "create_performance_monitor",
    "monitor_forest_performance",
    
    # Availability flags
    "VISUALIZATION_AVAILABLE",
    "PLUGIN_SYSTEM_AVAILABLE", 
    "PERFORMANCE_MONITORING_AVAILABLE"
] 