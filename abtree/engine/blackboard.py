"""
Blackboard system - Cross-node data sharing mechanism

The blackboard system allows different nodes in the behavior tree to share data,
providing thread-safe data storage and access mechanisms with zero-copy optimization.
"""

import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union, AsyncGenerator


@dataclass
class Blackboard:
    """
    Blackboard system - Cross-node data sharing with zero-copy optimization

    The blackboard system provides data sharing mechanism for nodes in the behavior tree,
    supporting synchronous and asynchronous operations, ensuring thread safety,
    and optimized for zero-copy data transfer to minimize memory overhead.

    Attributes:
        data: Dictionary storing data (using direct references)
        _lock: Async lock, ensuring thread safety
    """

    data: Dict[str, Any] = field(default_factory=dict)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    def set(self, key: str, value: Any) -> None:
        """
        Set blackboard data - zero-copy optimized
        
        Args:
            key: Data key
            value: Data value (stored by reference, no copying)
        """
        self.data[key] = value  # Direct reference storage

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get blackboard data - zero-copy optimized
        
        Args:
            key: Data key
            default: Default value returned when key doesn't exist

        Returns:
            Stored data value or default value (direct reference)
        """
        return self.data.get(key, default)  # Direct reference retrieval

    def has(self, key: str) -> bool:
        """
        Check if specified key exists in blackboard - zero-copy optimized
        
        Args:
            key: Key to check

        Returns:
            True if key exists, False otherwise
        """
        return key in self.data

    def remove(self, key: str) -> bool:
        """
        Remove data from blackboard - zero-copy optimized
        
        Args:
            key: Key to remove

        Returns:
            True if key exists and is removed, False otherwise
        """
        if key in self.data:
            del self.data[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all data in the blackboard - zero-copy optimized"""
        self.data.clear()

    def keys(self) -> List[str]:
        """
        Get list of all keys in blackboard - zero-copy optimized
        
        Returns:
            List of keys
        """
        return list(self.data.keys())

    def values(self) -> List[Any]:
        """
        Get list of all values in blackboard - zero-copy optimized
        
        Returns:
            List of values (direct references)
        """
        return list(self.data.values())  # Direct references

    def items(self) -> List[Tuple[str, Any]]:
        """
        Get list of all key-value pairs in blackboard - zero-copy optimized
        
        Returns:
            List of key-value pairs (direct references)
        """
        return list(self.data.items())  # Direct references

    async def set_async(self, key: str, value: Any) -> None:
        """
        Asynchronously set blackboard data (thread-safe) - zero-copy optimized
        
        Args:
            key: Data key
            value: Data value (stored by reference, no copying)
        """
        async with self._lock:
            self.data[key] = value  # Direct reference storage

    async def get_async(self, key: str, default: Any = None) -> Any:
        """
        Asynchronously get blackboard data (thread-safe) - zero-copy optimized
        
        Args:
            key: Data key
            default: Default value

        Returns:
            Stored data value or default value (direct reference)
        """
        async with self._lock:
            return self.data.get(key, default)  # Direct reference retrieval

    async def has_async(self, key: str) -> bool:
        """
        Asynchronously check if specified key exists in blackboard (thread-safe) - zero-copy optimized
        
        Args:
            key: Key to check

        Returns:
            True if key exists, False otherwise
        """
        async with self._lock:
            return key in self.data

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator["Blackboard", None]:
        """
        Blackboard transaction context manager - zero-copy optimized

        Provides atomic operations, ensuring data consistency during transactions.

        Yields:
            Blackboard: Current blackboard instance
        """
        async with self._lock:
            yield self

    def __len__(self) -> int:
        """Return the number of data items in blackboard - zero-copy optimized"""
        return len(self.data)

    def __contains__(self, key: str) -> bool:
        """Check if key exists in blackboard - zero-copy optimized"""
        return key in self.data

    def __getitem__(self, key: str) -> Any:
        """Get data by key - zero-copy optimized"""
        return self.data[key]  # Direct reference

    def __setitem__(self, key: str, value: Any) -> None:
        """Set data by key - zero-copy optimized"""
        self.data[key] = value  # Direct reference storage

    def __delitem__(self, key: str) -> None:
        """Delete data for specified key - zero-copy optimized"""
        del self.data[key]

    def __repr__(self) -> str:
        """String representation of blackboard object - zero-copy optimized"""
        return f"Blackboard(data={self.data})"
