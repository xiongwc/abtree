"""
Forest Extensions - Advanced features for behavior forests

This module contains advanced features including visualization, performance
monitoring, and plugin system for behavior forests.
"""

# Import extension classes from forest module
try:
    from ..visualization import ForestVisualizer, ForestDashboard, create_forest_visualizer, create_forest_dashboard
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    ForestVisualizer = None
    ForestDashboard = None
    create_forest_visualizer = None
    create_forest_dashboard = None

try:
    from ..plugin_system import PluginManager, BasePlugin, PluginInfo, create_plugin_manager
    PLUGIN_SYSTEM_AVAILABLE = True
except ImportError:
    PLUGIN_SYSTEM_AVAILABLE = False
    PluginManager = None
    BasePlugin = None
    PluginInfo = None
    create_plugin_manager = None

try:
    from ..performance import PerformanceMonitor, create_performance_monitor, monitor_forest_performance
    PERFORMANCE_MONITORING_AVAILABLE = True
except ImportError:
    PERFORMANCE_MONITORING_AVAILABLE = False
    PerformanceMonitor = None
    create_performance_monitor = None
    monitor_forest_performance = None

__all__ = [
    # Visualization
    "ForestVisualizer",
    "ForestDashboard",
    "create_forest_visualizer", 
    "create_forest_dashboard",
    
    # Plugin system
    "PluginManager",
    "BasePlugin",
    "PluginInfo",
    "create_plugin_manager",
    
    # Performance monitoring
    "PerformanceMonitor",
    "create_performance_monitor",
    "monitor_forest_performance",
    
    # Availability flags
    "VISUALIZATION_AVAILABLE",
    "PLUGIN_SYSTEM_AVAILABLE",
    "PERFORMANCE_MONITORING_AVAILABLE",
] 