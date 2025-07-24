"""
Behavior Forest Core - Core classes for multi-behavior tree collaboration

Provides the core classes for behavior forest architecture, including BehaviorForest
and ForestNode that enable multiple behavior trees to work together.
"""

import asyncio
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Union

from ..core.status import Status
from ..engine.behavior_tree import BehaviorTree
from ..engine.blackboard import Blackboard
from ..engine.event_system import EventSystem


class ForestNodeType(Enum):
    """Forest node type enumeration"""
    MASTER = auto()      # Master node with coordination capabilities
    WORKER = auto()      # Worker node for specific tasks
    MONITOR = auto()     # Monitor node for system monitoring
    COORDINATOR = auto() # Coordinator node for task distribution


@dataclass
class ForestNode:
    """
    Forest Node - Individual behavior tree in the forest
    
    Each forest node represents a behavior tree with its own control logic,
    perception capabilities, and state management.
    
    Attributes:
        name: Node name
        tree: Behavior tree instance
        node_type: Type of forest node
        capabilities: Set of node capabilities
        dependencies: Set of node dependencies
        status: Current node status
        metadata: Additional node metadata
    """
    
    name: str
    tree: BehaviorTree
    node_type: ForestNodeType = ForestNodeType.WORKER
    capabilities: Set[str] = field(default_factory=set)
    dependencies: Set[str] = field(default_factory=set)
    status: Status = Status.FAILURE
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Initialize node after creation"""
        if not self.capabilities:
            self.capabilities = {self.node_type.name.lower()}
    
    async def tick(self) -> Status:
        """
        Execute one tick of the behavior tree
        
        Returns:
            Execution status
        """
        try:
            self.status = await self.tree.tick()
            return self.status
        except Exception as e:
            print(f"Forest node '{self.name}' tick error: {e}")
            self.status = Status.FAILURE
            return Status.FAILURE
    
    def add_capability(self, capability: str) -> None:
        """Add capability to the node"""
        self.capabilities.add(capability)
    
    def remove_capability(self, capability: str) -> None:
        """Remove capability from the node"""
        self.capabilities.discard(capability)
    
    def has_capability(self, capability: str) -> bool:
        """Check if node has specific capability"""
        return capability in self.capabilities
    
    def add_dependency(self, dependency: str) -> None:
        """Add dependency to the node"""
        self.dependencies.add(dependency)
    
    def remove_dependency(self, dependency: str) -> None:
        """Remove dependency from the node"""
        self.dependencies.discard(dependency)
    
    def get_blackboard(self) -> Blackboard:
        """Get node's blackboard"""
        blackboard = self.tree.blackboard
        if blackboard is None:
            raise ValueError("Tree blackboard is not initialized")
        return blackboard
    
    def get_event_system(self) -> EventSystem:
        """Get node's event system"""
        event_system = self.tree.event_system
        if event_system is None:
            raise ValueError("Tree event system is not initialized")
        return event_system
    
    def reset(self) -> None:
        """Reset node status"""
        self.tree.reset()
        self.status = Status.FAILURE
    
    def __repr__(self) -> str:
        return f"ForestNode(name='{self.name}', type={self.node_type.name}, status={self.status.name})"


class BehaviorForest:
    """
    Behavior Forest - Multi-behavior tree collaboration system
    
    A forest consists of multiple behavior trees that can communicate and collaborate
    through various middleware patterns, enabling complex multi-agent systems.
    
    Attributes:
        name: Forest name
        nodes: Dictionary of forest nodes
        middleware: List of communication middleware
        forest_blackboard: Shared forest blackboard
        forest_event_system: Forest-level event system
        running: Whether the forest is running
        _task: Forest execution task
    """
    
    def __init__(
        self,
        name: str = "BehaviorForest",
        forest_blackboard: Optional[Blackboard] = None,
        forest_event_system: Optional[EventSystem] = None,
    ):
        """
        Initialize behavior forest
        
        Args:
            name: Forest name
            forest_blackboard: Shared forest blackboard
            forest_event_system: Forest-level event system
        """
        self.name = name
        self.nodes: Dict[str, ForestNode] = {}
        self.middleware: List[Any] = []
        self.forest_blackboard = forest_blackboard or Blackboard()
        self.forest_event_system = forest_event_system or EventSystem()
        self.running = False
        self._task: Optional[asyncio.Task] = None
        # Track running tasks for each node to prevent duplicate task creation
        self._node_tasks: Dict[str, Optional[asyncio.Task]] = {}
        # Track execution states to prevent race conditions
        self._node_execution_states: Dict[str, bool] = {}
        # Track last execution time to prevent rapid re-execution
        self._node_last_execution: Dict[str, float] = {} 

    def add_node(self, node: ForestNode) -> None:
        """
        Add node to the forest
        
        Args:
            node: Forest node to add
        """
        if node.name in self.nodes:
            raise ValueError(f"Node '{node.name}' already exists in forest")
        
        self.nodes[node.name] = node
        # Initialize task tracking for the new node
        self._node_tasks[node.name] = None
        # Initialize execution state for the new node
        self._node_execution_states[node.name] = False
        # Initialize last execution time for the new node
        self._node_last_execution[node.name] = 0.0
        
        # Emit node added event
        try:
            asyncio.create_task(
                self.forest_event_system.emit(
                    "node_added",
                    source=node.name
                )
            )
        except RuntimeError:
            # No running event loop, skip async event emission
            pass 

    def remove_node(self, node_name: str) -> bool:
        """
        Remove node from the forest
        
        Args:
            node_name: Name of node to remove
            
        Returns:
            True if node was found and removed, False otherwise
        """
        if node_name not in self.nodes:
            return False
        
        node = self.nodes.pop(node_name)
        
        # Cancel and clean up task tracking for the removed node
        task = self._node_tasks.get(node_name)
        if task is not None:
            task.cancel()
            self._node_tasks[node_name] = None
        
        # Clean up task execution state
        if node_name in self._node_execution_states:
            self._node_execution_states.pop(node_name)
        
        # Clean up last execution time
        if node_name in self._node_last_execution:
            self._node_last_execution.pop(node_name)
        
        # Emit node removed event
        try:
            asyncio.create_task(
                self.forest_event_system.emit(
                    "node_removed",
                    source=node_name
                )
            )
        except RuntimeError:
            # No running event loop, skip async event emission
            pass
        
        return True 

    async def tick(self) -> Dict[str, Status]:
        """
        Execute tick for all nodes in the forest
        
        Returns:
            Dictionary mapping node names to their execution status
        """
        results = {}
        
        # Execute middleware pre-tick processing
        for middleware in self.middleware:
            if hasattr(middleware, 'pre_tick'):
                await middleware.pre_tick()
        
        # Execute tick for all nodes
        for node_name, node in self.nodes.items():
            try:
                # Execute the node's tick
                status = await node.tick()
                results[node_name] = status
            except Exception as e:
                print(f"Error ticking node '{node_name}': {e}")
                results[node_name] = Status.FAILURE
        
        # Execute middleware post-tick processing
        for middleware in self.middleware:
            if hasattr(middleware, 'post_tick'):
                await middleware.post_tick(results)
        
        return results
    
    def get_node(self, node_name: str) -> Optional[ForestNode]:
        """
        Get node by name
        
        Args:
            node_name: Name of the node
            
        Returns:
            Forest node or None if not found
        """
        return self.nodes.get(node_name)
    
    def get_nodes_by_type(self, node_type: ForestNodeType) -> List[ForestNode]:
        """
        Get all nodes of specific type
        
        Args:
            node_type: Type of nodes to get
            
        Returns:
            List of nodes of specified type
        """
        return [node for node in self.nodes.values() if node.node_type == node_type]
    
    def get_nodes_by_capability(self, capability: str) -> List[ForestNode]:
        """
        Get all nodes with specific capability
        
        Args:
            capability: Capability to search for
            
        Returns:
            List of nodes with specified capability
        """
        return [node for node in self.nodes.values() if node.has_capability(capability)]
    
    def add_middleware(self, middleware: Any) -> None:
        """
        Add communication middleware
        
        Args:
            middleware: Middleware instance to add
        """
        self.middleware.append(middleware)
        
        # Initialize middleware with forest
        if hasattr(middleware, 'initialize'):
            middleware.initialize(self)
    
    def remove_middleware(self, middleware: Any) -> bool:
        """
        Remove communication middleware
        
        Args:
            middleware: Middleware instance to remove
            
        Returns:
            True if middleware was found and removed, False otherwise
        """
        if middleware in self.middleware:
            self.middleware.remove(middleware)
            return True
        return False
    
    async def _tick_node(self, node: ForestNode) -> Status:
        """
        Execute tick for a single node
        
        Args:
            node: Forest node to tick
            
        Returns:
            Node execution status
        """
        return await node.tick()
    
    async def _tick_node_async(self, node_name: str, node: ForestNode) -> None:
        """
        Execute tick for a single node asynchronously
        
        Args:
            node_name: Name of the node
            node: Forest node to tick
        """
        try:
            status = await self._tick_node(node)
            # Update node status after completion
            node.status = status
        except Exception as e:
            print(f"Node '{node_name}' tick error: {e}")
            node.status = Status.FAILURE
        finally:
            # Clean up task tracking when task completes
            if node_name in self._node_tasks:
                self._node_tasks[node_name] = None
            # Reset execution state after task completion
            if node_name in self._node_execution_states:
                self._node_execution_states[node_name] = False
    
    async def start(self) -> None:
        """
        Start forest execution - runs as an infinite loop service
        Also starts each behavior tree's tick manager
        """
        if self.running:
            return
        
        self.running = True
        
        # Start each behavior tree's tick manager
        for node_name, node in self.nodes.items():
            try:
                if node.tree.tick_manager:
                    # Get the tick rate from the tick manager
                    tick_rate = node.tree.tick_manager.tick_rate
                    await node.tree.start(tick_rate=tick_rate)
                    print(f"🌳 Started behavior tree: {node_name} (tick_rate: {tick_rate})")
            except Exception as e:
                print(f"❌ Failed to start behavior tree {node_name}: {e}")
        
        # Emit forest start event
        await self.forest_event_system.emit(
            "forest_started",
            source=self.name
        )
        
        # Start forest execution task for coordination and monitoring
        self._task = asyncio.create_task(self._run())
    
    async def stop(self) -> None:
        """Stop forest execution and all behavior trees"""
        if not self.running:
            return
        
        self.running = False
        
        # Stop each behavior tree's tick manager
        for node_name, node in self.nodes.items():
            try:
                if node.tree.tick_manager:
                    await node.tree.stop()
                    print(f"🛑 Stopped behavior tree: {node_name}")
            except Exception as e:
                print(f"❌ Failed to stop behavior tree {node_name}: {e}")
        
        # Cancel all running node tasks
        for node_name, task in self._node_tasks.items():
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                self._node_tasks[node_name] = None
        
        # Reset all task execution states
        for node_name in self._node_execution_states:
            self._node_execution_states[node_name] = False
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        
        # Emit forest stop event
        await self.forest_event_system.emit(
            "forest_stopped",
            source=self.name
        )
    
    async def _run(self) -> None:
        """Forest execution loop - monitors and coordinates behavior trees"""
        while self.running:
            try:
                # Collect status from all behavior trees (for monitoring and coordination)
                await self.tick()
                # Brief pause to prevent excessive CPU usage
                await asyncio.sleep(0.1)  # 100ms delay for monitoring
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Forest execution error: {e}")
                await asyncio.sleep(0.1)  # Brief pause on error
    
    def reset(self) -> None:
        """Reset all nodes in the forest and their behavior trees"""
        # Reset each node and its behavior tree
        for node_name, node in self.nodes.items():
            try:
                node.reset()
                print(f"🔄 Reset behavior tree: {node_name}")
            except Exception as e:
                print(f"❌ Failed to reset behavior tree {node_name}: {e}")
        
        # Cancel all running node tasks
        for node_name, task in self._node_tasks.items():
            if task and not task.done():
                task.cancel()
                self._node_tasks[node_name] = None
        
        # Reset all task execution states
        for node_name in self._node_execution_states:
            self._node_execution_states[node_name] = False
        
        # Reset all last execution times
        for node_name in self._node_last_execution:
            self._node_last_execution[node_name] = 0.0
        
        # Emit forest reset event
        asyncio.create_task(
            self.forest_event_system.emit(
                "forest_reset",
                source=self.name
            )
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get forest statistics
        
        Returns:
            Forest statistics dictionary
        """
        node_stats = {}
        for node_name, node in self.nodes.items():
            node_stats[node_name] = {
                "type": node.node_type.name,
                "status": node.status.name,
                "capabilities": list(node.capabilities),
                "dependencies": list(node.dependencies)
            }
        
        return {
            "name": self.name,
            "running": self.running,
            "total_nodes": len(self.nodes),
            "middleware_count": len(self.middleware),
            "node_stats": node_stats
        }
    
    def load_from_string(self, xml_string: str) -> None:
        """
        Load behavior forest configuration from XML string
        
        Args:
            xml_string: XML configuration string
            
        Raises:
            ValueError: If parsing fails or configuration is invalid
        """
        try:
            from ..parser.xml_parser import XMLParser
            parser = XMLParser()
            loaded_forest = parser.parse_string(xml_string)
            
            if not isinstance(loaded_forest, BehaviorForest):
                raise ValueError("XML string does not contain a valid behavior forest configuration")
            
            # Copy forest properties
            self.name = loaded_forest.name
            self.nodes = loaded_forest.nodes
            self.middleware = loaded_forest.middleware
            self.forest_blackboard = loaded_forest.forest_blackboard
            self.forest_event_system = loaded_forest.forest_event_system
            
        except Exception as e:
            raise ValueError(f"Failed to load forest from XML string: {e}")
    
    def load_from_file(self, file_path: str) -> None:
        """
        Load behavior forest configuration from XML file
        
        Args:
            file_path: Path to XML configuration file
            
        Raises:
            ValueError: If parsing fails or configuration is invalid
            FileNotFoundError: If file does not exist
        """
        try:
            from ..parser.xml_parser import XMLParser
            parser = XMLParser()
            loaded_forest = parser.parse_file(file_path)
            
            if not isinstance(loaded_forest, BehaviorForest):
                raise ValueError("XML file does not contain a valid behavior forest configuration")
            
            # Copy forest properties
            self.name = loaded_forest.name
            self.nodes = loaded_forest.nodes
            self.middleware = loaded_forest.middleware
            self.forest_blackboard = loaded_forest.forest_blackboard
            self.forest_event_system = loaded_forest.forest_event_system
            
        except FileNotFoundError as e:
            raise FileNotFoundError(f"XML configuration file not found: {file_path}")
        except Exception as e:
            raise ValueError(f"Failed to load forest from XML file: {e}")
    
    def __repr__(self) -> str:
        stats = self.get_stats()
        return f"BehaviorForest(name='{self.name}', nodes={stats['total_nodes']}, running={self.running})" 