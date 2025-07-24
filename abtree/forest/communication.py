"""
Communication Middleware - Unified Inter-Behavior Tree Communication

Provides 6 different communication patterns for behavior trees in the forest:
1. Pub/Sub (Publish-Subscribe) - Event-driven communication
2. Req/Resp (Request-Response) - Service call communication  
3. Shared Blackboard - Cross-tree data sharing
4. State Watching - State change monitoring
5. Behavior Call - Direct behavior tree calls
6. Task Board - Task distribution and claiming

Optimized for zero-copy data transfer to minimize memory overhead and improve performance.
"""

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set, Union, MutableMapping

from ..core.status import Status
from ..engine.blackboard import Blackboard
from ..engine.event_system import EventSystem
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
    """Base message class for communication - optimized for zero-copy"""
    id: str
    source: str
    target: Optional[str] = None
    data: Any = None  # Direct reference, no copying
    timestamp: float = field(default_factory=time.time)
    priority: int = 0


@dataclass
class Request(Message):
    """Request message for Req/Resp pattern - optimized for zero-copy"""
    method: str = ""
    params: Dict[str, Any] = field(default_factory=dict)  # Direct reference


@dataclass
class Response(Message):
    """Response message for Req/Resp pattern - optimized for zero-copy"""
    request_id: str = ""
    success: bool = True
    error: Optional[str] = None


@dataclass
class Task:
    """Task for Task Board pattern - optimized for zero-copy"""
    id: str
    title: str
    description: str
    requirements: Set[str] = field(default_factory=set)  # Direct reference
    priority: int = 0
    status: str = "pending"  # pending, claimed, completed, failed
    claimed_by: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    data: Dict[str, Any] = field(default_factory=dict)  # Direct reference


class CommunicationMiddleware:
    """
    Unified Communication Middleware - Zero-Copy Optimized
    
    Provides all 6 communication patterns in a single middleware:
    - Pub/Sub: Event-driven communication
    - Req/Resp: Service call communication
    - Shared Blackboard: Cross-tree data sharing
    - State Watching: State change monitoring
    - Behavior Call: Direct behavior tree calls
    - Task Board: Task distribution and claiming
    
    Optimized for zero-copy data transfer to minimize memory overhead.
    """
    
    def __init__(self, name: str = "CommunicationMiddleware"):
        self.name = name
        self.forest: Optional[BehaviorForest] = None
        self.enabled = True
        
        # Pub/Sub components - using direct references
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_history: List[Dict[str, Any]] = []
        self.max_history = 1000
        
        # Req/Resp components - using direct references
        self.services: Dict[str, Callable] = {}
        self.pending_requests: Dict[str, asyncio.Future] = {}
        self.request_counter = 0
        
        # Shared Blackboard components - using direct references
        self.shared_blackboard = Blackboard()
        self.access_log: List[Dict[str, Any]] = []
        self.max_log_size = 1000
        
        # State Watching components - using direct references
        self.watchers: Dict[str, List[Callable]] = {}
        self.state_cache: Dict[str, Any] = {}
        self.state_history: Dict[str, List[Dict[str, Any]]] = {}
        self.max_history_per_key = 100
        
        # Behavior Call components - using direct references
        self.registered_behaviors: Dict[str, Callable] = {}
        self.call_log: List[Dict[str, Any]] = []
        
        # Task Board components - using direct references
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
    
    # ==================== Pub/Sub Methods - Zero-Copy Optimized ====================
    
    def subscribe(self, topic: str, callback: Callable) -> None:
        """
        Subscribe to a topic - zero-copy optimized
        
        Args:
            topic: Topic to subscribe to
            callback: Callback function to execute when event is published
        """
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)
    
    def unsubscribe(self, topic: str, callback: Callable) -> bool:
        """
        Unsubscribe from a topic - zero-copy optimized
        
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
        Publish an event to a topic - zero-copy optimized
        
        Args:
            topic: Topic to publish to
            data: Event data (passed by reference, no copying)
            source: Source node name
        """
        if not self.enabled:
            return
        
        # Create event info with direct reference to data (no copying)
        event_info = {
            "name": topic,
            "data": data,
            "source": source,
            "timestamp": time.time()
        }
        self.event_history.append(event_info)
        
        # Trim history if needed
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
        
        # Execute callbacks with direct event info reference
        if topic in self.subscribers:
            tasks = []
            for callback in self.subscribers[topic]:
                if asyncio.iscoroutinefunction(callback):
                    task = asyncio.create_task(callback(event_info))
                else:
                    task = asyncio.create_task(self._run_sync_callback(callback, event_info))
                tasks.append(task)
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _run_sync_callback(self, callback: Callable, event_info: Dict[str, Any]) -> None:
        """Run synchronous callback in async context - zero-copy optimized"""
        try:
            callback(event_info)  # Direct event info reference
        except Exception as e:
            print(f"PubSub callback error: {e}")
    
    def get_subscribers(self, topic: str) -> List[Callable]:
        """Get subscribers for a topic - zero-copy optimized"""
        return self.subscribers.get(topic, [])
    
    def get_event_history(self, topic: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get event history - zero-copy optimized"""
        if topic is None:
            return self.event_history  # Direct reference
        return [event for event in self.event_history if event["name"] == topic]
    
    # ==================== Req/Resp Methods - Zero-Copy Optimized ====================
    
    def register_service(self, service_name: str, handler: Callable) -> None:
        """
        Register a service - zero-copy optimized
        
        Args:
            service_name: Name of the service
            handler: Handler function for the service
        """
        self.services[service_name] = handler
    
    def unregister_service(self, service_name: str) -> bool:
        """
        Unregister a service - zero-copy optimized
        
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
        Make a request to a service - zero-copy optimized
        
        Args:
            service_name: Name of the service to call
            params: Request parameters (passed by reference)
            source: Source node name
            
        Returns:
            Response from the service
        """
        if not self.enabled or service_name not in self.services:
            raise ValueError(f"Service '{service_name}' not found")
        
        handler = self.services[service_name]
        
        try:
            if asyncio.iscoroutinefunction(handler):
                result = await handler(params, source)  # Direct params reference
            else:
                result = handler(params, source)  # Direct params reference
            return result
        except Exception as e:
            print(f"Service '{service_name}' error: {e}")
            raise
    
    def get_available_services(self) -> List[str]:
        """Get list of available services - zero-copy optimized"""
        return list(self.services.keys())
    
    # ==================== Shared Blackboard Methods - Zero-Copy Optimized ====================
    
    def set(self, key: str, value: Any, source: str) -> None:
        """
        Set a value in the shared blackboard - zero-copy optimized
        
        Args:
            key: Data key
            value: Data value (stored by reference)
            source: Source node name
        """
        if not self.enabled:
            return
        
        self.shared_blackboard.set(key, value)  # Direct reference storage
        self._log_access("set", key, value, source)
    
    def get(self, key: str, default: Any = None, source: str = "") -> Any:
        """
        Get a value from the shared blackboard - zero-copy optimized
        
        Args:
            key: Data key
            default: Default value if key doesn't exist
            source: Source node name
            
        Returns:
            Value from blackboard (direct reference)
        """
        if not self.enabled:
            return default
        
        value = self.shared_blackboard.get(key, default)  # Direct reference retrieval
        self._log_access("get", key, value, source)
        return value
    
    def has(self, key: str) -> bool:
        """Check if key exists in shared blackboard - zero-copy optimized"""
        return self.shared_blackboard.has(key)
    
    def remove(self, key: str, source: str) -> bool:
        """
        Remove a key from the shared blackboard - zero-copy optimized
        
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
        """Log blackboard access - zero-copy optimized"""
        log_entry = {
            "timestamp": time.time(),
            "operation": operation,
            "key": key,
            "value": value,  # Direct reference
            "source": source
        }
        self.access_log.append(log_entry)
        
        if len(self.access_log) > self.max_log_size:
            self.access_log.pop(0)
    
    def get_access_log(self, source: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get access log - zero-copy optimized"""
        if source is None:
            return self.access_log  # Direct reference
        return [entry for entry in self.access_log if entry["source"] == source]
    
    # ==================== State Watching Methods - Zero-Copy Optimized ====================
    
    def watch_state(self, key: str, callback: Callable, source: str) -> None:
        """
        Watch for state changes - zero-copy optimized
        
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
        Stop watching a state - zero-copy optimized
        
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
        Update a state value - zero-copy optimized
        
        Args:
            key: State key
            value: New value (stored by reference)
            source: Source node name
        """
        if not self.enabled:
            return
        
        old_value = self.state_cache.get(key)
        self.state_cache[key] = value  # Direct reference storage
        
        # Record state history with direct references
        if key not in self.state_history:
            self.state_history[key] = []
        
        history_entry = {
            "timestamp": time.time(),
            "old_value": old_value,  # Direct reference
            "new_value": value,  # Direct reference
            "source": source
        }
        self.state_history[key].append(history_entry)
        
        # Trim history if needed
        if len(self.state_history[key]) > self.max_history_per_key:
            self.state_history[key].pop(0)
        
        # Notify watchers if value changed - with direct references
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
        """Run synchronous state callback in async context - zero-copy optimized"""
        try:
            callback(key, old_value, new_value, source)  # Direct references
        except Exception as e:
            print(f"State watching callback error: {e}")
    
    def get_state(self, key: str) -> Any:
        """Get current state value - zero-copy optimized"""
        return self.state_cache.get(key)  # Direct reference
    
    def get_state_history(self, key: str) -> List[Dict[str, Any]]:
        """Get state change history - zero-copy optimized"""
        return self.state_history.get(key, [])  # Direct reference
    
    def get_watched_keys(self) -> List[str]:
        """Get list of watched state keys - zero-copy optimized"""
        return list(self.watchers.keys())
    
    # ==================== Behavior Call Methods - Zero-Copy Optimized ====================
    
    def register_behavior(self, behavior_name: str, behavior_func: Callable) -> None:
        """
        Register a behavior for external calling - zero-copy optimized
        
        Args:
            behavior_name: Name of the behavior
            behavior_func: Behavior function to register
        """
        self.registered_behaviors[behavior_name] = behavior_func
    
    def unregister_behavior(self, behavior_name: str) -> bool:
        """
        Unregister a behavior - zero-copy optimized
        
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
        Call a behavior from another tree - zero-copy optimized
        
        Args:
            behavior_name: Name of the behavior to call
            params: Parameters for the behavior (passed by reference)
            source: Source node name
            
        Returns:
            Result from the behavior execution
        """
        if not self.enabled or behavior_name not in self.registered_behaviors:
            raise ValueError(f"Behavior '{behavior_name}' not found")
        
        behavior_func = self.registered_behaviors[behavior_name]
        
        # Log the call with direct references
        call_entry = {
            "timestamp": time.time(),
            "behavior": behavior_name,
            "params": params,  # Direct reference
            "source": source
        }
        self.call_log.append(call_entry)
        
        if len(self.call_log) > self.max_log_size:
            self.call_log.pop(0)
        
        try:
            if asyncio.iscoroutinefunction(behavior_func):
                result = await behavior_func(params)  # Direct params reference
            else:
                result = behavior_func(params)  # Direct params reference
            
            # Log successful result with direct reference
            call_entry["result"] = result  # Direct reference
            call_entry["success"] = True
            return result
            
        except Exception as e:
            # Log error
            call_entry["error"] = str(e)
            call_entry["success"] = False
            print(f"Behavior call '{behavior_name}' error: {e}")
            raise
    
    def get_registered_behaviors(self) -> List[str]:
        """Get list of registered behaviors - zero-copy optimized"""
        return list(self.registered_behaviors.keys())
    
    def get_call_log(self, behavior_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get behavior call log - zero-copy optimized"""
        if behavior_name is None:
            return self.call_log  # Direct reference
        return [entry for entry in self.call_log if entry["behavior"] == behavior_name]
    
    # ==================== Task Board Methods - Zero-Copy Optimized ====================
    
    def publish_task(self, title: str, description: str, requirements: Set[str], 
                    priority: int = 0, data: Optional[Dict[str, Any]] = None) -> str:
        """
        Publish a task to the task board - zero-copy optimized
        
        Args:
            title: Task title
            description: Task description
            requirements: Set of required capabilities (passed by reference)
            priority: Task priority (higher = more important)
            data: Additional task data (passed by reference)
            
        Returns:
            Task ID
        """
        if not self.enabled:
            return ""
        
        self.task_counter += 1
        task_id = f"task_{self.task_counter}"
        
        # Create task with direct references (no copying)
        task = Task(
            id=task_id,
            title=title,
            description=description,
            requirements=requirements,  # Direct reference
            priority=priority,
            data=data or {}  # Direct reference
        )
        
        self.tasks[task_id] = task
        
        # Notify potential claimants
        self._notify_task_available(task)
        
        return task_id
    
    def claim_task(self, task_id: str, claimant: str, capabilities: Set[str]) -> bool:
        """
        Claim a task - zero-copy optimized
        
        Args:
            task_id: ID of the task to claim
            claimant: Name of the claiming node
            capabilities: Set of capabilities of the claimant (passed by reference)
            
        Returns:
            True if task was successfully claimed
        """
        if not self.enabled or task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        
        # Check if task is available and claimant has required capabilities
        if (task.status == "pending" and 
            task.requirements.issubset(capabilities)):  # Direct reference comparison
            
            task.status = "claimed"
            task.claimed_by = claimant
            
            # Notify task claimed
            self._notify_task_claimed(task)
            return True
        
        return False
    
    def complete_task(self, task_id: str, result: Any = None) -> bool:
        """
        Mark a task as completed - zero-copy optimized
        
        Args:
            task_id: ID of the task to complete
            result: Task result (stored by reference)
            
        Returns:
            True if task was found and completed
        """
        if not self.enabled or task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        if task.status == "claimed":
            task.status = "completed"
            task.data["result"] = result  # Direct reference storage
            self._notify_task_completed(task)
            return True
        
        return False
    
    def fail_task(self, task_id: str, error: str = "") -> bool:
        """
        Mark a task as failed - zero-copy optimized
        
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
        Get available tasks for a node with given capabilities - zero-copy optimized
        
        Args:
            capabilities: Set of capabilities (passed by reference)
            
        Returns:
            List of available tasks (direct references)
        """
        available = []
        for task in self.tasks.values():
            if (task.status == "pending" and 
                task.requirements.issubset(capabilities)):  # Direct reference comparison
                available.append(task)  # Direct reference
        
        # Sort by priority (highest first)
        available.sort(key=lambda t: t.priority, reverse=True)
        return available
    
    def get_claimed_tasks(self, claimant: str) -> List[Task]:
        """Get tasks claimed by a specific node - zero-copy optimized"""
        return [task for task in self.tasks.values() 
                if task.claimed_by == claimant and task.status == "claimed"]  # Direct references
    
    def register_claim_callback(self, callback: Callable) -> None:
        """Register callback for task claiming events - zero-copy optimized"""
        if "claim_callback" not in self.claim_callbacks:
            self.claim_callbacks["claim_callback"] = []
        self.claim_callbacks["claim_callback"].append(callback)
    
    def _notify_task_available(self, task: Task) -> None:
        """Notify that a task is available - zero-copy optimized"""
        if "task_available" in self.claim_callbacks:
            for callback in self.claim_callbacks["task_available"]:
                asyncio.create_task(callback(task))  # Direct task reference
    
    def _notify_task_claimed(self, task: Task) -> None:
        """Notify that a task was claimed - zero-copy optimized"""
        if "task_claimed" in self.claim_callbacks:
            for callback in self.claim_callbacks["task_claimed"]:
                asyncio.create_task(callback(task))  # Direct task reference
    
    def _notify_task_completed(self, task: Task) -> None:
        """Notify that a task was completed - zero-copy optimized"""
        if "task_completed" in self.claim_callbacks:
            for callback in self.claim_callbacks["task_completed"]:
                asyncio.create_task(callback(task))  # Direct task reference
    
    def _notify_task_failed(self, task: Task) -> None:
        """Notify that a task failed - zero-copy optimized"""
        if "task_failed" in self.claim_callbacks:
            for callback in self.claim_callbacks["task_failed"]:
                asyncio.create_task(callback(task))  # Direct task reference
    
    def get_task_stats(self) -> Dict[str, Any]:
        """Get task board statistics - zero-copy optimized"""
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