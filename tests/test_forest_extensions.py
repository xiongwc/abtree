import pytest
from unittest.mock import Mock, patch
from abtree.forest.extensions import (
    PLUGIN_SYSTEM_AVAILABLE, PERFORMANCE_MONITORING_AVAILABLE,
    PluginManager, BasePlugin, PluginInfo, create_plugin_manager,
    PerformanceMonitor, create_performance_monitor, monitor_forest_performance
)
from abtree.forest.core import BehaviorForest
import asyncio


class TestForestExtensions:
    """Test forest extensions"""
    
    def test_extension_availability(self):
        """Test extension availability"""
        # Check plugin system availability
        assert isinstance(PLUGIN_SYSTEM_AVAILABLE, bool)
        
        # Check performance monitoring availability
        assert isinstance(PERFORMANCE_MONITORING_AVAILABLE, bool)
    
    def test_plugin_system_imports(self):
        """Test plugin system imports"""
        if PLUGIN_SYSTEM_AVAILABLE:
            assert PluginManager is not None
            assert BasePlugin is not None
            assert PluginInfo is not None
            assert create_plugin_manager is not None
        else:
            assert PluginManager is None
            assert BasePlugin is None
            assert PluginInfo is None
            assert create_plugin_manager is None
    
    def test_performance_monitoring_imports(self):
        """Test performance monitoring imports"""
        if PERFORMANCE_MONITORING_AVAILABLE:
            assert PerformanceMonitor is not None
            assert create_performance_monitor is not None
            assert monitor_forest_performance is not None
        else:
            assert PerformanceMonitor is None
            assert create_performance_monitor is None
            assert monitor_forest_performance is None


class TestPluginSystemIntegration:
    """Test plugin system integration"""
    
    @pytest.fixture
    def forest(self):
        """Create test forest"""
        return BehaviorForest("TestForest")
    
    @pytest.mark.skipif(not PLUGIN_SYSTEM_AVAILABLE, reason="Plugin system not available")
    def test_plugin_manager_creation(self):
        """Test plugin manager creation"""
        manager = create_plugin_manager()
        assert isinstance(manager, PluginManager)
    
    @pytest.mark.skipif(not PLUGIN_SYSTEM_AVAILABLE, reason="Plugin system not available")
    def test_base_plugin_creation(self):
        """Test base plugin creation"""
        class TestPlugin(BasePlugin):
            def initialize(self, forest):
                pass
            
            def cleanup(self):
                pass
        
        plugin = TestPlugin("TestPlugin", "1.0.0")
        assert isinstance(plugin, BasePlugin)
        assert plugin.name == "TestPlugin"
        assert plugin.version == "1.0.0"
    
    @pytest.mark.skipif(not PLUGIN_SYSTEM_AVAILABLE, reason="Plugin system not available")
    def test_plugin_info_creation(self):
        """Test plugin info creation"""
        plugin_info = PluginInfo(
            name="TestPlugin",
            version="1.0.0",
            description="Test plugin",
            author="Test Author"
        )
        assert isinstance(plugin_info, PluginInfo)
        assert plugin_info.name == "TestPlugin"
    
    @pytest.mark.skipif(not PLUGIN_SYSTEM_AVAILABLE, reason="Plugin system not available")
    def test_plugin_lifecycle(self, forest):
        """Test plugin lifecycle"""
        class TestPlugin(BasePlugin):
            def initialize(self, forest):
                self.forest = forest
            
            def cleanup(self):
                pass
        
        plugin = TestPlugin("TestPlugin", "1.0.0")
        
        # Initialize plugin
        plugin.initialize(forest)
        assert plugin.forest == forest
        
        # Cleanup plugin
        plugin.cleanup()
    
    @pytest.mark.skipif(not PLUGIN_SYSTEM_AVAILABLE, reason="Plugin system not available")
    def test_plugin_manager_operations(self, forest):
        """Test plugin manager operations"""
        manager = create_plugin_manager()
        
        class TestPlugin(BasePlugin):
            def initialize(self, forest):
                pass
            
            def cleanup(self):
                pass
        
        plugin = TestPlugin("TestPlugin", "1.0.0")
        
        # Add plugin to manager
        manager.plugins["TestPlugin"] = plugin
        
        # Initialize plugin
        plugins = manager.initialize_all_plugins(forest)
        assert len(plugins) == 1
        
        # Cleanup plugin
        manager.cleanup_all_plugins()
        assert len(manager.plugins) == 0


class TestPerformanceMonitoringIntegration:
    """Test performance monitoring integration"""
    
    @pytest.fixture
    def forest(self):
        """Create test forest"""
        return BehaviorForest("TestForest")
    
    @pytest.mark.skipif(not PERFORMANCE_MONITORING_AVAILABLE, reason="Performance monitoring not available")
    def test_performance_monitor_creation(self, forest):
        """Test performance monitor creation"""
        monitor = create_performance_monitor(forest)
        assert isinstance(monitor, PerformanceMonitor)
        assert monitor.forest == forest
    
    @pytest.mark.skipif(not PERFORMANCE_MONITORING_AVAILABLE, reason="Performance monitoring not available")
    def test_performance_decorator_creation(self, forest):
        """Test performance decorator creation"""
        monitor = create_performance_monitor(forest)
        decorator = monitor_forest_performance(monitor)
        assert decorator is not None
    
    @pytest.mark.skipif(not PERFORMANCE_MONITORING_AVAILABLE, reason="Performance monitoring not available")
    def test_performance_monitor_operations(self, forest):
        """Test performance monitor operations"""
        monitor = create_performance_monitor(forest)
        
        # Record execution data
        monitor.record_forest_execution(1.0, True)
        monitor.record_node_execution("test_node", 0.5, True)
        monitor.record_middleware_execution("test_middleware", 0.1, False)
        
        # Get performance report
        report = monitor.get_forest_performance_report()
        assert "forest_metrics" in report
        assert "node_performance" in report
        assert "middleware_performance" in report
        
        # Get performance summary
        summary = monitor.get_performance_summary()
        assert isinstance(summary, str)
        assert "TestForest" in summary
    
    @pytest.mark.skipif(not PERFORMANCE_MONITORING_AVAILABLE, reason="Performance monitoring not available")
    @pytest.mark.asyncio
    async def test_performance_monitor_async_operations(self, forest):
        """Test performance monitor async operations"""
        monitor = create_performance_monitor(forest)
        
        # Start monitoring
        await monitor.start_monitoring(interval=0.1)
        assert monitor.monitoring is True
        
        # Wait for a short time
        await asyncio.sleep(0.2)
        
        # Stop monitoring
        await monitor.stop_monitoring()
        assert monitor.monitoring is False


class TestExtensionErrorHandling:
    """Test extension error handling"""
    
    def test_extension_import_errors(self):
        """Test extension import error handling"""
        # These tests verify that the extension module can gracefully handle import errors
        # Even if some dependencies are unavailable, the module should still be able to import
        
        # Verify extension module can import
        from abtree.forest import extensions
        assert extensions is not None
        
        # 验证可用性标志存在
        assert hasattr(extensions, 'PLUGIN_SYSTEM_AVAILABLE')
        assert hasattr(extensions, 'PERFORMANCE_MONITORING_AVAILABLE')
    
    @pytest.mark.skipif(PLUGIN_SYSTEM_AVAILABLE, reason="Plugin system is available")
    def test_plugin_system_unavailable(self):
        """Test plugin system unavailable behavior"""
        # When plugin system is unavailable, related classes should be None
        assert PluginManager is None
        assert BasePlugin is None
        assert PluginInfo is None
        assert create_plugin_manager is None
    
    @pytest.mark.skipif(PERFORMANCE_MONITORING_AVAILABLE, reason="Performance monitoring is available")
    def test_performance_monitoring_unavailable(self):
        """Test performance monitoring unavailable behavior"""
        # When performance monitoring is unavailable, related classes should be None
        assert PerformanceMonitor is None
        assert create_performance_monitor is None
        assert monitor_forest_performance is None


class TestExtensionIntegration:
    """Test extension integration"""
    
    @pytest.fixture
    def forest(self):
        """Create test forest"""
        return BehaviorForest("TestForest")
    
    def test_extension_module_structure(self):
        """Test extension module structure"""
        from abtree.forest import extensions
        
        # Verify module contains necessary attributes
        assert hasattr(extensions, '__all__')
        assert 'PLUGIN_SYSTEM_AVAILABLE' in extensions.__all__
        assert 'PERFORMANCE_MONITORING_AVAILABLE' in extensions.__all__
    
    @pytest.mark.skipif(not PLUGIN_SYSTEM_AVAILABLE, reason="Plugin system not available")
    def test_plugin_system_with_forest(self, forest):
        """Test plugin system with forest integration"""
        manager = create_plugin_manager()
        
        class TestPlugin(BasePlugin):
            def initialize(self, forest):
                self.forest = forest
            
            def cleanup(self):
                pass
        
        plugin = TestPlugin("TestPlugin", "1.0.0")
        manager.plugins["TestPlugin"] = plugin
        
        # Initialize plugin
        plugins = manager.initialize_all_plugins(forest)
        assert len(plugins) == 1
        assert plugins[0].forest == forest
        
        # Verify plugin info
        plugin_info = manager.get_plugin_info("TestPlugin")
        assert plugin_info is None  # Because we didn't add plugin info through normal process
        
        # Cleanup plugin
        manager.cleanup_all_plugins()
    
    @pytest.mark.skipif(not PERFORMANCE_MONITORING_AVAILABLE, reason="Performance monitoring not available")
    def test_performance_monitoring_with_forest(self, forest):
        """Test performance monitoring with forest integration"""
        monitor = create_performance_monitor(forest)
        
        # Record some execution data
        monitor.record_forest_execution(1.0, True)
        monitor.record_forest_execution(2.0, False)
        monitor.record_node_execution("node1", 0.5, True)
        monitor.record_node_execution("node2", 0.3, False)
        
        # Get stats
        report = monitor.get_forest_performance_report()
        
        # Verify forest metrics
        forest_metrics = report["forest_metrics"]
        assert forest_metrics["total_executions"] == 2
        assert forest_metrics["successful_executions"] == 1
        assert forest_metrics["failed_executions"] == 1
        
        # Verify node metrics
        node_performance = report["node_performance"]
        assert "node1" in node_performance
        assert "node2" in node_performance
        
        # Verify summary
        summary = monitor.get_performance_summary()
        assert "TestForest" in summary
        assert "50.0%" in summary  # Success rate
    
    def test_extension_availability_flags(self):
        """Test extension availability flags"""
        # Verify type of availability flags
        assert isinstance(PLUGIN_SYSTEM_AVAILABLE, bool)
        assert isinstance(PERFORMANCE_MONITORING_AVAILABLE, bool)
        
        # Verify consistency of flags
        if PLUGIN_SYSTEM_AVAILABLE:
            assert PluginManager is not None
        else:
            assert PluginManager is None
        
        if PERFORMANCE_MONITORING_AVAILABLE:
            assert PerformanceMonitor is not None
        else:
            assert PerformanceMonitor is None


class TestExtensionEdgeCases:
    """Test extension edge cases"""
    
    @pytest.fixture
    def forest(self):
        """Create test forest"""
        return BehaviorForest("TestForest")
    
    @pytest.mark.skipif(not PLUGIN_SYSTEM_AVAILABLE, reason="Plugin system not available")
    def test_plugin_with_invalid_forest(self):
        """Test plugin with invalid forest"""
        class TestPlugin(BasePlugin):
            def initialize(self, forest):
                pass
            
            def cleanup(self):
                pass
        
        plugin = TestPlugin("TestPlugin", "1.0.0")
        
        # Test with None forest
        plugin.initialize(None)
        assert plugin.forest is None
        
        # Test cleanup
        plugin.cleanup()
    
    @pytest.mark.skipif(not PERFORMANCE_MONITORING_AVAILABLE, reason="Performance monitoring not available")
    def test_performance_monitor_with_invalid_forest(self):
        """Test performance monitor with invalid forest"""
        # Test with None forest - this should handle gracefully
        monitor = None
        try:
            monitor = create_performance_monitor(None)
            # If it doesn't raise an exception, it should handle None gracefully
            assert monitor.forest is None
        except AttributeError:
            # Expected behavior when forest is None
            return
        
        # Record some data
        monitor.record_forest_execution(1.0, True)
        
        # Get report
        report = monitor.get_forest_performance_report()
        assert "forest_metrics" in report
    
    @pytest.mark.skipif(not PLUGIN_SYSTEM_AVAILABLE, reason="Plugin system not available")
    def test_plugin_manager_with_empty_state(self):
        """Test plugin manager with empty state"""
        manager = create_plugin_manager()
        
        # Test empty manager operations
        plugins = manager.list_plugins()
        assert len(plugins) == 0
        
        loaded_plugins = manager.list_loaded_plugins()
        assert len(loaded_plugins) == 0
        
        # Test cleanup empty manager
        manager.cleanup_all_plugins()
        assert len(manager.plugins) == 0
    
    @pytest.mark.skipif(not PERFORMANCE_MONITORING_AVAILABLE, reason="Performance monitoring not available")
    def test_performance_monitor_with_empty_state(self, forest):
        """Test performance monitor with empty state"""
        monitor = create_performance_monitor(forest)
        
        # Test empty monitor report
        report = monitor.get_forest_performance_report()
        assert "forest_metrics" in report
        
        forest_metrics = report["forest_metrics"]
        assert forest_metrics["total_executions"] == 0
        assert forest_metrics["successful_executions"] == 0
        assert forest_metrics["failed_executions"] == 0
        
        # Test empty monitor summary
        summary = monitor.get_performance_summary()
        assert "No performance data available" in summary or "TestForest" in summary 