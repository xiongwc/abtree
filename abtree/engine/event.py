"""
Event dispatcher - Event listening and context awareness

The event dispatcher provides an event-driven communication mechanism for behavior trees,
supporting event publication and subscription between nodes with asyncio.Event().
Focused on triggering mechanism between behavior trees without data transfer.
"""

import asyncio
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass


@dataclass
class EventInfo:
    """
    Event information for tracking and management
    
    Attributes:
        name: Event name
        source: Event source
        timestamp: Event timestamp
        trigger_count: Number of times this event has been triggered
        data: Event data (optional)
    """
    
    name: str
    source: Optional[str] = None
    timestamp: float = 0.0
    trigger_count: int = 0
    data: Optional[Any] = None


class EventDispatcher:
    """
    Event dispatcher - based on asyncio.Event() for behavior tree communication
    
    Provides event publication, subscription, and management functionality,
    supporting asynchronous event handling with asyncio.Event() for triggering
    between behavior trees without data transfer.
    """

    def __init__(self) -> None:
        """Initialize event dispatcher with asyncio.Event()"""
        self._events: Dict[str, asyncio.Event] = {}
        self._event_info: Dict[str, EventInfo] = {}
        self._global_listeners: List[asyncio.Event] = []
        self._lock = asyncio.Lock()
        self._loop = asyncio.get_event_loop()

    async def emit(self, event_name: str, source: Optional[str] = None, data: Optional[Any] = None) -> None:
        """
        Emit an event - trigger all listeners
        
        Args:
            event_name: Event name to emit
            source: Event source (optional)
            data: Event data (optional)
        """
        async with self._lock:
            # Create event if it doesn't exist
            if event_name not in self._events:
                self._events[event_name] = asyncio.Event()
                self._event_info[event_name] = EventInfo(
                    name=event_name,
                    source=source,
                    timestamp=self._loop.time(),
                    trigger_count=0,
                    data=data
                )
            
            # Update event info
            event_info = self._event_info[event_name]
            event_info.source = source
            event_info.timestamp = self._loop.time()
            event_info.trigger_count += 1
            event_info.data = data
            
            # Set the event to trigger all listeners
            self._events[event_name].set()
            
            # Also trigger global listeners
            for global_event in self._global_listeners:
                global_event.set()
            
            # Trigger middleware publish if this is a topic event
            if event_name.startswith("topic_"):
                topic = event_name[6:]  # Remove "topic_" prefix
                # Try to find middleware through blackboard
                try:
                    # This is a bit of a hack, but we need to access the middleware
                    # We'll let the forest handle this through its own mechanism
                    pass
                except Exception:
                    pass

    async def wait_for(self, event_name: str, timeout: Optional[float] = None) -> bool:
        """
        Wait for an event to be triggered
        
        Args:
            event_name: Event name to wait for
            timeout: Timeout in seconds (None for no timeout)
            
        Returns:
            True if event was triggered, False if timeout occurred
        """
        if event_name not in self._events:
            self._events[event_name] = asyncio.Event()
            self._event_info[event_name] = EventInfo(
                name=event_name,
                trigger_count=0
            )
        
        try:
            await asyncio.wait_for(self._events[event_name].wait(), timeout=timeout)
            # Automatically clear the event to avoid repeated triggers
            self._events[event_name].clear()
            return True
        except asyncio.TimeoutError:
            return False

    async def wait_for_any(self, event_names: List[str], timeout: Optional[float] = None) -> Optional[str]:
        """
        Wait for any of the specified events to be triggered
        
        Args:
            event_names: List of event names to wait for
            timeout: Timeout in seconds (None for no timeout)
            
        Returns:
            Name of the triggered event, or None if timeout occurred
        """
        # Ensure all events exist
        for event_name in event_names:
            if event_name not in self._events:
                self._events[event_name] = asyncio.Event()
                self._event_info[event_name] = EventInfo(
                    name=event_name,
                    trigger_count=0
                )
        
        # Create tasks for all events
        tasks = [asyncio.create_task(self._events[event_name].wait()) for event_name in event_names]
        
        try:
            # Wait for the first event to complete
            done, pending = await asyncio.wait(
                tasks, 
                timeout=timeout, 
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel remaining tasks
            for task in pending:
                task.cancel()
            
            # Find which event was triggered
            for event_name, task in zip(event_names, tasks):
                if task in done:
                    return event_name
            
            return None
        except asyncio.TimeoutError:
            return None

    async def wait_for_all(self, event_names: List[str], timeout: Optional[float] = None) -> bool:
        """
        Wait for all specified events to be triggered
        
        Args:
            event_names: List of event names to wait for
            timeout: Timeout in seconds (None for no timeout)
            
        Returns:
            True if all events were triggered, False if timeout occurred
        """
        # Ensure all events exist
        for event_name in event_names:
            if event_name not in self._events:
                self._events[event_name] = asyncio.Event()
                self._event_info[event_name] = EventInfo(
                    name=event_name,
                    trigger_count=0
                )
        
        # Create tasks for all events
        tasks = [asyncio.create_task(self._events[event_name].wait()) for event_name in event_names]
        
        try:
            await asyncio.wait_for(asyncio.gather(*tasks), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            return False

    def create_global_listener(self) -> asyncio.Event:
        """
        Create a global listener that triggers on any event
        
        Returns:
            asyncio.Event that will be set when any event is emitted
        """
        global_event = asyncio.Event()
        self._global_listeners.append(global_event)
        return global_event

    def remove_global_listener(self, global_event: asyncio.Event) -> bool:
        """
        Remove a global listener
        
        Args:
            global_event: The global event to remove
            
        Returns:
            True if the event was found and removed
        """
        if global_event in self._global_listeners:
            self._global_listeners.remove(global_event)
            return True
        return False

    def clear_event(self, event_name: str) -> bool:
        """
        Clear an event (reset its state)
        
        Args:
            event_name: Event name to clear
            
        Returns:
            True if event was found and cleared
        """
        if event_name in self._events:
            self._events[event_name].clear()
            return True
        return False

    def clear_all_events(self) -> None:
        """Clear all events (reset their states)"""
        for event in self._events.values():
            event.clear()
        
        for global_event in self._global_listeners:
            global_event.clear()

    def remove_event(self, event_name: str) -> bool:
        """
        Remove an event completely
        
        Args:
            event_name: Event name to remove
            
        Returns:
            True if event was found and removed
        """
        if event_name in self._events:
            del self._events[event_name]
            if event_name in self._event_info:
                del self._event_info[event_name]
            return True
        return False

    def get_event_info(self, event_name: str) -> Optional[EventInfo]:
        """
        Get information about an event
        
        Args:
            event_name: Event name
            
        Returns:
            EventInfo object or None if event doesn't exist
        """
        return self._event_info.get(event_name)

    def get_all_event_names(self) -> List[str]:
        """
        Get all registered event names
        
        Returns:
            List of all event names
        """
        return list(self._events.keys())

    def is_event_set(self, event_name: str) -> bool:
        """
        Check if an event is currently set (triggered)
        
        Args:
            event_name: Event name to check
            
        Returns:
            True if event is set, False otherwise
        """
        if event_name in self._events:
            return self._events[event_name].is_set()
        return False

    def get_stats(self) -> Dict[str, Any]:
        """
        Get event dispatcher statistics
        
        Returns:
            Dictionary with event dispatcher statistics
        """
        total_triggers = sum(info.trigger_count for info in self._event_info.values())
        
        return {
            "total_events": len(self._events),
            "global_listeners": len(self._global_listeners),
            "total_triggers": total_triggers,
            "event_names": list(self._events.keys()),
        }

    def __repr__(self) -> str:
        """String representation"""
        return f"EventDispatcher(events={len(self._events)}, global_listeners={len(self._global_listeners)})"
