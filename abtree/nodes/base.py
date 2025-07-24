"""
Base node class - Base class for behavior tree nodes

Defines the common interface and basic functionality for all behavior tree nodes,
including node execution, child node management, status management, etc.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from ..core.status import Status
from ..engine.blackboard import Blackboard


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
        _param_mappings: Parameter mapping table, storing the mapping of node member variable names to blackboard key names
    """

    def __init__(self, name: str, children: Optional[List["BaseNode"]] = None):
        self.name = name
        self.children = children or []
        self.parent = None
        self.status = Status.FAILURE
        self._last_tick_time = 0.0
        self._param_mappings = {}
        
        # Set parent node reference for child nodes after initialization
        for child in self.children:
            child.parent = self

    def set_param_mapping(self, node_attr: str, blackboard_key: str) -> None:
        """
        Set parameter mapping relationship
        
        Args:
            node_attr: Node member variable name
            blackboard_key: Key name in blackboard
        """
        self._param_mappings[node_attr] = blackboard_key

    def get_mapped_value(self, attr_name: str, blackboard: Blackboard, default: Any = None) -> Any:
        """
        Get mapped value, prioritize from blackboard, if not set then use default value
        
        Args:
            attr_name: Node member variable name
            blackboard: Blackboard system
            default: Default value
            
        Returns:
            Mapped value
        """
        if attr_name in self._param_mappings:
            blackboard_key = self._param_mappings[attr_name]
            # Get value from blackboard, if not set then use default value
            value = blackboard.get(blackboard_key, default)
            return value
        return getattr(self, attr_name, default)

    def set_mapped_value(self, attr_name: str, value: Any, blackboard: Blackboard) -> None:
        """
        Set mapped value, update blackboard and internal attributes
        
        Args:
            attr_name: Node member variable name
            value: Value to set
            blackboard: Blackboard system
        """
        if attr_name in self._param_mappings:
            blackboard_key = self._param_mappings[attr_name]
            # Update blackboard
            blackboard.set(blackboard_key, value)
            # Update internal attributes
            setattr(self, attr_name, value)
        else:
            # If there is no mapping, only update internal attributes
            setattr(self, attr_name, value)

    def get_param_mappings(self) -> Dict[str, str]:
        """
        Get parameter mapping table
        
        Returns:
            Parameter mapping table
        """
        return self._param_mappings.copy()

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

    def add_child(self, child: "BaseNode") -> None:
        """
        Add child node

        Args:
            child: child node
        """
        self.children.append(child)
        child.parent = self

    def remove_child(self, child: "BaseNode") -> bool:
        """
        Remove child node

        Args:
            child: child node to remove

        Returns:
            True if the child node is found and removed, False otherwise
        """
        if child in self.children:
            self.children.remove(child)
            child.parent = None
            return True
        return False

    def get_child(self, index: int) -> Optional["BaseNode"]:
        """
        Get child node by index

        Args:
            index: child node index

        Returns:
            child node or None if index is out of range
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
        Check if there are child nodes

        Returns:
            True if there are child nodes, False otherwise
        """
        return len(self.children) > 0

    def get_depth(self) -> int:
        """
        Get node depth in the tree

        Returns:
            Node depth (0 for root node)
        """
        if self.parent is None:
            return 0
        return self.parent.get_depth() + 1

    def get_ancestors(self) -> List["BaseNode"]:
        """
        Get all ancestor nodes

        Returns:
            List of ancestor nodes (from root to parent)
        """
        if self.parent is None:
            return []
        return self.parent.get_ancestors() + [self.parent]

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

    def find_node_by_name(self, name: str) -> Optional["BaseNode"]:
        """
        Find node by name in the subtree

        Args:
            name: Node name to find

        Returns:
            Found node or None
        """
        if self.name == name:
            return self
        
        for child in self.children:
            found = child.find_node_by_name(name)
            if found:
                return found
        
        return None

    def reset(self) -> None:
        """Reset node status"""
        self.status = Status.FAILURE
        self._last_tick_time = 0.0
        
        # Reset all child nodes
        for child in self.children:
            child.reset()

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
