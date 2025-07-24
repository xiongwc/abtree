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
    CommunicationMiddleware,
    CommunicationType,
    Message,
    Request,
    Response,
    Task,
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
        # Global communication middleware for cross-forest communication
        self.global_communication = CommunicationMiddleware("GlobalCommunication")
        self.cross_forest_middleware.append(self.global_communication)
    
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
        
        # Note: Event subscription is handled differently in the new event system
        # Forest events will be handled through the global event system
        
        # Emit forest added event
        asyncio.create_task(
            self.global_event_system.emit(
                "forest_added",
                source=f"{self.name}:{forest.name}"
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
                source=f"{self.name}:{forest_name}"
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
            source=self.name
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
            source=self.name
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
                            source=forest_name
                        )
                
                await asyncio.sleep(5.0)  # Monitor every 5 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Forest manager monitoring error: {e}")
                await asyncio.sleep(1.0)
    
    async def _on_forest_started(self, forest_name: str) -> None:
        """Handle forest started event"""
        await self.global_event_system.emit(
            "forest_started_global",
            source=forest_name
        )
    
    async def _on_forest_stopped(self, forest_name: str) -> None:
        """Handle forest stopped event"""
        await self.global_event_system.emit(
            "forest_stopped_global",
            source=forest_name
        )
    
    async def _on_forest_reset(self, forest_name: str) -> None:
        """Handle forest reset event"""
        await self.global_event_system.emit(
            "forest_reset_global",
            source=forest_name
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
            tick_rate=stats.get("tick_rate", 0.0),
            uptime=asyncio.get_event_loop().time() - self._start_time if self.running else 0.0,
            total_ticks=0,  # TODO: Add tick counting
            error_count=0    # TODO: Add error counting
        )
    
    def get_all_forest_info(self) -> List[ForestInfo]:
        """Get information about all forests"""
        forest_infos = []
        for name in self.forests.keys():
            info = self.get_forest_info(name)
            if info is not None:
                forest_infos.append(info)
        return forest_infos
    
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
            self.global_communication.publish(topic, data, self.name)
        )
    
    def set_global_data(self, key: str, value: Any) -> None:
        """
        Set data in global shared blackboard
        
        Args:
            key: Data key
            value: Data value
        """
        self.global_communication.set(key, value, self.name)
    
    def get_global_data(self, key: str, default: Any = None) -> Any:
        """
        Get data from global shared blackboard
        
        Args:
            key: Data key
            default: Default value
            
        Returns:
            Data value
        """
        return self.global_communication.get(key, default, self.name)
    
    def watch_global_state(self, key: str, callback: Any) -> None:
        """
        Watch for global state changes
        
        Args:
            key: State key to watch
            callback: Callback function
        """
        self.global_communication.watch_state(key, callback, self.name)
    
    def publish_global_task(self, title: str, description: str, requirements: Set[str],
                           priority: int = 0, data: Optional[Dict[str, Any]] = None) -> str:
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
        return self.global_communication.publish_task(
            title, description, requirements, priority, data
        )
    
    def __repr__(self) -> str:
        stats = self.get_manager_stats()
        return f"ForestManager(name='{self.name}', forests={stats['total_forests']}, running={self.running})" 