"""
Behavior Forest - Multi-Behavior Tree Collaboration Framework

A high-performance asynchronous behavior forest framework that enables multiple behavior trees
to collaborate through various communication patterns, supporting complex multi-agent systems.
"""

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
    ForestVisualizer = None
    ForestDashboard = None
    create_forest_visualizer = None
    create_forest_dashboard = None

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
    PluginManager = None
    BasePlugin = None
    PluginInfo = None
    create_plugin_manager = None

try:
    from .performance import (
        PerformanceMonitor,
        create_performance_monitor,
        monitor_forest_performance,
    )
    PERFORMANCE_MONITORING_AVAILABLE = True
except ImportError:
    PERFORMANCE_MONITORING_AVAILABLE = False
    PerformanceMonitor = None
    create_performance_monitor = None
    monitor_forest_performance = None

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