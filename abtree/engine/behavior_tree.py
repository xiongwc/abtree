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
    ):
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

    def load_from_root(self, root: BaseNode) -> None:
        """
        Load behavior tree from root node

        Args:
            root: Root node
        """
        self.root = root
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
        xml_tree = parser.parse_string(xml_string)
        
        # Copy XML parsing results
        self.root = xml_tree.root
        self.name = xml_tree.name
        self.description = xml_tree.description
        self.blackboard = xml_tree.blackboard
        self.event_system = xml_tree.event_system
        self.tick_manager = xml_tree.tick_manager

    def _init_from_xml_file(self, xml_file: str) -> None:
        """
        Initialize from XML file

        Args:
            xml_file: XML file path
        """
        from ..parser.xml_parser import XMLParser
        
        parser = XMLParser()
        # Pass the blackboard to the parser for object resolution
        xml_tree = parser.parse_file(xml_file, self.blackboard)
        
        # Copy XML parsing results
        self.root = xml_tree.root
        self.name = xml_tree.name
        self.description = xml_tree.description
        self.blackboard = xml_tree.blackboard
        self.event_system = xml_tree.event_system
        self.tick_manager = xml_tree.tick_manager

    def _init_default_components(self) -> None:
        """Initialize default components"""
        if self.blackboard is None:
            self.blackboard = Blackboard()

        if self.event_system is None:
            self.event_system = EventSystem()

        if self.tick_manager is None:
            self.tick_manager = TickManager(
                root_node=self.root, blackboard=self.blackboard
            )
        else:
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
                {"tree_name": self.name, "timestamp": asyncio.get_event_loop().time()},
            )

        # Execute tick
        status = await self.tick_manager.tick_once()

        # Emit tick end event
        if self.event_system:
            await self.event_system.emit(
                "tree_tick_end",
                {
                    "tree_name": self.name,
                    "status": status.name,
                    "timestamp": asyncio.get_event_loop().time(),
                },
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
                {"tree_name": self.name, "tick_rate": self.tick_manager.tick_rate},
            )

    async def stop(self) -> None:
        """Stop behavior tree automatic execution"""
        if self.tick_manager is None:
            return

        await self.tick_manager.stop()

        # Emit stop event
        if self.event_system:
            await self.event_system.emit("tree_stopped", {"tree_name": self.name})

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
            asyncio.create_task(
                self.event_system.emit("tree_reset", {"tree_name": self.name})
            )

    def set_root(self, root: BaseNode) -> None:
        """
        Set root node

        Args:
            root: New root node
        """
        self.root = root

        if self.tick_manager:
            self.tick_manager.set_root_node(root)

        # Emit root node change event
        if self.event_system:
            asyncio.create_task(
                self.event_system.emit(
                    "tree_root_changed", {"tree_name": self.name, "new_root": root.name}
                )
            )

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
            stats["node_types"][node_type] = stats["node_types"].get(node_type, 0) + 1

            # Count status distribution
            status_name = node.status.name
            stats["status_distribution"][status_name] += 1

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
            asyncio.create_task(
                self.event_system.emit(
                    "tree_status_changed",
                    {
                        "tree_name": self.name,
                        "old_status": old_status.name,
                        "new_status": new_status.name,
                        "timestamp": asyncio.get_event_loop().time(),
                    },
                )
            )

    def set_blackboard_data(self, key: str, value: Any) -> None:
        """
        Set blackboard data

        Args:
            key: Data key
            value: Data value
        """
        if self.blackboard:
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

    def subscribe_event(self, event_name: str, callback: Any) -> None:
        """
        Subscribe to event

        Args:
            event_name: Event name
            callback: Callback function
        """
        if self.event_system:
            self.event_system.on(event_name, callback)

    def unsubscribe_event(self, event_name: str, callback: Any) -> None:
        """
        Unsubscribe from event

        Args:
            event_name: Event name
            callback: Callback function
        """
        if self.event_system:
            self.event_system.off(event_name, callback)

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop()

    def __repr__(self) -> str:
        """String representation of the behavior tree"""
        stats = self.get_tree_stats()
        return f"BehaviorTree(name='{self.name}', nodes={stats['total_nodes']}, running={stats.get('running', False)})"
