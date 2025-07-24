"""
Communication Middleware - Unified Inter-Behavior Tree Communication

Provides 6 different communication patterns for behavior trees in the forest:
1. Pub/Sub (Publish-Subscribe) - Event-driven communication
2. Req/Resp (Request-Response) - Service call communication  
3. Shared Blackboard - Cross-tree data sharing
4. State Watching - State change monitoring
5. Behavior Call - Direct behavior tree calls
6. Task Board - Task distribution and claiming
"""

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set, Union

from ..core.status import Status
from ..engine.blackboard import Blackboard
from ..engine.event_system import Event, EventSystem
from .core import BehaviorForest, ForestNode


class CommunicationType(Enum):
    """Communication type enumeration"""
    PUB_SUB = auto()
    REQ_RESP = auto()
    SHARED_BLACKBOARD = auto()
    STATE_WATCHING = auto()
    BEHAVIOR_CALL = auto()
    TASK_BOARD = auto()


@dataclass
class Message:
    """Base message class for communication"""
    id: str
    source: str
    target: Optional[str] = None
    data: Any = None
    timestamp: float = field(default_factory=time.time)
    priority: int = 0


@dataclass
class Request(Message):
    """Request message for Req/Resp pattern"""
    method: str = ""
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Response(Message):
    """Response message for Req/Resp pattern"""
    request_id: str = ""
    success: bool = True
    error: Optional[str] = None


@dataclass
class Task:
    """Task for Task Board pattern"""
    id: str
    title: str
    description: str
    requirements: Set[str] = field(default_factory=set)
    priority: int = 0
    status: str = "pending"  # pending, claimed, completed, failed
    claimed_by: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    data: Dict[str, Any] = field(default_factory=dict)


class CommunicationMiddleware:
    """
    Unified Communication Middleware
    
    Provides all 6 communication patterns in a single middleware:
    - Pub/Sub: Event-driven communication
    - Req/Resp: Service call communication
    - Shared Blackboard: Cross-tree data sharing
    - State Watching: State change monitoring
    - Behavior Call: Direct behavior tree calls
    - Task Board: Task distribution and claiming
    """
    
    def __init__(self, name: str = "CommunicationMiddleware"):
        self.name = name
        self.forest: Optional[BehaviorForest] = None
        self.enabled = True
        
        # Pub/Sub components
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_history: List[Event] = []
        self.max_history = 1000
        
        # Req/Resp components
        self.services: Dict[str, Callable] = {}
        self.pending_requests: Dict[str, asyncio.Future] = {}
        self.request_counter = 0
        
        # Shared Blackboard components
        self.shared_blackboard = Blackboard()
        self.access_log: List[Dict[str, Any]] = []
        self.max_log_size = 1000
        
        # State Watching components
        self.watchers: Dict[str, List[Callable]] = {}
        self.state_cache: Dict[str, Any] = {}
        self.state_history: Dict[str, List[Dict[str, Any]]] = {}
        self.max_history_per_key = 100
        
        # Behavior Call components
        self.registered_behaviors: Dict[str, Callable] = {}
        self.call_log: List[Dict[str, Any]] = []
        
        # Task Board components
        self.tasks: Dict[str, Task] = {}
        self.task_counter = 0
        self.claim_callbacks: Dict[str, List[Callable]] = {}
    
    def initialize(self, forest: BehaviorForest) -> None:
        """Initialize middleware with forest"""
        self.forest = forest
    
    async def pre_tick(self) -> None:
        """Pre-tick processing"""
        pass
    
    async def post_tick(self, results: Dict[str, Status]) -> None:
        """Post-tick processing"""
        pass
    
    # ==================== Pub/Sub Methods ====================
    
    def subscribe(self, topic: str, callback: Callable) -> None:
        """
        Subscribe to a topic
        
        Args:
            topic: Topic to subscribe to
            callback: Callback function to execute when event is published
        """
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)
    
    def unsubscribe(self, topic: str, callback: Callable) -> bool:
        """
        Unsubscribe from a topic
        
        Args:
            topic: Topic to unsubscribe from
            callback: Callback function to remove
            
        Returns:
            True if callback was found and removed
        """
        if topic in self.subscribers and callback in self.subscribers[topic]:
            self.subscribers[topic].remove(callback)
            return True
        return False
    
    async def publish(self, topic: str, data: Any, source: str) -> None:
        """
        Publish an event to a topic
        
        Args:
            topic: Topic to publish to
            data: Event data
            source: Source node name
        """
        if not self.enabled:
            return
        
        event = Event(name=topic, data=data, source=source)
        self.event_history.append(event)
        
        # Trim history if needed
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
        
        # Execute callbacks
        if topic in self.subscribers:
            tasks = []
            for callback in self.subscribers[topic]:
                if asyncio.iscoroutinefunction(callback):
                    task = asyncio.create_task(callback(event))
                else:
                    task = asyncio.create_task(self._run_sync_callback(callback, event))
                tasks.append(task)
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _run_sync_callback(self, callback: Callable, event: Event) -> None:
        """Run synchronous callback in async context"""
        try:
            callback(event)
        except Exception as e:
            print(f"PubSub callback error: {e}")
    
    def get_subscribers(self, topic: str) -> List[Callable]:
        """Get subscribers for a topic"""
        return self.subscribers.get(topic, [])
    
    def get_event_history(self, topic: Optional[str] = None) -> List[Event]:
        """Get event history"""
        if topic is None:
            return self.event_history
        return [event for event in self.event_history if event.name == topic]
    
    # ==================== Req/Resp Methods ====================
    
    def register_service(self, service_name: str, handler: Callable) -> None:
        """
        Register a service
        
        Args:
            service_name: Name of the service
            handler: Handler function for the service
        """
        self.services[service_name] = handler
    
    def unregister_service(self, service_name: str) -> bool:
        """
        Unregister a service
        
        Args:
            service_name: Name of the service to unregister
            
        Returns:
            True if service was found and removed
        """
        if service_name in self.services:
            del self.services[service_name]
            return True
        return False
    
    async def request(self, service_name: str, params: Dict[str, Any], source: str) -> Any:
        """
        Make a request to a service
        
        Args:
            service_name: Name of the service to call
            params: Request parameters
            source: Source node name
            
        Returns:
            Response from the service
        """
        if not self.enabled or service_name not in self.services:
            raise ValueError(f"Service '{service_name}' not found")
        
        handler = self.services[service_name]
        
        try:
            if asyncio.iscoroutinefunction(handler):
                result = await handler(params, source)
            else:
                result = handler(params, source)
            return result
        except Exception as e:
            print(f"Service '{service_name}' error: {e}")
            raise
    
    def get_available_services(self) -> List[str]:
        """Get list of available services"""
        return list(self.services.keys())
    
    # ==================== Shared Blackboard Methods ====================
    
    def set(self, key: str, value: Any, source: str) -> None:
        """
        Set a value in the shared blackboard
        
        Args:
            key: Data key
            value: Data value
            source: Source node name
        """
        if not self.enabled:
            return
        
        self.shared_blackboard.set(key, value)
        self._log_access("set", key, value, source)
    
    def get(self, key: str, default: Any = None, source: str = "") -> Any:
        """
        Get a value from the shared blackboard
        
        Args:
            key: Data key
            default: Default value if key doesn't exist
            source: Source node name
            
        Returns:
            Value from blackboard
        """
        if not self.enabled:
            return default
        
        value = self.shared_blackboard.get(key, default)
        self._log_access("get", key, value, source)
        return value
    
    def has(self, key: str) -> bool:
        """Check if key exists in shared blackboard"""
        return self.shared_blackboard.has(key)
    
    def remove(self, key: str, source: str) -> bool:
        """
        Remove a key from the shared blackboard
        
        Args:
            key: Key to remove
            source: Source node name
            
        Returns:
            True if key was found and removed
        """
        if not self.enabled:
            return False
        
        result = self.shared_blackboard.remove(key)
        if result:
            self._log_access("remove", key, None, source)
        return result
    
    def _log_access(self, operation: str, key: str, value: Any, source: str) -> None:
        """Log blackboard access"""
        log_entry = {
            "timestamp": time.time(),
            "operation": operation,
            "key": key,
            "value": value,
            "source": source
        }
        self.access_log.append(log_entry)
        
        if len(self.access_log) > self.max_log_size:
            self.access_log.pop(0)
    
    def get_access_log(self, source: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get access log"""
        if source is None:
            return self.access_log
        return [entry for entry in self.access_log if entry["source"] == source]
    
    # ==================== State Watching Methods ====================
    
    def watch_state(self, key: str, callback: Callable, source: str) -> None:
        """
        Watch for state changes
        
        Args:
            key: State key to watch
            callback: Callback function to execute on state change
            source: Source node name
        """
        if key not in self.watchers:
            self.watchers[key] = []
        self.watchers[key].append(callback)
    
    def unwatch_state(self, key: str, callback: Callable) -> bool:
        """
        Stop watching a state
        
        Args:
            key: State key to unwatch
            callback: Callback function to remove
            
        Returns:
            True if callback was found and removed
        """
        if key in self.watchers and callback in self.watchers[key]:
            self.watchers[key].remove(callback)
            return True
        return False
    
    async def update_state(self, key: str, value: Any, source: str) -> None:
        """
        Update a state value
        
        Args:
            key: State key
            value: New value
            source: Source node name
        """
        if not self.enabled:
            return
        
        old_value = self.state_cache.get(key)
        self.state_cache[key] = value
        
        # Record state history
        if key not in self.state_history:
            self.state_history[key] = []
        
        history_entry = {
            "timestamp": time.time(),
            "old_value": old_value,
            "new_value": value,
            "source": source
        }
        self.state_history[key].append(history_entry)
        
        # Trim history if needed
        if len(self.state_history[key]) > self.max_history_per_key:
            self.state_history[key].pop(0)
        
        # Notify watchers if value changed
        if old_value != value and key in self.watchers:
            tasks = []
            for callback in self.watchers[key]:
                if asyncio.iscoroutinefunction(callback):
                    task = asyncio.create_task(callback(key, old_value, value, source))
                else:
                    task = asyncio.create_task(self._run_sync_state_callback(callback, key, old_value, value, source))
                tasks.append(task)
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _run_sync_state_callback(self, callback: Callable, key: str, old_value: Any, new_value: Any, source: str) -> None:
        """Run synchronous state callback in async context"""
        try:
            callback(key, old_value, new_value, source)
        except Exception as e:
            print(f"State watching callback error: {e}")
    
    def get_state(self, key: str) -> Any:
        """Get current state value"""
        return self.state_cache.get(key)
    
    def get_state_history(self, key: str) -> List[Dict[str, Any]]:
        """Get state change history"""
        return self.state_history.get(key, [])
    
    def get_watched_keys(self) -> List[str]:
        """Get list of watched state keys"""
        return list(self.watchers.keys())
    
    # ==================== Behavior Call Methods ====================
    
    def register_behavior(self, behavior_name: str, behavior_func: Callable) -> None:
        """
        Register a behavior for external calling
        
        Args:
            behavior_name: Name of the behavior
            behavior_func: Behavior function to register
        """
        self.registered_behaviors[behavior_name] = behavior_func
    
    def unregister_behavior(self, behavior_name: str) -> bool:
        """
        Unregister a behavior
        
        Args:
            behavior_name: Name of the behavior to unregister
            
        Returns:
            True if behavior was found and removed
        """
        if behavior_name in self.registered_behaviors:
            del self.registered_behaviors[behavior_name]
            return True
        return False
    
    async def call_behavior(self, behavior_name: str, params: Dict[str, Any], source: str) -> Any:
        """
        Call a behavior from another tree
        
        Args:
            behavior_name: Name of the behavior to call
            params: Parameters for the behavior
            source: Source node name
            
        Returns:
            Result from the behavior execution
        """
        if not self.enabled or behavior_name not in self.registered_behaviors:
            raise ValueError(f"Behavior '{behavior_name}' not found")
        
        behavior_func = self.registered_behaviors[behavior_name]
        
        # Log the call
        call_entry = {
            "timestamp": time.time(),
            "behavior": behavior_name,
            "params": params,
            "source": source
        }
        self.call_log.append(call_entry)
        
        if len(self.call_log) > self.max_log_size:
            self.call_log.pop(0)
        
        try:
            if asyncio.iscoroutinefunction(behavior_func):
                result = await behavior_func(params)
            else:
                result = behavior_func(params)
            
            # Log successful result
            call_entry["result"] = result
            call_entry["success"] = True
            return result
            
        except Exception as e:
            # Log error
            call_entry["error"] = str(e)
            call_entry["success"] = False
            print(f"Behavior call '{behavior_name}' error: {e}")
            raise
    
    def get_registered_behaviors(self) -> List[str]:
        """Get list of registered behaviors"""
        return list(self.registered_behaviors.keys())
    
    def get_call_log(self, behavior_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get behavior call log"""
        if behavior_name is None:
            return self.call_log
        return [entry for entry in self.call_log if entry["behavior"] == behavior_name]
    
    # ==================== Task Board Methods ====================
    
    def publish_task(self, title: str, description: str, requirements: Set[str], 
                    priority: int = 0, data: Optional[Dict[str, Any]] = None) -> str:
        """
        Publish a task to the task board
        
        Args:
            title: Task title
            description: Task description
            requirements: Set of required capabilities
            priority: Task priority (higher = more important)
            data: Additional task data
            
        Returns:
            Task ID
        """
        if not self.enabled:
            return ""
        
        self.task_counter += 1
        task_id = f"task_{self.task_counter}"
        
        task = Task(
            id=task_id,
            title=title,
            description=description,
            requirements=requirements,
            priority=priority,
            data=data or {}
        )
        
        self.tasks[task_id] = task
        
        # Notify potential claimants
        self._notify_task_available(task)
        
        return task_id
    
    def claim_task(self, task_id: str, claimant: str, capabilities: Set[str]) -> bool:
        """
        Claim a task
        
        Args:
            task_id: ID of the task to claim
            claimant: Name of the claiming node
            capabilities: Set of capabilities of the claimant
            
        Returns:
            True if task was successfully claimed
        """
        if not self.enabled or task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        
        # Check if task is available and claimant has required capabilities
        if (task.status == "pending" and 
            task.requirements.issubset(capabilities)):
            
            task.status = "claimed"
            task.claimed_by = claimant
            
            # Notify task claimed
            self._notify_task_claimed(task)
            return True
        
        return False
    
    def complete_task(self, task_id: str, result: Any = None) -> bool:
        """
        Mark a task as completed
        
        Args:
            task_id: ID of the task to complete
            result: Task result
            
        Returns:
            True if task was found and completed
        """
        if not self.enabled or task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        if task.status == "claimed":
            task.status = "completed"
            task.data["result"] = result
            self._notify_task_completed(task)
            return True
        
        return False
    
    def fail_task(self, task_id: str, error: str = "") -> bool:
        """
        Mark a task as failed
        
        Args:
            task_id: ID of the task to fail
            error: Error message
            
        Returns:
            True if task was found and failed
        """
        if not self.enabled or task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        if task.status in ["pending", "claimed"]:
            task.status = "failed"
            task.data["error"] = error
            self._notify_task_failed(task)
            return True
        
        return False
    
    def get_available_tasks(self, capabilities: Set[str]) -> List[Task]:
        """
        Get available tasks for a node with given capabilities
        
        Args:
            capabilities: Set of capabilities
            
        Returns:
            List of available tasks
        """
        available = []
        for task in self.tasks.values():
            if (task.status == "pending" and 
                task.requirements.issubset(capabilities)):
                available.append(task)
        
        # Sort by priority (highest first)
        available.sort(key=lambda t: t.priority, reverse=True)
        return available
    
    def get_claimed_tasks(self, claimant: str) -> List[Task]:
        """Get tasks claimed by a specific node"""
        return [task for task in self.tasks.values() 
                if task.claimed_by == claimant and task.status == "claimed"]
    
    def register_claim_callback(self, callback: Callable) -> None:
        """Register callback for task claiming events"""
        if "claim_callback" not in self.claim_callbacks:
            self.claim_callbacks["claim_callback"] = []
        self.claim_callbacks["claim_callback"].append(callback)
    
    def _notify_task_available(self, task: Task) -> None:
        """Notify that a task is available"""
        if "task_available" in self.claim_callbacks:
            for callback in self.claim_callbacks["task_available"]:
                asyncio.create_task(callback(task))
    
    def _notify_task_claimed(self, task: Task) -> None:
        """Notify that a task was claimed"""
        if "task_claimed" in self.claim_callbacks:
            for callback in self.claim_callbacks["task_claimed"]:
                asyncio.create_task(callback(task))
    
    def _notify_task_completed(self, task: Task) -> None:
        """Notify that a task was completed"""
        if "task_completed" in self.claim_callbacks:
            for callback in self.claim_callbacks["task_completed"]:
                asyncio.create_task(callback(task))
    
    def _notify_task_failed(self, task: Task) -> None:
        """Notify that a task failed"""
        if "task_failed" in self.claim_callbacks:
            for callback in self.claim_callbacks["task_failed"]:
                asyncio.create_task(callback(task))
    
    def get_task_stats(self) -> Dict[str, Any]:
        """Get task board statistics"""
        total_tasks = len(self.tasks)
        pending_tasks = len([t for t in self.tasks.values() if t.status == "pending"])
        claimed_tasks = len([t for t in self.tasks.values() if t.status == "claimed"])
        completed_tasks = len([t for t in self.tasks.values() if t.status == "completed"])
        failed_tasks = len([t for t in self.tasks.values() if t.status == "failed"])
        
        return {
            "total_tasks": total_tasks,
            "pending_tasks": pending_tasks,
            "claimed_tasks": claimed_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks
        } 