"""
Event system - Event listening and context awareness

The event system provides an event-driven communication mechanism for behavior trees,
supporting event publication and subscription between nodes.
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
    Event object

    Attributes:
        name: Event name
        data: Event data
        source: Event source
        timestamp: Event timestamp
        priority: Event priority
    """

    name: str
    data: Any = None
    source: Optional[str] = None
    timestamp: float = field(default_factory=lambda: asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else 0.0)
    priority: EventPriority = EventPriority.NORMAL

    def __repr__(self) -> str:
        return f"Event(name='{self.name}', data={self.data}, source='{self.source}')"


@dataclass
class EventListener:
    """
    Event listener

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
        Execute event callback

        Args:
            event: Event object

        Returns:
            Return value of the callback function
        """
        if self.event_filter and not self.event_filter(event):
            return None

        if asyncio.iscoroutinefunction(self.callback):
            return await self.callback(event)
        else:
            return self.callback(event)


class EventSystem:
    """
    Event system

    Provides event publication, subscription, and management functionality,
    supporting asynchronous event handling and priority sorting.
    """

    def __init__(self):
        """Initialize event system"""
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
        Publish event

        Args:
            event: Event object or event name
            data: Event data
            source: Event source
            priority: Event priority
        """
        if isinstance(event, str):
            event = Event(name=event, data=data, source=source, priority=priority)

        async with self._lock:
            # Add to history
            self._event_history.append(event)
            if len(self._event_history) > self._max_history_size:
                self._event_history.pop(0)

            # Get event listeners
            listeners = self._listeners.get(event.name, [])
            all_listeners = listeners + self._global_listeners

            # Sort by priority
            all_listeners.sort(key=lambda l: l.priority.value, reverse=True)

        # Asynchronously execute listeners
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
        Subscribe to specific event

        Args:
            event_name: Event name
            callback: Callback function
            priority: Priority
            event_filter: Event filter
        """
        listener = EventListener(
            callback=callback, priority=priority, event_filter=event_filter
        )

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
        Subscribe to all events

        Args:
            callback: Callback function
            priority: Priority
            event_filter: Event filter
        """
        listener = EventListener(
            callback=callback, priority=priority, event_filter=event_filter
        )
        self._global_listeners.append(listener)

    def off(self, event_name: str, callback: Callable[[Event], Any]) -> bool:
        """
        Unsubscribe from specific event

        Args:
            event_name: Event name
            callback: Callback function

        Returns:
            True if listener is found and removed, False otherwise
        """
        if event_name not in self._listeners:
            return False

        listeners = self._listeners[event_name]
        for i, listener in enumerate(listeners):
            if listener.callback == callback:
                listeners.pop(i)
                return True

        return False

    def off_any(self, callback: Callable[[Event], Any]) -> bool:
        """
        Unsubscribe from all events

        Args:
            callback: Callback function

        Returns:
            True if listener is found and removed, False otherwise
        """
        for i, listener in enumerate(self._global_listeners):
            if listener.callback == callback:
                self._global_listeners.pop(i)
                return True

        return False

    def clear(self, event_name: Optional[str] = None) -> None:
        """
        Clear event listeners

        Args:
            event_name: Event name, if None then clear all events
        """
        if event_name is None:
            self._listeners.clear()
            self._global_listeners.clear()
        elif event_name in self._listeners:
            del self._listeners[event_name]

    def get_listeners(self, event_name: Optional[str] = None) -> List[EventListener]:
        """
        Get event listener list

        Args:
            event_name: Event name, if None then return all listeners

        Returns:
            Listener list
        """
        if event_name is None:
            all_listeners = []
            for listeners in self._listeners.values():
                all_listeners.extend(listeners)
            all_listeners.extend(self._global_listeners)
            return all_listeners
        else:
            return self._listeners.get(event_name, [])

    def get_event_history(
        self, event_name: Optional[str] = None, limit: Optional[int] = None
    ) -> List[Event]:
        """
        Get event history

        Args:
            event_name: Event name, if None then return all events
            limit: Limit the number of events returned

        Returns:
            Event history list
        """
        if event_name is None:
            history = self._event_history
        else:
            history = [
                event for event in self._event_history if event.name == event_name
            ]

        if limit is not None:
            history = history[-limit:]

        return history

    def set_max_history_size(self, size: int) -> None:
        """
        Set maximum history size

        Args:
            size: Maximum history size
        """
        self._max_history_size = size
        while len(self._event_history) > self._max_history_size:
            self._event_history.pop(0)

    def clear_history(self) -> None:
        """Clear event history"""
        self._event_history.clear()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get event system statistics

        Returns:
            Statistics dictionary
        """
        total_listeners = sum(len(listeners) for listeners in self._listeners.values())
        total_listeners += len(self._global_listeners)

        return {
            "total_events": len(self._event_history),
            "total_listeners": total_listeners,
            "event_types": list(self._listeners.keys()),
            "global_listeners": len(self._global_listeners),
            "max_history_size": self._max_history_size,
        }

    def __repr__(self) -> str:
        """String representation of the event system"""
        stats = self.get_stats()
        return f"EventSystem(events={stats['total_events']}, listeners={stats['total_listeners']})"
