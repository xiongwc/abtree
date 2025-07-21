"""
Base node class - Base class for behavior tree nodes

Defines the common interface and basic functionality for all behavior tree nodes,
including node execution, child node management, status management, etc.
"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from ..core.status import Status
from ..engine.blackboard import Blackboard


@dataclass
class BaseNode(ABC):
    """
    Behavior tree node base class

    All behavior tree nodes inherit from this class, defining the basic interface and functionality of nodes.

    Attributes:
        name: Node name
        children: List of child nodes
        parent: Parent node
        status: Current execution status
        _last_tick_time: Last execution time
    """

    name: str
    children: List["BaseNode"] = field(default_factory=list)
    parent: Optional["BaseNode"] = None
    status: Status = Status.FAILURE
    _last_tick_time: float = field(default=0.0, init=False)

    def __post_init__(self):
        """Set parent node reference for child nodes after initialization"""
        for child in self.children:
            child.parent = self

    @abstractmethod
    async def tick(self, blackboard: Blackboard) -> Status:
        """
        Execute node logic

        This is the core method of the node, which every node must implement.

        Args:
            blackboard: Blackboard system for data sharing

        Returns:
            Execution status: SUCCESS, FAILURE or RUNNING
        """
        pass

    def reset(self) -> None:
        """
        Reset node status

        Reset the node status to initial state and recursively reset all child nodes.
        """
        self.status = Status.FAILURE
        self._last_tick_time = 0.0

        for child in self.children:
            child.reset()

    def add_child(self, child: "BaseNode") -> None:
        """
        Add child node

        Args:
            child: Child node to add
        """
        child.parent = self
        self.children.append(child)

    def remove_child(self, child: "BaseNode") -> bool:
        """
        Remove child node

        Args:
            child: Child node to remove

        Returns:
            True if child node is found and removed, False otherwise
        """
        if child in self.children:
            child.parent = None
            self.children.remove(child)
            return True
        return False

    def get_child(self, index: int) -> Optional["BaseNode"]:
        """
        Get child node at specified index

        Args:
            index: Child node index

        Returns:
            Child node, or None if index is invalid
        """
        if 0 <= index < len(self.children):
            return self.children[index]
        return None

    def get_child_count(self) -> int:
        """
        Get number of child nodes

        Returns:
            Number of child nodes
        """
        return len(self.children)

    def has_children(self) -> bool:
        """
        Check if node has children

        Returns:
            True if node has children, False otherwise
        """
        return len(self.children) > 0

    def get_root(self) -> "BaseNode":
        """
        Get root node

        Returns:
            Root node of the behavior tree
        """
        current = self
        while current.parent is not None:
            current = current.parent
        return current

    def get_depth(self) -> int:
        """
        Get node depth in the tree

        Returns:
            Node depth, root node is 0
        """
        depth = 0
        current = self
        while current.parent is not None:
            depth += 1
            current = current.parent
        return depth

    def get_path(self) -> List[str]:
        """
        Get path from root node to current node

        Returns:
            List of node names from root to current node
        """
        path = [self.name]
        current = self
        while current.parent is not None:
            current = current.parent
            path.insert(0, current.name)
        return path

    def find_node(self, name: str) -> Optional["BaseNode"]:
        """
        Find node with specified name in subtree

        Args:
            name: Name of node to find

        Returns:
            Found node, or None if not found
        """
        if self.name == name:
            return self

        for child in self.children:
            result = child.find_node(name)
            if result is not None:
                return result

        return None

    def get_descendants(self) -> List["BaseNode"]:
        """
        Get all descendant nodes

        Returns:
            List of descendant nodes
        """
        descendants = []
        for child in self.children:
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants

    def get_ancestors(self) -> List["BaseNode"]:
        """
        Get all ancestor nodes

        Returns:
            List of ancestor nodes
        """
        ancestors = []
        current = self.parent
        while current is not None:
            ancestors.append(current)
            current = current.parent
        return ancestors

    def is_running(self) -> bool:
        """
        Check if node is running

        Returns:
            True if node status is RUNNING, False otherwise
        """
        return self.status == Status.RUNNING

    def is_success(self) -> bool:
        """
        Check if node completed successfully

        Returns:
            True if node status is SUCCESS, False otherwise
        """
        return self.status == Status.SUCCESS

    def is_failure(self) -> bool:
        """
        Check if node execution failed

        Returns:
            True if node status is FAILURE, False otherwise
        """
        return self.status == Status.FAILURE

    def get_last_tick_time(self) -> float:
        """
        Get last execution time

        Returns:
            Timestamp of last execution
        """
        return self._last_tick_time

    def update_tick_time(self) -> None:
        """Update execution timestamp"""
        self._last_tick_time = asyncio.get_event_loop().time()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get node statistics

        Returns:
            Statistics dictionary
        """
        return {
            "name": self.name,
            "type": self.__class__.__name__,
            "status": self.status.name,
            "children_count": len(self.children),
            "depth": self.get_depth(),
            "last_tick_time": self._last_tick_time,
        }

    def __str__(self) -> str:
        """String representation of the node"""
        return f"{self.__class__.__name__}(name='{self.name}', status={self.status})"

    def __repr__(self) -> str:
        """Detailed string representation of the node"""
        return f"{self.__class__.__name__}(name='{self.name}', children={len(self.children)}, status={self.status})"
