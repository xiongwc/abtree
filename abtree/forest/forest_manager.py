"""
Forest Manager - Multi-Forest Management System

Provides management capabilities for multiple behavior forests,
enabling complex multi-system coordination and monitoring.
"""

import asyncio
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set

from ..core.status import Status
from ..engine.blackboard import Blackboard
from ..engine.event_system import EventSystem
from .communication import (
    BehaviorCallMiddleware,
    PubSubMiddleware,
    ReqRespMiddleware,
    SharedBlackboardMiddleware,
    StateWatchingMiddleware,
    TaskBoardMiddleware,
)
from .core import BehaviorForest, ForestNode, ForestNodeType


class ForestStatus(Enum):
    """Forest status enumeration"""
    STOPPED = auto()
    RUNNING = auto()
    PAUSED = auto()
    ERROR = auto()


@dataclass
class ForestInfo:
    """Forest information container"""
    name: str
    status: ForestStatus
    node_count: int
    middleware_count: int
    tick_rate: float
    uptime: float = 0.0
    total_ticks: int = 0
    error_count: int = 0


class ForestManager:
    """
    Forest Manager - Multi-forest coordination system
    
    Manages multiple behavior forests, providing coordination, monitoring,
    and cross-forest communication capabilities.
    
    Attributes:
        forests: Dictionary of managed forests
        global_blackboard: Global shared blackboard
        global_event_system: Global event system
        cross_forest_middleware: Cross-forest communication middleware
        running: Whether the manager is running
        _task: Manager execution task
    """
    
    def __init__(self, name: str = "ForestManager"):
        """
        Initialize forest manager
        
        Args:
            name: Manager name
        """
        self.name = name
        self.forests: Dict[str, BehaviorForest] = {}
        self.global_blackboard = Blackboard()
        self.global_event_system = EventSystem()
        self.cross_forest_middleware: List[Any] = []
        self.running = False
        self._task: Optional[asyncio.Task] = None
        self._start_time = 0.0
        
        # Initialize cross-forest middleware
        self._init_cross_forest_middleware()
    
    def _init_cross_forest_middleware(self) -> None:
        """Initialize cross-forest communication middleware"""
        # Global pub/sub for cross-forest events
        self.global_pubsub = PubSubMiddleware("GlobalPubSub")
        self.cross_forest_middleware.append(self.global_pubsub)
        
        # Global shared blackboard for cross-forest data
        self.global_shared_blackboard = SharedBlackboardMiddleware("GlobalSharedBlackboard")
        self.cross_forest_middleware.append(self.global_shared_blackboard)
        
        # Global state watching for cross-forest state monitoring
        self.global_state_watching = StateWatchingMiddleware("GlobalStateWatching")
        self.cross_forest_middleware.append(self.global_state_watching)
        
        # Global task board for cross-forest task distribution
        self.global_task_board = TaskBoardMiddleware("GlobalTaskBoard")
        self.cross_forest_middleware.append(self.global_task_board)
    
    def add_forest(self, forest: BehaviorForest) -> None:
        """
        Add forest to manager
        
        Args:
            forest: Behavior forest to add
        """
        if forest.name in self.forests:
            raise ValueError(f"Forest '{forest.name}' already exists in manager")
        
        self.forests[forest.name] = forest
        
        # Add cross-forest middleware to the forest
        for middleware in self.cross_forest_middleware:
            forest.add_middleware(middleware)
        
        # Subscribe to forest events
        forest.forest_event_system.on("forest_started", self._on_forest_started)
        forest.forest_event_system.on("forest_stopped", self._on_forest_stopped)
        forest.forest_event_system.on("forest_reset", self._on_forest_reset)
        
        # Emit forest added event
        asyncio.create_task(
            self.global_event_system.emit(
                "forest_added",
                {"forest_name": forest.name, "manager_name": self.name}
            )
        )
    
    def remove_forest(self, forest_name: str) -> bool:
        """
        Remove forest from manager
        
        Args:
            forest_name: Name of forest to remove
            
        Returns:
            True if forest was found and removed
        """
        if forest_name not in self.forests:
            return False
        
        forest = self.forests.pop(forest_name)
        
        # Stop forest if running
        if forest.running:
            asyncio.create_task(forest.stop())
        
        # Emit forest removed event
        asyncio.create_task(
            self.global_event_system.emit(
                "forest_removed",
                {"forest_name": forest_name, "manager_name": self.name}
            )
        )
        
        return True
    
    def get_forest(self, forest_name: str) -> Optional[BehaviorForest]:
        """
        Get forest by name
        
        Args:
            forest_name: Name of the forest
            
        Returns:
            Behavior forest or None if not found
        """
        return self.forests.get(forest_name)
    
    def get_forests_by_status(self, status: ForestStatus) -> List[BehaviorForest]:
        """
        Get forests by status
        
        Args:
            status: Status to filter by
            
        Returns:
            List of forests with specified status
        """
        return [forest for forest in self.forests.values() 
                if self._get_forest_status(forest) == status]
    
    def _get_forest_status(self, forest: BehaviorForest) -> ForestStatus:
        """Get status of a forest"""
        if not forest.running:
            return ForestStatus.STOPPED
        # Add more status logic as needed
        return ForestStatus.RUNNING
    
    async def start_all_forests(self, tick_rate: Optional[float] = None) -> None:
        """
        Start all forests
        
        Args:
            tick_rate: Execution frequency for all forests
        """
        tasks = []
        for forest in self.forests.values():
            if not forest.running:
                task = asyncio.create_task(forest.start())
                tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def stop_all_forests(self) -> None:
        """Stop all forests"""
        tasks = []
        for forest in self.forests.values():
            if forest.running:
                task = asyncio.create_task(forest.stop())
                tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def start(self) -> None:
        """Start forest manager"""
        if self.running:
            return
        
        self.running = True
        self._start_time = asyncio.get_event_loop().time()
        
        # Start all forests
        await self.start_all_forests()
        
        # Start manager monitoring task
        self._task = asyncio.create_task(self._monitor_forests())
        
        # Emit manager start event
        await self.global_event_system.emit(
            "manager_started",
            {"manager_name": self.name, "forest_count": len(self.forests)}
        )
    
    async def stop(self) -> None:
        """Stop forest manager"""
        if not self.running:
            return
        
        self.running = False
        
        # Stop all forests
        await self.stop_all_forests()
        
        # Stop manager task
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        
        # Emit manager stop event
        await self.global_event_system.emit(
            "manager_stopped",
            {"manager_name": self.name}
        )
    
    async def _monitor_forests(self) -> None:
        """Monitor all forests for health and status"""
        while self.running:
            try:
                # Check forest health
                for forest_name, forest in self.forests.items():
                    if forest.running:
                        # Monitor forest performance
                        stats = forest.get_stats()
                        
                        # Emit monitoring event
                        await self.global_event_system.emit(
                            "forest_monitoring",
                            {
                                "forest_name": forest_name,
                                "stats": stats,
                                "timestamp": asyncio.get_event_loop().time()
                            }
                        )
                
                await asyncio.sleep(5.0)  # Monitor every 5 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Forest manager monitoring error: {e}")
                await asyncio.sleep(1.0)
    
    def _on_forest_started(self, event: Any) -> None:
        """Handle forest started event"""
        asyncio.create_task(
            self.global_event_system.emit(
                "forest_started_global",
                event.data
            )
        )
    
    def _on_forest_stopped(self, event: Any) -> None:
        """Handle forest stopped event"""
        asyncio.create_task(
            self.global_event_system.emit(
                "forest_stopped_global",
                event.data
            )
        )
    
    def _on_forest_reset(self, event: Any) -> None:
        """Handle forest reset event"""
        asyncio.create_task(
            self.global_event_system.emit(
                "forest_reset_global",
                event.data
            )
        )
    
    def get_forest_info(self, forest_name: str) -> Optional[ForestInfo]:
        """
        Get detailed information about a forest
        
        Args:
            forest_name: Name of the forest
            
        Returns:
            Forest information or None if not found
        """
        forest = self.get_forest(forest_name)
        if not forest:
            return None
        
        stats = forest.get_stats()
        status = self._get_forest_status(forest)
        
        return ForestInfo(
            name=forest_name,
            status=status,
            node_count=stats["total_nodes"],
            middleware_count=stats["middleware_count"],
            tick_rate=stats.get("tick_rate", None),
            uptime=asyncio.get_event_loop().time() - self._start_time if self.running else 0.0,
            total_ticks=0,  # TODO: Add tick counting
            error_count=0    # TODO: Add error counting
        )
    
    def get_all_forest_info(self) -> List[ForestInfo]:
        """Get information about all forests"""
        return [self.get_forest_info(name) for name in self.forests.keys()]
    
    def get_manager_stats(self) -> Dict[str, Any]:
        """
        Get manager statistics
        
        Returns:
            Manager statistics dictionary
        """
        running_forests = len([f for f in self.forests.values() if f.running])
        total_nodes = sum(len(f.nodes) for f in self.forests.values())
        
        return {
            "name": self.name,
            "running": self.running,
            "total_forests": len(self.forests),
            "running_forests": running_forests,
            "total_nodes": total_nodes,
            "uptime": asyncio.get_event_loop().time() - self._start_time if self.running else 0.0,
            "cross_forest_middleware": len(self.cross_forest_middleware)
        }
    
    def publish_global_event(self, topic: str, data: Any) -> None:
        """
        Publish event to all forests
        
        Args:
            topic: Event topic
            data: Event data
        """
        asyncio.create_task(
            self.global_pubsub.publish(topic, data, self.name)
        )
    
    def set_global_data(self, key: str, value: Any) -> None:
        """
        Set data in global shared blackboard
        
        Args:
            key: Data key
            value: Data value
        """
        self.global_shared_blackboard.set(key, value, self.name)
    
    def get_global_data(self, key: str, default: Any = None) -> Any:
        """
        Get data from global shared blackboard
        
        Args:
            key: Data key
            default: Default value
            
        Returns:
            Data value
        """
        return self.global_shared_blackboard.get(key, default, self.name)
    
    def watch_global_state(self, key: str, callback: Any) -> None:
        """
        Watch for global state changes
        
        Args:
            key: State key to watch
            callback: Callback function
        """
        self.global_state_watching.watch_state(key, callback, self.name)
    
    def publish_global_task(self, title: str, description: str, requirements: Set[str],
                           priority: int = 0, data: Dict[str, Any] = None) -> str:
        """
        Publish task to global task board
        
        Args:
            title: Task title
            description: Task description
            requirements: Required capabilities
            priority: Task priority
            data: Additional task data
            
        Returns:
            Task ID
        """
        return self.global_task_board.publish_task(
            title, description, requirements, priority, data
        )
    
    def __repr__(self) -> str:
        stats = self.get_manager_stats()
        return f"ForestManager(name='{self.name}', forests={stats['total_forests']}, running={self.running})" 