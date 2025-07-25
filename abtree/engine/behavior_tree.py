"""
Behavior tree main class - Integrates all core components

Behavior tree is the core class of the framework, integrating node system, blackboard system,
event system and Tick manager, providing complete behavior tree functionality.
"""

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

from ..core.status import Status
from ..nodes.base import BaseNode
from .blackboard import Blackboard
from .event_system import EventSystem
from .tick_manager import TickManager


@dataclass
class BehaviorTree:
    """
    Behavior tree main class

    Integrates node system, blackboard system, event system and Tick manager,
    providing complete behavior tree functionality.

    Attributes:
        root: Root node
        blackboard: Blackboard system
        event_system: Event system
        tick_manager: Tick manager
        name: Behavior tree name
        description: Behavior tree description
    """

    root: Optional[BaseNode] = field(default=None, init=False)
    blackboard: Optional[Blackboard] = None
    event_system: Optional[EventSystem] = None
    tick_manager: Optional[TickManager] = None
    name: str = "BehaviorTree"
    description: str = ""

    def __init__(
        self,
        blackboard: Optional[Blackboard] = None,
        event_system: Optional[EventSystem] = None,
        tick_manager: Optional[TickManager] = None,
        name: str = "BehaviorTree",
        description: str = "",
    ) -> None:
        """
        Initialize behavior tree

        Args:
            blackboard: Blackboard system
            event_system: Event system
            tick_manager: Tick manager
            name: Behavior tree name
            description: Behavior tree description
        """
        # Set basic attributes
        self.name = name
        self.description = description
        self.blackboard = blackboard
        self.event_system = event_system
        self.tick_manager = tick_manager
        self.root = None

        # Initialize default components
        self._init_default_components()

    def load_from_string(self, xml_text: str) -> None:
        """
        Load behavior tree from XML text

        Args:
            xml_text: XML text string
        """
        self._init_from_xml_string(xml_text)
        self._init_default_components()

    def load_from_file(self, xml_file: str) -> None:
        """
        Load behavior tree from XML file

        Args:
            xml_file: XML file path
        """
        self._init_from_xml_file(xml_file)
        self._init_default_components()

    def load_from_node(self, root: BaseNode) -> None:
        """
        Load behavior tree from root node

        Args:
            root: Root node
        """
        self.root = root
        # Set blackboard on the root node and all its descendants
        if self.blackboard is not None:
            self.root.set_blackboard(self.blackboard)
        if self.tick_manager:
            self.tick_manager.set_root_node(root)

    def _init_from_xml_string(self, xml_string: str) -> None:
        """
        Initialize from XML string

        Args:
            xml_string: XML string
        """
        from ..parser.xml_parser import XMLParser
        
        parser = XMLParser()
        # Pass the blackboard to the parser for object resolution
        xml_result = parser.parse_string(xml_string)
        
        # Only handle BehaviorTree, not BehaviorForest
        if hasattr(xml_result, 'root') and hasattr(xml_result, 'name'):
            # Copy XML parsing results
            self.root = xml_result.root
            self.name = xml_result.name
            if hasattr(xml_result, 'description'):
                self.description = xml_result.description
            if hasattr(xml_result, 'blackboard'):
                self.blackboard = xml_result.blackboard
            if hasattr(xml_result, 'event_system'):
                self.event_system = xml_result.event_system
            if hasattr(xml_result, 'tick_manager'):
                self.tick_manager = xml_result.tick_manager
            
            # Store event_system in blackboard if available
            if self.event_system is not None and self.blackboard is not None:
                self.blackboard.set("__event_system", self.event_system)

    def _init_from_xml_file(self, xml_file: str) -> None:
        """
        Initialize from XML file

        Args:
            xml_file: XML file path
        """
        from ..parser.xml_parser import XMLParser
        
        parser = XMLParser()
        # Pass the blackboard to the parser for object resolution
        xml_result = parser.parse_file(xml_file)
        
        # Only handle BehaviorTree, not BehaviorForest
        if hasattr(xml_result, 'root') and hasattr(xml_result, 'name'):
            # Copy XML parsing results
            self.root = xml_result.root
            self.name = xml_result.name
            if hasattr(xml_result, 'description'):
                self.description = xml_result.description
            if hasattr(xml_result, 'blackboard'):
                self.blackboard = xml_result.blackboard
            if hasattr(xml_result, 'event_system'):
                self.event_system = xml_result.event_system
            if hasattr(xml_result, 'tick_manager'):
                self.tick_manager = xml_result.tick_manager
            
            # Store event_system in blackboard if available
            if self.event_system is not None and self.blackboard is not None:
                self.blackboard.set("__event_system", self.event_system)

    def _init_default_components(self) -> None:
        """Initialize default components"""
        if self.blackboard is None:
            self.blackboard = Blackboard()

        if self.event_system is None:
            self.event_system = EventSystem()

        # Store event_system in blackboard
        if self.event_system is not None and hasattr(self.blackboard, 'set'):
            self.blackboard.set("__event_system", self.event_system)

        if self.tick_manager is None:
            self.tick_manager = TickManager(
                root_node=self.root, blackboard=self.blackboard
            )
        else:
            if self.root is not None:
                self.tick_manager.set_root_node(self.root)
            self.tick_manager.set_blackboard(self.blackboard)

    async def tick(self) -> Status:
        """
        Execute one behavior tree tick

        Returns:
            Execution result status
        """
        if self.tick_manager is None:
            raise ValueError("Tick manager not initialized")

        # Emit tick start event
        if self.event_system:
            await self.event_system.emit(
                "tree_tick_start",
                source=self.name
            )

        # Execute tick
        status = await self.tick_manager.tick_once()

        # Emit tick end event
        if self.event_system:
            await self.event_system.emit(
                "tree_tick_end",
                source=self.name
            )

        return status

    async def start(self, tick_rate: Optional[float] = None) -> None:
        """
        Start behavior tree automatic execution

        Args:
            tick_rate: Execution frequency, if None use default value
        """
        if self.tick_manager is None:
            raise ValueError("Tick manager not initialized")

        if tick_rate is not None:
            self.tick_manager.set_tick_rate(tick_rate)

        # Set status change callback
        self.tick_manager.set_on_status_change_callback(self._on_status_change)

        # Start tick manager
        await self.tick_manager.start()

        # Emit start event
        if self.event_system:
            await self.event_system.emit(
                "tree_started",
                source=self.name
            )

    async def stop(self) -> None:
        """Stop behavior tree automatic execution"""
        if self.tick_manager is None:
            return

        await self.tick_manager.stop()

        # Emit stop event
        if self.event_system:
            await self.event_system.emit("tree_stopped", source=self.name)

    def reset(self) -> None:
        """Reset behavior tree status"""
        if self.root:
            self.root.reset()

        if self.blackboard:
            self.blackboard.clear()

        if self.tick_manager:
            self.tick_manager.reset_stats()

        # Emit reset event
        if self.event_system:
            try:
                loop = asyncio.get_running_loop()
                asyncio.create_task(
                    self.event_system.emit("tree_reset", source=self.name)
                )
            except RuntimeError:
                # No running event loop, skip event emission
                pass

    def set_root(self, root: BaseNode) -> None:
        """
        Set root node

        Args:
            root: New root node
        """
        self.root = root
        # Set blackboard on the root node and all its descendants
        if self.blackboard is not None:
            self.root.set_blackboard(self.blackboard)

        if self.tick_manager:
            self.tick_manager.set_root_node(root)

        # Emit root node change event
        if self.event_system:
            try:
                loop = asyncio.get_running_loop()
                asyncio.create_task(
                    self.event_system.emit(
                        "tree_root_changed", source=self.name
                    )
                )
            except RuntimeError:
                # No running event loop, skip event emission
                pass

    def find_node(self, name: str) -> Optional[BaseNode]:
        """
        Find node with specified name

        Args:
            name: Node name

        Returns:
            Found node, or None if not found
        """
        if self.root:
            return self.root.find_node(name)
        return None

    def get_all_nodes(self) -> List[BaseNode]:
        """
        Get all nodes in the behavior tree

        Returns:
            List of nodes
        """
        if not self.root:
            return []

        nodes = [self.root]
        nodes.extend(self.root.get_descendants())
        return nodes

    def get_node_stats(self) -> Dict[str, Any]:
        """
        Get node statistics

        Returns:
            Statistics dictionary
        """
        nodes = self.get_all_nodes()

        stats = {
            "total_nodes": len(nodes),
            "node_types": {},
            "status_distribution": {
                Status.SUCCESS.name: 0,
                Status.FAILURE.name: 0,
                Status.RUNNING.name: 0,
            },
        }

        for node in nodes:
            # Count node types
            node_type = node.__class__.__name__
            node_types = stats["node_types"]
            if isinstance(node_types, dict):
                node_types[node_type] = node_types.get(node_type, 0) + 1

            # Count status distribution
            status_name = node.status.name
            status_distribution = stats["status_distribution"]
            if isinstance(status_distribution, dict):
                status_distribution[status_name] += 1

        return stats

    def get_tree_stats(self) -> Dict[str, Any]:
        """
        Get behavior tree statistics

        Returns:
            Statistics dictionary
        """
        stats = {
            "name": self.name,
            "description": self.description,
            "has_root": self.root is not None,
            "has_blackboard": self.blackboard is not None,
            "has_event_system": self.event_system is not None,
            "has_tick_manager": self.tick_manager is not None,
        }

        if self.tick_manager:
            stats.update(self.tick_manager.get_stats())

        if self.event_system:
            stats.update(self.event_system.get_stats())

        stats.update(self.get_node_stats())

        return stats

    def _on_status_change(self, old_status: Status, new_status: Status) -> None:
        """
        Status change callback function

        Args:
            old_status: Old status
            new_status: New status
        """
        if self.event_system:
            try:
                loop = asyncio.get_running_loop()
                asyncio.create_task(
                    self.event_system.emit(
                        "tree_status_changed",
                        source=self.name
                    )
                )
            except RuntimeError:
                # No running event loop, skip event emission
                pass

    def set_blackboard_data(self, key: str, value: Any) -> None:
        """
        Set blackboard data

        Args:
            key: Data key
            value: Data value
        """
        if self.blackboard is not None:
            self.blackboard.set(key, value)

    def get_blackboard_data(self, key: str, default: Any = None) -> Any:
        """
        Get blackboard data

        Args:
            key: Data key
            default: Default value

        Returns:
            Blackboard data
        """
        if self.blackboard:
            return self.blackboard.get(key, default)
        return default

    def get_event_system_from_blackboard(self) -> Optional[EventSystem]:
        """
        Get event system from blackboard

        Returns:
            Event system instance or None if not found
        """
        if self.blackboard:
            event_system = self.blackboard.get("__event_system")
            if isinstance(event_system, EventSystem):
                return event_system
        return None

    def set_event_system_to_blackboard(self, event_system: EventSystem) -> None:
        """
        Store event system to blackboard

        Args:
            event_system: Event system to store
        """
        if self.blackboard:
            self.blackboard.set("__event_system", event_system)

    def subscribe_event(self, event_name: str, callback: Any) -> None:
        """
        Subscribe to event (deprecated - use wait_for instead)

        Args:
            event_name: Event name
            callback: Callback function
        """
        # Note: This method is deprecated in the new event system
        # Use event_system.wait_for() instead
        pass

    def unsubscribe_event(self, event_name: str, callback: Any) -> None:
        """
        Unsubscribe from event (deprecated - use clear_event instead)

        Args:
            event_name: Event name
            callback: Callback function
        """
        # Note: This method is deprecated in the new event system
        # Use event_system.clear_event() instead
        pass

    async def __aenter__(self) -> "BehaviorTree":
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit"""
        await self.stop()

    def __repr__(self) -> str:
        """String representation of the behavior tree"""
        stats = self.get_tree_stats()
        return f"BehaviorTree(name='{self.name}', nodes={stats['total_nodes']}, running={stats.get('running', False)})"
