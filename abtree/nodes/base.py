"""
Base node class - Base class for behavior tree nodes

Defines the common interface and basic functionality for all behavior tree nodes,
including node execution, child node management, status management, etc.
"""

import asyncio
import inspect
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
        blackboard: Reference to the behavior tree's blackboard system
    """

    def __init__(self, name: str = "", children: Optional[List["BaseNode"]] = None, **kwargs):
        # Automatically call parent's __init__ if it exists and is not object.__init__
        try:
            super().__init__(**kwargs)
        except TypeError:
            # If parent doesn't have __init__ or doesn't accept arguments, ignore
            pass
            
        # Only initialize base attributes if they haven't been set by dataclass
        if not hasattr(self, 'name'):
            self.name = name
        if not hasattr(self, 'children'):
            self.children = children or []
        if not hasattr(self, 'parent'):
            self.parent = None
        if not hasattr(self, 'status'):
            self.status = Status.FAILURE
        if not hasattr(self, '_last_tick_time'):
            self._last_tick_time = 0.0
        if not hasattr(self, '_param_mappings'):
            self._param_mappings: Dict[str, str] = {}
        if not hasattr(self, 'blackboard'):
            self.blackboard: Optional[Blackboard] = None
        
        # Set parent node reference for child nodes after initialization
        for child in self.children:
            child.parent = self

    def __post_init__(self) -> None:
        """Post-initialization hook for dataclass inheritance"""
        # This method is called by dataclass after __init__
        # It can be overridden by subclasses for additional initialization
        pass

    def set_blackboard(self, blackboard: Blackboard) -> None:
        """
        Set the blackboard reference for this node and all its descendants
        
        Args:
            blackboard: Blackboard system to set
        """
        self.blackboard = blackboard
        # Recursively set blackboard for all child nodes
        for child in self.children:
            child.set_blackboard(blackboard)

    def get_blackboard(self) -> Optional[Blackboard]:
        """
        Get the blackboard reference
        
        Returns:
            Blackboard system or None if not set
        """
        return self.blackboard

    def get_event_dispatcher(self):
        """
        Get the event dispatcher from blackboard
        
        Returns:
            EventDispatcher instance or None if not found
        """
        if self.blackboard is not None:
            return self.blackboard.get("__event_dispatcher")
        return None

    def set_param_mapping(self, node_attr: str, blackboard_key: str) -> None:
        """
        Set parameter mapping relationship
        
        Args:
            node_attr: Node member variable name
            blackboard_key: Key name in blackboard
        """
        self._param_mappings[node_attr] = blackboard_key

    def get_mapped_value(self, attr_name: str, default: Any = None) -> Any:
        """
        Get mapped value, prioritize from blackboard, if not set then use default value
        
        Args:
            attr_name: Node member variable name
            default: Default value
            
        Returns:
            Mapped value
        """
        if attr_name in self._param_mappings and self.blackboard is not None:
            blackboard_key = self._param_mappings[attr_name]
            # Get value from blackboard, if not set then use default value
            value = self.blackboard.get(blackboard_key, default)
            return value
        return getattr(self, attr_name, default)

    def set_mapped_value(self, attr_name: str, value: Any) -> None:
        """
        Set mapped value, update blackboard and internal attributes
        
        Args:
            attr_name: Node member variable name
            value: Value to set
        """
        if attr_name in self._param_mappings and self.blackboard is not None:
            blackboard_key = self._param_mappings[attr_name]
            # Update blackboard
            self.blackboard.set(blackboard_key, value)

    def get_param_mappings(self) -> Dict[str, str]:
        """
        Get parameter mapping table
        
        Returns:
            Parameter mapping table
        """
        return self._param_mappings.copy()

    def getPort(self, variable_name: str) -> Any:
        """
        Get value from mapped port using variable name
        
        Args:
            variable_name: Name of the variable to get from blackboard
            
        Returns:
            Value from blackboard or None if not found
        """
        if variable_name in self._param_mappings:
            mapped_value = self.get_mapped_value(variable_name)
            return mapped_value
        else:
            # If not found, raise an error
            raise ValueError(f"Variable '{variable_name}' is not mapped to blackboard")

    def setPort(self, variable_name: str, value: Any) -> None:
        """
        Set value to mapped port using variable name
        
        Args:
            variable_name: Name of the variable to set
            value: Value to set
        """
        if variable_name in self._param_mappings:
            self.set_mapped_value(variable_name, value)
        else:
            # If not found, raise an error
            raise ValueError(f"Variable '{variable_name}' is not mapped to blackboard")

    @abstractmethod
    async def tick(self) -> Status:
        """
        Execute node logic

        This is the core method of the node, which every node must implement.

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
        # Propagate blackboard to new child
        if self.blackboard is not None:
            child.set_blackboard(self.blackboard)

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
        Find node with specified name in the subtree

        Args:
            name: Node name to find

        Returns:
            Found node or None if not found
        """
        if self.name == name:
            return self
        
        for child in self.children:
            found = child.find_node_by_name(name)
            if found:
                return found
        
        return None

    def find_node(self, name: str) -> Optional["BaseNode"]:
        """
        Find node with specified name in the subtree (alias for find_node_by_name)

        Args:
            name: Node name to find

        Returns:
            Found node or None if not found
        """
        return self.find_node_by_name(name)

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
