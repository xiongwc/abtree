"""
Behavior Forest Performance Monitoring

This module provides comprehensive performance monitoring for behavior forests,
including execution time tracking, resource usage monitoring, and performance metrics.
"""

import asyncio
import time
import logging

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from statistics import mean, median, stdev

from .core import BehaviorForest, ForestNode, ForestNodeType


@dataclass
class PerformanceMetrics:
    """Performance metrics for a forest or node."""
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    total_execution_time: float = 0.0
    min_execution_time: float = float('inf')
    max_execution_time: float = 0.0
    average_execution_time: float = 0.0
    median_execution_time: float = 0.0
    execution_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    
    def update(self, execution_time: float, success: bool) -> None:
        """Update metrics with new execution data."""
        self.total_executions += 1
        self.total_execution_time += execution_time
        self.execution_times.append(execution_time)
        
        if success:
            self.successful_executions += 1
        else:
            self.failed_executions += 1
            
        # Update min/max
        self.min_execution_time = min(self.min_execution_time, execution_time)
        self.max_execution_time = max(self.max_execution_time, execution_time)
        
        # Update averages
        self.average_execution_time = self.total_execution_time / self.total_executions
        if self.execution_times:
            self.median_execution_time = median(self.execution_times)
    
    def get_success_rate(self) -> float:
        """Get the success rate as a percentage."""
        if self.total_executions == 0:
            return 0.0
        return (self.successful_executions / self.total_executions) * 100
    
    def get_throughput(self, time_window: float = 60.0) -> float:
        """Get executions per second over a time window."""
        if not self.execution_times:
            return 0.0
            
        now = time.time()
        recent_executions = sum(1 for t in self.execution_times 
                              if now - t <= time_window)
        return recent_executions / time_window


@dataclass
class ResourceUsage:
    """Resource usage metrics."""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_mb: float = 0.0
    disk_io_read: float = 0.0
    disk_io_write: float = 0.0
    network_io_sent: float = 0.0
    network_io_recv: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class PerformanceMonitor:
    """
    Performance monitor for behavior forests.
    
    Tracks execution times, success rates, resource usage, and other
    performance metrics for forests and individual nodes.
    """
    
    def __init__(self, forest: BehaviorForest):
        self.forest = forest
        self.logger = logging.getLogger(f"PerformanceMonitor.{forest.name}")
        
        # Metrics storage
        self.forest_metrics = PerformanceMetrics()
        self.node_metrics: Dict[str, PerformanceMetrics] = defaultdict(PerformanceMetrics)
        self.middleware_metrics: Dict[str, PerformanceMetrics] = defaultdict(PerformanceMetrics)
        
        # Resource monitoring
        self.resource_history: List[ResourceUsage] = []
        self.max_history_size = 1000
        
        # Monitoring state
        self.monitoring = False
        self.monitor_task: Optional[asyncio.Task] = None
        
        # Performance thresholds
        self.execution_time_threshold = 1.0  # seconds
        self.success_rate_threshold = 90.0   # percentage
        self.cpu_threshold = 80.0           # percentage
        self.memory_threshold = 80.0        # percentage
        
    async def start_monitoring(self, interval: float = 1.0) -> None:
        """Start performance monitoring."""
        if self.monitoring:
            self.logger.warning("Monitoring is already active")
            return
            
        self.monitoring = True
        self.monitor_task = asyncio.create_task(self._monitor_loop(interval))
        self.logger.info("Started performance monitoring")
        
    async def stop_monitoring(self) -> None:
        """Stop performance monitoring."""
        if not self.monitoring:
            return
            
        self.monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Stopped performance monitoring")
        
    async def _monitor_loop(self, interval: float) -> None:
        """Main monitoring loop."""
        while self.monitoring:
            try:
                await self._collect_metrics()
                await self._check_thresholds()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(interval)
    
    async def _collect_metrics(self) -> None:
        """Collect current performance metrics."""
        # Collect resource usage
        resource_usage = self._get_resource_usage()
        self.resource_history.append(resource_usage)
        
        # Trim history if too long
        if len(self.resource_history) > self.max_history_size:
            self.resource_history.pop(0)
    
    def _get_resource_usage(self) -> ResourceUsage:
        """Get current resource usage."""
        if not PSUTIL_AVAILABLE:
            # Return default values when psutil is not available
            return ResourceUsage(timestamp=datetime.now())
        
        try:
            process = psutil.Process()
            cpu_percent = process.cpu_percent()
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()
            
            # Get disk I/O
            disk_io = process.io_counters()
            
            # Get network I/O
            network_io = psutil.net_io_counters()
            
            return ResourceUsage(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_mb=memory_info.rss / 1024 / 1024,
                disk_io_read=disk_io.read_bytes / 1024 / 1024,
                disk_io_write=disk_io.write_bytes / 1024 / 1024,
                network_io_sent=network_io.bytes_sent / 1024 / 1024,
                network_io_recv=network_io.bytes_recv / 1024 / 1024,
                timestamp=datetime.now()
            )
        except Exception as e:
            self.logger.error(f"Error collecting resource usage: {e}")
            return ResourceUsage()
    
    async def _check_thresholds(self) -> None:
        """Check performance thresholds and log warnings."""
        # Check forest performance
        if self.forest_metrics.average_execution_time > self.execution_time_threshold:
            self.logger.warning(
                f"Forest execution time ({self.forest_metrics.average_execution_time:.3f}s) "
                f"exceeds threshold ({self.execution_time_threshold}s)"
            )
        
        if self.forest_metrics.get_success_rate() < self.success_rate_threshold:
            self.logger.warning(
                f"Forest success rate ({self.forest_metrics.get_success_rate():.1f}%) "
                f"below threshold ({self.success_rate_threshold}%)"
            )
        
        # Check resource usage
        if self.resource_history:
            latest = self.resource_history[-1]
            if latest.cpu_percent > self.cpu_threshold:
                self.logger.warning(
                    f"CPU usage ({latest.cpu_percent:.1f}%) "
                    f"exceeds threshold ({self.cpu_threshold}%)"
                )
            
            if latest.memory_percent > self.memory_threshold:
                self.logger.warning(
                    f"Memory usage ({latest.memory_percent:.1f}%) "
                    f"exceeds threshold ({self.memory_threshold}%)"
                )
    
    def record_forest_execution(self, execution_time: float, success: bool) -> None:
        """Record forest execution metrics."""
        self.forest_metrics.update(execution_time, success)
    
    def record_node_execution(self, node_name: str, execution_time: float, success: bool) -> None:
        """Record node execution metrics."""
        self.node_metrics[node_name].update(execution_time, success)
    
    def record_middleware_execution(self, middleware_name: str, execution_time: float, success: bool) -> None:
        """Record middleware execution metrics."""
        self.middleware_metrics[middleware_name].update(execution_time, success)
    
    def get_forest_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive forest performance report."""
        report = {
            'forest_name': self.forest.name,
            'timestamp': datetime.now().isoformat(),
            'forest_metrics': {
                'total_executions': self.forest_metrics.total_executions,
                'successful_executions': self.forest_metrics.successful_executions,
                'failed_executions': self.forest_metrics.failed_executions,
                'success_rate': self.forest_metrics.get_success_rate(),
                'average_execution_time': self.forest_metrics.average_execution_time,
                'median_execution_time': self.forest_metrics.median_execution_time,
                'min_execution_time': self.forest_metrics.min_execution_time,
                'max_execution_time': self.forest_metrics.max_execution_time,
                'throughput': self.forest_metrics.get_throughput()
            },
            'node_performance': {},
            'middleware_performance': {},
            'resource_usage': {}
        }
        
        # Node performance
        for node_name, metrics in self.node_metrics.items():
            report['node_performance'][node_name] = {
                'total_executions': metrics.total_executions,
                'success_rate': metrics.get_success_rate(),
                'average_execution_time': metrics.average_execution_time,
                'throughput': metrics.get_throughput()
            }
        
        # Middleware performance
        for mw_name, metrics in self.middleware_metrics.items():
            report['middleware_performance'][mw_name] = {
                'total_executions': metrics.total_executions,
                'success_rate': metrics.get_success_rate(),
                'average_execution_time': metrics.average_execution_time
            }
        
        # Resource usage
        if self.resource_history:
            latest = self.resource_history[-1]
            report['resource_usage'] = {
                'cpu_percent': latest.cpu_percent,
                'memory_percent': latest.memory_percent,
                'memory_mb': latest.memory_mb,
                'disk_io_read_mb': latest.disk_io_read,
                'disk_io_write_mb': latest.disk_io_write,
                'network_io_sent_mb': latest.network_io_sent,
                'network_io_recv_mb': latest.network_io_recv
            }
        
        return report
    
    def get_performance_summary(self) -> str:
        """Get a human-readable performance summary."""
        if not self.forest_metrics.total_executions:
            return "No performance data available"
        
        summary = f"""
Performance Summary for Forest '{self.forest.name}'
{'='*50}
Total Executions: {self.forest_metrics.total_executions}
Success Rate: {self.forest_metrics.get_success_rate():.1f}%
Average Execution Time: {self.forest_metrics.average_execution_time:.3f}s
Throughput: {self.forest_metrics.get_throughput():.2f} exec/s

Node Performance:
"""
        
        for node_name, metrics in self.node_metrics.items():
            if metrics.total_executions > 0:
                summary += f"  {node_name}: {metrics.get_success_rate():.1f}% success, "
                summary += f"{metrics.average_execution_time:.3f}s avg\n"
        
        if self.resource_history:
            latest = self.resource_history[-1]
            summary += f"""
Resource Usage:
  CPU: {latest.cpu_percent:.1f}%
  Memory: {latest.memory_percent:.1f}% ({latest.memory_mb:.1f} MB)
"""
        
        return summary


class PerformanceDecorator:
    """
    Decorator for measuring performance of forest operations.
    
    Can be used to automatically track execution times and success rates
    for forest operations.
    """
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
    
    def __call__(self, func: Callable):
        """Decorator implementation."""
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            
            try:
                result = await func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                raise e
            finally:
                execution_time = time.time() - start_time
                self.monitor.record_forest_execution(execution_time, success)
        
        return wrapper


def create_performance_monitor(forest: BehaviorForest) -> PerformanceMonitor:
    """Create a performance monitor for a forest."""
    return PerformanceMonitor(forest)


def monitor_forest_performance(monitor: PerformanceMonitor):
    """Decorator for monitoring forest performance."""
    return PerformanceDecorator(monitor) 