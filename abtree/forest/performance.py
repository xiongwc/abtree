"""
Behavior Forest Performance Monitoring

This module provides comprehensive performance monitoring for behavior forests,
including execution time tracking, resource usage monitoring, and performance metrics.
"""

import asyncio
import logging
import time

from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from statistics import mean, median, stdev
from typing import Any, Callable, Dict, List, Optional

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
    timestamp: datetime = field(default_factory=datetime.now)


class PerformanceMonitor:
    """
    Performance monitor for behavior forests.
    
    Tracks execution times, success rates, and other
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
        # Collect basic resource usage (timestamp only)
        resource_usage = ResourceUsage(timestamp=datetime.now())
        self.resource_history.append(resource_usage)
        
        # Trim history if too long
        if len(self.resource_history) > self.max_history_size:
            self.resource_history.pop(0)
    
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
        report: Dict[str, Any] = {
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
        
        # Basic resource usage (timestamp only)
        if self.resource_history:
            latest = self.resource_history[-1]
            report['resource_usage'] = {
                'timestamp': latest.timestamp.isoformat()
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
        
        return summary


class PerformanceDecorator:
    """
    Decorator for measuring performance of forest operations.
    
    Can be used to automatically track execution times and success rates
    for forest operations.
    """
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator implementation."""
        async def wrapper(*args, **kwargs) -> Any:
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


def monitor_forest_performance(monitor: PerformanceMonitor) -> PerformanceDecorator:
    """Decorator for monitoring forest performance."""
    return PerformanceDecorator(monitor) 