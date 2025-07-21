"""
Forest Extensions - Advanced features for behavior forests

This module contains advanced features including performance
monitoring and plugin system for behavior forests.
"""

from typing import Any

# Import extension classes from forest module
try:
    from ..plugin_system import (
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
    from ..performance import (
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
    "PLUGIN_SYSTEM_AVAILABLE",
    "PERFORMANCE_MONITORING_AVAILABLE",
] 