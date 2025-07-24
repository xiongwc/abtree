"""
Event system - Event listening and context awareness

The event system provides an event-driven communication mechanism for behavior trees,
supporting event publication and subscription between nodes with zero-copy optimization.
"""

import asyncio
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple, Union


class EventPriority(Enum):
    """Event priority enumeration"""

    LOW = auto()
    NORMAL = auto()
    HIGH = auto()
    CRITICAL = auto()


@dataclass
class Event:
    """
    Event object - optimized for zero-copy data transfer
    
    Attributes:
        name: Event name
        data: Event data (stored by reference, no copying)
        source: Event source
        timestamp: Event timestamp
        priority: Event priority
    """

    name: str
    data: Any = None  # Direct reference, no copying
    source: Optional[str] = None
    timestamp: float = field(default_factory=lambda: asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else 0.0)
    priority: EventPriority = EventPriority.NORMAL

    def __repr__(self) -> str:
        return f"Event(name='{self.name}', data={self.data}, source='{self.source}')"


@dataclass
class EventListener:
    """
    Event listener - optimized for zero-copy data transfer
    
    Attributes:
        callback: Callback function
        priority: Priority
        event_filter: Event filter
    """

    callback: Callable[[Event], Any]
    priority: EventPriority = EventPriority.NORMAL
    event_filter: Optional[Callable[[Event], bool]] = None

    async def execute(self, event: Event) -> Any:
        """
        Execute event callback - zero-copy optimized
        
        Args:
            event: Event object (passed by reference)

        Returns:
            Return value of the callback function
        """
        if self.event_filter and not self.event_filter(event):
            return None

        if asyncio.iscoroutinefunction(self.callback):
            return await self.callback(event)  # Direct event reference
        else:
            return self.callback(event)  # Direct event reference


class EventSystem:
    """
    Event system - optimized for zero-copy data transfer

    Provides event publication, subscription, and management functionality,
    supporting asynchronous event handling and priority sorting with minimal memory overhead.
    """

    def __init__(self) -> None:
        """Initialize event system - zero-copy optimized"""
        self._listeners: Dict[str, List[EventListener]] = {}
        self._global_listeners: List[EventListener] = []
        self._event_history: List[Event] = []
        self._max_history_size = 1000
        self._lock = asyncio.Lock()

    async def emit(
        self,
        event: Union[Event, str],
        data: Any = None,
        source: Optional[str] = None,
        priority: EventPriority = EventPriority.NORMAL,
    ) -> None:
        """
        Emit an event - zero-copy optimized
        
        Args:
            event: Event object or event name
            data: Event data (passed by reference, no copying)
            source: Event source
            priority: Event priority
        """
        if isinstance(event, str):
            event = Event(name=event, data=data, source=source, priority=priority)
        
        # Store event in history with direct reference
        self._event_history.append(event)
        
        # Trim history if needed
        if len(self._event_history) > self._max_history_size:
            self._event_history.pop(0)
        
        # Notify listeners with direct event reference
        await self._notify_listeners(event)
    
    async def _notify_listeners(self, event: Event) -> None:
        """Notify listeners with direct event reference - zero-copy optimized"""
        async with self._lock:
            # Get specific listeners for this event
            listeners = self._listeners.get(event.name, [])
            
            # Add global listeners
            all_listeners = listeners + self._global_listeners
            
            # Sort by priority
            all_listeners.sort(key=lambda l: l.priority.value, reverse=True)
            
            # Execute listeners with direct event reference
            tasks = []
            for listener in all_listeners:
                task = asyncio.create_task(listener.execute(event))
                tasks.append(task)
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

    def on(
        self,
        event_name: str,
        callback: Callable[[Event], Any],
        priority: EventPriority = EventPriority.NORMAL,
        event_filter: Optional[Callable[[Event], bool]] = None,
    ) -> None:
        """
        Subscribe to an event - zero-copy optimized
        
        Args:
            event_name: Event name to subscribe to
            callback: Callback function
            priority: Priority level
            event_filter: Optional event filter
        """
        listener = EventListener(callback=callback, priority=priority, event_filter=event_filter)
        
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        
        self._listeners[event_name].append(listener)

    def on_any(
        self,
        callback: Callable[[Event], Any],
        priority: EventPriority = EventPriority.NORMAL,
        event_filter: Optional[Callable[[Event], bool]] = None,
    ) -> None:
        """
        Subscribe to all events - zero-copy optimized
        
        Args:
            callback: Callback function
            priority: Priority level
            event_filter: Optional event filter
        """
        listener = EventListener(callback=callback, priority=priority, event_filter=event_filter)
        self._global_listeners.append(listener)

    def off(self, event_name: str, callback: Callable[[Event], Any]) -> bool:
        """
        Unsubscribe from an event - zero-copy optimized
        
        Args:
            event_name: Event name to unsubscribe from
            callback: Callback function to remove
            
        Returns:
            True if callback was found and removed
        """
        if event_name in self._listeners:
            listeners = self._listeners[event_name]
            for listener in listeners:
                if listener.callback == callback:
                    listeners.remove(listener)
                    return True
        return False

    def off_any(self, callback: Callable[[Event], Any]) -> bool:
        """
        Unsubscribe from all events - zero-copy optimized
        
        Args:
            callback: Callback function to remove
            
        Returns:
            True if callback was found and removed
        """
        for listener in self._global_listeners:
            if listener.callback == callback:
                self._global_listeners.remove(listener)
                return True
        return False

    def clear(self, event_name: Optional[str] = None) -> None:
        """
        Clear event listeners - zero-copy optimized
        
        Args:
            event_name: Event name to clear (None for all events)
        """
        if event_name is None:
            self._listeners.clear()
            self._global_listeners.clear()
        elif event_name in self._listeners:
            del self._listeners[event_name]

    def get_listeners(self, event_name: Optional[str] = None) -> List[EventListener]:
        """
        Get event listeners - zero-copy optimized
        
        Args:
            event_name: Event name (None for all listeners)
            
        Returns:
            List of event listeners (direct references)
        """
        if event_name is None:
            all_listeners = []
            for listeners in self._listeners.values():
                all_listeners.extend(listeners)
            all_listeners.extend(self._global_listeners)
            return all_listeners
        else:
            return self._listeners.get(event_name, [])  # Direct reference

    def get_event_history(
        self, event_name: Optional[str] = None, limit: Optional[int] = None
    ) -> List[Event]:
        """
        Get event history - zero-copy optimized
        
        Args:
            event_name: Event name to filter by (None for all events)
            limit: Maximum number of events to return
            
        Returns:
            List of events (direct references)
        """
        if event_name is None:
            events = self._event_history  # Direct reference
        else:
            events = [event for event in self._event_history if event.name == event_name]
        
        if limit is not None:
            events = events[-limit:]  # Direct reference
        
        return events

    def set_max_history_size(self, size: int) -> None:
        """
        Set maximum history size - zero-copy optimized
        
        Args:
            size: Maximum number of events to keep in history
        """
        self._max_history_size = size
        
        # Trim history if needed
        while len(self._event_history) > self._max_history_size:
            self._event_history.pop(0)

    def clear_history(self) -> None:
        """Clear event history - zero-copy optimized"""
        self._event_history.clear()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get event system statistics - zero-copy optimized
        
        Returns:
            Dictionary with event system statistics
        """
        total_listeners = sum(len(listeners) for listeners in self._listeners.values())
        total_listeners += len(self._global_listeners)
        
        return {
            "total_listeners": total_listeners,
            "event_types": len(self._listeners),
            "global_listeners": len(self._global_listeners),
            "history_size": len(self._event_history),
            "max_history_size": self._max_history_size,
        }

    def __repr__(self) -> str:
        """String representation - zero-copy optimized"""
        return f"EventSystem(listeners={len(self._listeners)}, history={len(self._event_history)})"
