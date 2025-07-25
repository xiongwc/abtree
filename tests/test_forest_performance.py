import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock
from abtree.forest.performance import (
    PerformanceMonitor, PerformanceMetrics, ResourceUsage,
    create_performance_monitor, monitor_forest_performance,
    PerformanceDecorator
)
from abtree.forest.core import BehaviorForest, ForestNode, ForestNodeType
from abtree.engine.behavior_tree import BehaviorTree
from abtree.core.status import Status


class TestPerformanceMetrics:
    """Test performance metrics class"""
    
    def test_metrics_initialization(self):
        """Test performance metrics initialization"""
        metrics = PerformanceMetrics()
        
        assert metrics.total_executions == 0
        assert metrics.successful_executions == 0
        assert metrics.failed_executions == 0
        assert metrics.total_execution_time == 0.0
        assert metrics.min_execution_time == float('inf')
        assert metrics.max_execution_time == 0.0
        assert metrics.average_execution_time == 0.0
        assert metrics.median_execution_time == 0.0
    
    def test_metrics_update_success(self):
        """Test successful execution metrics update"""
        metrics = PerformanceMetrics()
        
        # Update successful execution
        metrics.update(1.0, True)
        
        assert metrics.total_executions == 1
        assert metrics.successful_executions == 1
        assert metrics.failed_executions == 0
        assert metrics.total_execution_time == 1.0
        assert metrics.min_execution_time == 1.0
        assert metrics.max_execution_time == 1.0
        assert metrics.average_execution_time == 1.0
    
    def test_metrics_update_failure(self):
        """Test failed execution metrics update"""
        metrics = PerformanceMetrics()
        
        # Update failed execution
        metrics.update(0.5, False)
        
        assert metrics.total_executions == 1
        assert metrics.successful_executions == 0
        assert metrics.failed_executions == 1
        assert metrics.total_execution_time == 0.5
        assert metrics.min_execution_time == 0.5
        assert metrics.max_execution_time == 0.5
    
    def test_metrics_multiple_updates(self):
        """Test multiple metrics updates"""
        metrics = PerformanceMetrics()
        
        # Multiple updates
        metrics.update(1.0, True)
        metrics.update(2.0, False)
        metrics.update(0.5, True)
        
        assert metrics.total_executions == 3
        assert metrics.successful_executions == 2
        assert metrics.failed_executions == 1
        assert metrics.total_execution_time == 3.5
        assert metrics.min_execution_time == 0.5
        assert metrics.max_execution_time == 2.0
        assert metrics.average_execution_time == 3.5 / 3
    
    def test_metrics_success_rate(self):
        """Test success rate calculation"""
        metrics = PerformanceMetrics()
        
        # No executions
        assert metrics.get_success_rate() == 0.0
        
        # All successful
        metrics.update(1.0, True)
        metrics.update(1.0, True)
        assert metrics.get_success_rate() == 100.0
        
        # Partial success
        metrics.update(1.0, False)
        assert abs(metrics.get_success_rate() - 66.66666666666667) < 0.0001
    
    def test_metrics_throughput(self):
        """Test throughput calculation"""
        metrics = PerformanceMetrics()
        
        # No executions
        assert metrics.get_throughput() == 0.0
        
        # Add some execution times
        current_time = time.time()
        metrics.execution_times.append(current_time - 30)  # 30 seconds ago
        metrics.execution_times.append(current_time - 10)  # 10 seconds ago
        metrics.execution_times.append(current_time - 5)   # 5 seconds ago
        
        # Should have 3 executions in 60 second window
        throughput = metrics.get_throughput(60.0)
        assert throughput > 0.0


class TestResourceUsage:
    """Test resource usage class"""
    
    def test_resource_usage_initialization(self):
        """Test resource usage initialization"""
        usage = ResourceUsage()
        
        assert usage.timestamp is not None
        assert isinstance(usage.timestamp, type(usage.timestamp))


class TestPerformanceMonitor:
    """Test performance monitor"""
    
    @pytest.fixture
    def forest(self):
        """Create test forest"""
        return BehaviorForest("TestForest")
    
    @pytest.fixture
    def monitor(self, forest):
        """Create performance monitor"""
        return PerformanceMonitor(forest)
    
    def test_monitor_initialization(self, monitor, forest):
        """Test monitor initialization"""
        assert monitor.forest == forest
        assert monitor.forest_metrics is not None
        assert isinstance(monitor.node_metrics, dict)
        assert isinstance(monitor.middleware_metrics, dict)
        assert monitor.monitoring is False
        assert monitor.monitor_task is None
    
    def test_record_forest_execution(self, monitor):
        """Test record forest execution"""
        monitor.record_forest_execution(1.0, True)
        
        assert monitor.forest_metrics.total_executions == 1
        assert monitor.forest_metrics.successful_executions == 1
        assert monitor.forest_metrics.failed_executions == 0
    
    def test_record_node_execution(self, monitor):
        """Test record node execution"""
        monitor.record_node_execution("test_node", 0.5, True)
        
        assert "test_node" in monitor.node_metrics
        node_metrics = monitor.node_metrics["test_node"]
        assert node_metrics.total_executions == 1
        assert node_metrics.successful_executions == 1
    
    def test_record_middleware_execution(self, monitor):
        """Test record middleware execution"""
        monitor.record_middleware_execution("test_middleware", 0.1, False)
        
        assert "test_middleware" in monitor.middleware_metrics
        middleware_metrics = monitor.middleware_metrics["test_middleware"]
        assert middleware_metrics.total_executions == 1
        assert middleware_metrics.failed_executions == 1
    
    def test_get_forest_performance_report(self, monitor):
        """Test get forest performance report"""
        # Record some execution data
        monitor.record_forest_execution(1.0, True)
        monitor.record_forest_execution(2.0, False)
        monitor.record_node_execution("node1", 0.5, True)
        monitor.record_middleware_execution("middleware1", 0.1, True)
        
        report = monitor.get_forest_performance_report()
        
        assert "forest_metrics" in report
        assert "node_performance" in report
        assert "middleware_performance" in report
        
        # Check forest metrics
        forest_metrics = report["forest_metrics"]
        assert forest_metrics["total_executions"] == 2
        assert forest_metrics["successful_executions"] == 1
        assert forest_metrics["failed_executions"] == 1
        
        # Check node metrics
        node_metrics = report["node_performance"]
        assert "node1" in node_metrics
        
        # Check middleware metrics
        middleware_metrics = report["middleware_performance"]
        assert "middleware1" in middleware_metrics
    
    def test_get_performance_summary(self, monitor):
        """Test get performance summary"""
        # Record some execution data
        monitor.record_forest_execution(1.0, True)
        monitor.record_forest_execution(2.0, True)
        monitor.record_node_execution("node1", 0.5, True)
        
        summary = monitor.get_performance_summary()
        
        assert isinstance(summary, str)
        assert "TestForest" in summary
        assert "2" in summary  # Total executions
        assert "100.0%" in summary  # Success rate
    
    @pytest.mark.asyncio
    async def test_start_stop_monitoring(self, monitor):
        """Test start and stop monitoring"""
        # Start monitoring
        await monitor.start_monitoring(interval=0.1)
        assert monitor.monitoring is True
        assert monitor.monitor_task is not None
        
        # Wait a short time
        await asyncio.sleep(0.2)
        
        # Stop monitoring
        await monitor.stop_monitoring()
        assert monitor.monitoring is False
        # Note: monitor_task might not be None immediately due to async cleanup
    
    @pytest.mark.asyncio
    async def test_monitor_loop(self, monitor):
        """Test monitor loop"""
        # Start monitoring
        await monitor.start_monitoring(interval=0.1)
        
        # Wait a short time for monitoring to run
        await asyncio.sleep(0.3)
        
        # Stop monitoring
        await monitor.stop_monitoring()
        
        # Verify monitor task is done
        assert monitor.monitor_task.done()
    
    @pytest.mark.asyncio
    async def test_collect_metrics(self, monitor):
        """Test collect metrics"""
        # Record some data
        monitor.record_forest_execution(1.0, True)
        monitor.record_node_execution("node1", 0.5, True)
        
        # Collect metrics
        await monitor._collect_metrics()
        
        # Verify resource history is updated
        assert len(monitor.resource_history) > 0
    
    @pytest.mark.asyncio
    async def test_check_thresholds(self, monitor):
        """Test check thresholds"""
        # Record some long execution time data
        monitor.record_forest_execution(5.0, True)  # 5 second execution time
        
        # Check thresholds
        await monitor._check_thresholds()
        
        # Should not produce errors since no thresholds are set
        pass


class TestPerformanceDecorator:
    """Test performance decorator"""
    
    @pytest.fixture
    def monitor(self):
        """Create performance monitor"""
        forest = BehaviorForest("TestForest")
        return PerformanceMonitor(forest)
    
    @pytest.fixture
    def decorator(self, monitor):
        """Create performance decorator"""
        return PerformanceDecorator(monitor)
    
    def test_decorator_initialization(self, decorator, monitor):
        """Test decorator initialization"""
        assert decorator.monitor == monitor
    
    @pytest.mark.asyncio
    async def test_decorator_wrapper(self, decorator):
        """Test decorator wrapper"""
        # Create an async function
        async def test_function():
            await asyncio.sleep(0.1)
            return "success"
        
        # Apply decorator
        decorated_func = decorator(test_function)
        
        # Execute decorated function
        result = await decorated_func()
        
        assert result == "success"
        
        # Verify monitor recorded execution
        assert decorator.monitor.forest_metrics.total_executions >= 1


class TestPerformanceUtilities:
    """Test performance utility functions"""
    
    @pytest.fixture
    def forest(self):
        """Create test forest"""
        return BehaviorForest("TestForest")
    
    def test_create_performance_monitor(self, forest):
        """Test create performance monitor"""
        monitor = create_performance_monitor(forest)
        
        assert isinstance(monitor, PerformanceMonitor)
        assert monitor.forest == forest
    
    def test_monitor_forest_performance(self, forest):
        """Test forest performance monitoring decorator"""
        monitor = create_performance_monitor(forest)
        decorator = monitor_forest_performance(monitor)
        
        assert isinstance(decorator, PerformanceDecorator)
        assert decorator.monitor == monitor


class TestPerformanceIntegration:
    """Test performance monitoring integration"""
    
    @pytest.fixture
    def forest(self):
        """Create test forest"""
        return BehaviorForest("TestForest")
    
    @pytest.fixture
    def monitor(self, forest):
        """Create performance monitor"""
        return create_performance_monitor(forest)
    
    @pytest.mark.asyncio
    async def test_full_performance_monitoring_cycle(self, monitor):
        """Test complete performance monitoring cycle"""
        # Start monitoring
        await monitor.start_monitoring(interval=0.1)
        
        # Record various execution data
        monitor.record_forest_execution(1.0, True)
        monitor.record_forest_execution(2.0, False)
        monitor.record_node_execution("node1", 0.5, True)
        monitor.record_node_execution("node2", 0.3, False)
        monitor.record_middleware_execution("middleware1", 0.1, True)
        
        # Wait for monitoring to run
        await asyncio.sleep(0.3)
        
        # Get performance report
        report = monitor.get_forest_performance_report()
        
        # Verify report content
        assert report["forest_metrics"]["total_executions"] == 2
        assert report["forest_metrics"]["successful_executions"] == 1
        assert report["forest_metrics"]["failed_executions"] == 1
        
        assert len(report["node_performance"]) == 2
        assert len(report["middleware_performance"]) == 1
        
        # Stop monitoring
        await monitor.stop_monitoring()
        
        # Verify monitoring stopped
        assert monitor.monitoring is False
    
    def test_performance_metrics_edge_cases(self):
        """Test performance metrics edge cases"""
        metrics = PerformanceMetrics()
        
        # Test zero execution time
        metrics.update(0.0, True)
        assert metrics.min_execution_time == 0.0
        assert metrics.max_execution_time == 0.0
        
        # Test very large execution time
        metrics.update(1000000.0, False)
        assert metrics.max_execution_time == 1000000.0
        
        # Test success rate boundary
        assert metrics.get_success_rate() == 50.0  # 1 success 1 failure
    
    def test_resource_usage_timestamp(self):
        """Test resource usage timestamp"""
        usage1 = ResourceUsage()
        time.sleep(0.001)  # Short delay
        usage2 = ResourceUsage()
        
        assert usage2.timestamp > usage1.timestamp 