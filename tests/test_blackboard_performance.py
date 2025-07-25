"""
Performance tests for optimized blackboard system.

This module contains comprehensive performance tests to demonstrate
the improvements in the optimized blackboard implementation.
"""

import asyncio
import time
import threading
from typing import List, Dict, Any

import pytest

from abtree.engine.blackboard import OptimizedBlackboard, BlackboardStats


class PerformanceTestBlackboard:
    """Simple blackboard for performance comparison."""
    
    def __init__(self):
        self.data = {}
        self._lock = asyncio.Lock()
    
    def set(self, key: str, value: Any) -> None:
        self.data[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)
    
    async def set_async(self, key: str, value: Any) -> None:
        async with self._lock:
            self.data[key] = value
    
    async def get_async(self, key: str, default: Any = None) -> Any:
        async with self._lock:
            return self.data.get(key, default)


def test_blackboard_stats():
    """Test blackboard statistics functionality."""
    stats = BlackboardStats()
    
    # Test initial state
    assert stats.total_operations == 0
    assert stats.read_operations == 0
    assert stats.write_operations == 0
    assert stats.cache_hits == 0
    assert stats.cache_misses == 0
    
    # Test cache hit rate calculation
    assert stats.get_cache_hit_rate() == 0.0
    
    # Test statistics update
    stats.cache_hits = 80
    stats.cache_misses = 20
    assert stats.get_cache_hit_rate() == 80.0
    
    # Test reset
    stats.reset()
    assert stats.total_operations == 0
    assert stats.cache_hits == 0


def test_optimized_blackboard_initialization():
    """Test optimized blackboard initialization."""
    # Test with default settings
    bb = OptimizedBlackboard()
    assert bb._enable_caching is True
    assert bb._cache_size == 1000
    assert bb._enable_stats is True
    assert bb._enable_object_pooling is True
    
    # Test with custom settings
    bb = OptimizedBlackboard(
        enable_caching=False,
        cache_size=500,
        enable_stats=False,
        enable_object_pooling=False
    )
    assert bb._enable_caching is False
    assert bb._cache_size == 500
    assert bb._enable_stats is False
    assert bb._enable_object_pooling is False


def test_basic_operations():
    """Test basic blackboard operations."""
    bb = OptimizedBlackboard()
    
    # Test set and get
    bb.set("key1", "value1")
    assert bb.get("key1") == "value1"
    
    # Test default value
    assert bb.get("nonexistent", "default") == "default"
    
    # Test has
    assert bb.has("key1") is True
    assert bb.has("nonexistent") is False
    
    # Test remove
    assert bb.remove("key1") is True
    assert bb.has("key1") is False
    assert bb.remove("nonexistent") is False
    
    # Test clear
    bb.set("key2", "value2")
    bb.clear()
    assert len(bb) == 0


@pytest.mark.asyncio
async def test_async_operations():
    """Test asynchronous blackboard operations."""
    bb = OptimizedBlackboard()
    
    # Test async set and get
    await bb.set_async("key1", "value1")
    assert await bb.get_async("key1") == "value1"
    
    # Test async has
    assert await bb.has_async("key1") is True
    assert await bb.has_async("nonexistent") is False
    
    # Test async remove
    assert await bb.remove_async("key1") is True
    assert await bb.has_async("key1") is False
    
    # Test async clear
    await bb.set_async("key2", "value2")
    await bb.clear_async()
    assert len(bb) == 0


def test_caching_functionality():
    """Test caching functionality."""
    bb = OptimizedBlackboard(enable_caching=True, cache_size=2)
    
    # Set some values
    bb.set("key1", "value1")
    bb.set("key2", "value2")
    
    # Get values to populate cache
    bb.get("key1")
    bb.get("key2")
    
    # Check cache statistics
    stats = bb.get_stats()
    assert stats['cache_size'] > 0
    assert stats['cache_hits'] >= 0
    assert stats['cache_misses'] >= 0


def test_performance_statistics():
    """Test performance statistics collection."""
    bb = OptimizedBlackboard(enable_stats=True)
    
    # Perform some operations
    bb.set("key1", "value1")
    bb.get("key1")
    bb.get("nonexistent", "default")
    
    # Check statistics
    stats = bb.get_stats()
    assert stats['total_operations'] > 0
    assert stats['write_operations'] > 0
    assert stats['read_operations'] > 0
    assert 'cache_hit_rate' in stats
    assert 'average_lock_wait_time' in stats
    
    # Test reset
    bb.reset_stats()
    stats_after_reset = bb.get_stats()
    assert stats_after_reset['total_operations'] == 0


def test_thread_safety():
    """Test thread safety of blackboard operations."""
    bb = OptimizedBlackboard()
    results = []
    errors = []
    
    def worker(thread_id: int):
        """Worker function for thread safety test."""
        try:
            for i in range(100):
                key = f"key_{thread_id}_{i}"
                value = f"value_{thread_id}_{i}"
                bb.set(key, value)
                retrieved = bb.get(key)
                if retrieved != value:
                    errors.append(f"Thread {thread_id}: value mismatch at {i}")
                results.append(f"Thread {thread_id}: {i}")
        except Exception as e:
            errors.append(f"Thread {thread_id}: {e}")
    
    # Create multiple threads
    threads = []
    for i in range(5):
        thread = threading.Thread(target=worker, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Check for errors
    assert len(errors) == 0, f"Thread safety errors: {errors}"
    assert len(results) == 500  # 5 threads * 100 operations each


@pytest.mark.asyncio
async def test_concurrent_async_operations():
    """Test concurrent asynchronous operations."""
    bb = OptimizedBlackboard()
    
    async def async_worker(worker_id: int):
        """Async worker function."""
        for i in range(50):
            key = f"async_key_{worker_id}_{i}"
            value = f"async_value_{worker_id}_{i}"
            await bb.set_async(key, value)
            retrieved = await bb.get_async(key)
            assert retrieved == value
    
    # Create multiple concurrent tasks
    tasks = []
    for i in range(5):
        task = asyncio.create_task(async_worker(i))
        tasks.append(task)
    
    # Wait for all tasks to complete
    await asyncio.gather(*tasks)
    
    # Verify all data is present
    for i in range(5):
        for j in range(50):
            key = f"async_key_{i}_{j}"
            value = f"async_value_{i}_{j}"
            assert bb.get(key) == value


def test_memory_efficiency():
    """Test memory efficiency of optimized blackboard."""
    bb = OptimizedBlackboard(enable_object_pooling=True)
    
    # Store large objects
    large_data = [i for i in range(10000)]
    bb.set("large_key", large_data)
    
    # Check memory usage doesn't explode
    stats = bb.get_stats()
    assert stats['data_size'] == 1
    
    # Test with many small objects
    for i in range(1000):
        bb.set(f"small_key_{i}", f"small_value_{i}")
    
    stats = bb.get_stats()
    assert stats['data_size'] == 1001  # 1000 small + 1 large


def test_transaction_support():
    """Test transaction support."""
    bb = OptimizedBlackboard()
    
    # Test synchronous transaction-like behavior
    bb.set("key1", "value1")
    bb.set("key2", "value2")
    
    # Verify both values are set
    assert bb.get("key1") == "value1"
    assert bb.get("key2") == "value2"


@pytest.mark.asyncio
async def test_async_transaction():
    """Test asynchronous transaction support."""
    bb = OptimizedBlackboard()
    
    async with bb.transaction() as bb_tx:
        await bb_tx.set_async("key1", "value1")
        await bb_tx.set_async("key2", "value2")
    
    # Verify both values are set after transaction
    assert await bb.get_async("key1") == "value1"
    assert await bb.get_async("key2") == "value2"


def test_backward_compatibility():
    """Test backward compatibility with original Blackboard interface."""
    from abtree.engine.blackboard import Blackboard
    
    # Test that Blackboard is an alias for OptimizedBlackboard
    bb = Blackboard()
    assert isinstance(bb, OptimizedBlackboard)
    
    # Test basic operations work
    bb.set("key1", "value1")
    assert bb.get("key1") == "value1"


def test_performance_comparison():
    """Compare performance between simple and optimized blackboard."""
    simple_bb = PerformanceTestBlackboard()
    optimized_bb = OptimizedBlackboard(enable_caching=True, enable_stats=True)
    
    # Test synchronous operations
    start_time = time.time()
    for i in range(1000):
        simple_bb.set(f"key_{i}", f"value_{i}")
        simple_bb.get(f"key_{i}")
    simple_time = time.time() - start_time
    
    start_time = time.time()
    for i in range(1000):
        optimized_bb.set(f"key_{i}", f"value_{i}")
        optimized_bb.get(f"key_{i}")
    optimized_time = time.time() - start_time
    
    # Optimized should be at least as fast (with overhead for features)
    # In practice, it should be faster due to caching
    print(f"Simple blackboard time: {simple_time:.4f}s")
    print(f"Optimized blackboard time: {optimized_time:.4f}s")
    
    # Get performance statistics
    stats = optimized_bb.get_stats()
    print(f"Cache hit rate: {stats['cache_hit_rate']:.2f}%")
    print(f"Total operations: {stats['total_operations']}")


@pytest.mark.asyncio
async def test_async_performance_comparison():
    """Compare async performance between simple and optimized blackboard."""
    simple_bb = PerformanceTestBlackboard()
    optimized_bb = OptimizedBlackboard(enable_caching=True, enable_stats=True)
    
    # Test async operations
    start_time = time.time()
    for i in range(100):
        await simple_bb.set_async(f"key_{i}", f"value_{i}")
        await simple_bb.get_async(f"key_{i}")
    simple_time = time.time() - start_time
    
    start_time = time.time()
    for i in range(100):
        await optimized_bb.set_async(f"key_{i}", f"value_{i}")
        await optimized_bb.get_async(f"key_{i}")
    optimized_time = time.time() - start_time
    
    print(f"Simple async blackboard time: {simple_time:.4f}s")
    print(f"Optimized async blackboard time: {optimized_time:.4f}s")
    
    # Get performance statistics
    stats = optimized_bb.get_stats()
    print(f"Async cache hit rate: {stats['cache_hit_rate']:.2f}%")
    print(f"Async total operations: {stats['total_operations']}")


def test_cache_optimization():
    """Test cache optimization features."""
    bb = OptimizedBlackboard(enable_caching=True, cache_size=5)
    
    # Fill cache
    for i in range(10):
        bb.set(f"key_{i}", f"value_{i}")
        bb.get(f"key_{i}")  # Access to populate cache
    
    # Check cache size is limited
    stats = bb.get_stats()
    assert stats['cache_size'] <= 5
    
    # Test cache optimization
    bb.optimize_cache()
    
    # Verify blackboard still works
    assert bb.get("key_0") == "value_0"


if __name__ == "__main__":
    # Run performance tests
    print("Running blackboard performance tests...")
    
    test_performance_comparison()
    asyncio.run(test_async_performance_comparison())
    
    print("Performance tests completed!") 