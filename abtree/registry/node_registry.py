"""
Node Registry - Node Type Registration and Management

Provides functions for registering, looking up, and creating node types,
supports dynamic extension of custom node types.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Type

from ..nodes.base import BaseNode


@dataclass
class NodeRegistry:
    """
    Node Registry

    Manages all registered node types, provides node registration,
    lookup, and creation functions.
    """

    _registered_nodes: Dict[str, Type[BaseNode]] = field(default_factory=dict)
    _node_metadata: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    _builtin_nodes: set = field(default_factory=set)

    def register(
        self,
        name: str,
        node_class: Type[BaseNode],
        metadata: Optional[Dict[str, Any]] = None,
        is_builtin: bool = False,
    ) -> None:
        """
        Register node type

        Args:
            name: node type name
            node_class: node class
            metadata: node metadata
            is_builtin: whether this is a built-in node
        """
        if not issubclass(node_class, BaseNode):
            raise ValueError(f"Node class {node_class} must inherit from BaseNode")

        self._registered_nodes[name] = node_class

        # Store metadata
        if metadata is None:
            metadata = {}

        # Add default metadata
        metadata.setdefault("class_name", node_class.__name__)
        metadata.setdefault("module", node_class.__module__)
        metadata.setdefault("description", getattr(node_class, "__doc__", ""))

        self._node_metadata[name] = metadata
        
        # Mark as built-in if specified
        if is_builtin:
            self._builtin_nodes.add(name)

    def unregister(self, name: str) -> bool:
        """
        Unregister node type

        Args:
            name: node type name

        Returns:
            Return True if found and removed, otherwise return False
        """
        if name in self._registered_nodes:
            del self._registered_nodes[name]
            if name in self._node_metadata:
                del self._node_metadata[name]
            if name in self._builtin_nodes:
                self._builtin_nodes.remove(name)
            return True
        return False

    def create(self, node_type: str, **kwargs: Any) -> Optional[BaseNode]:
        """
        Create node instance

        Args:
            node_type: node type name
            **kwargs: node constructor parameters

        Returns:
            Node instance, return None if type does not exist
        """
        if node_type not in self._registered_nodes:
            return None

        node_class = self._registered_nodes[node_type]
        try:
            return node_class(**kwargs)
        except Exception as e:
            print(f"Failed to create node '{node_type}': {e}")
            return None

    def get_registered(self) -> List[str]:
        """
        Get all registered node type names

        Returns:
            List of node type names
        """
        return list(self._registered_nodes.keys())

    def is_registered(self, name: str) -> bool:
        """
        Check if node type is registered

        Args:
            name: node type name

        Returns:
            Return True if registered, otherwise return False
        """
        return name in self._registered_nodes

    def get_node_class(self, name: str) -> Optional[Type[BaseNode]]:
        """
        Get node class

        Args:
            name: node type name

        Returns:
            Node class, return None if not exist
        """
        return self._registered_nodes.get(name)

    def get_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get node metadata

        Args:
            name: node type name

        Returns:
            Node metadata, return None if not exist
        """
        return self._node_metadata.get(name)

    def get_all_metadata(self) -> Dict[str, Dict[str, Any]]:
        """
        Get metadata of all nodes

        Returns:
            Dictionary of all node metadata
        """
        return self._node_metadata.copy()

    def clear(self) -> None:
        """Clear all registered node types"""
        self._registered_nodes.clear()
        self._node_metadata.clear()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get registry statistics

        Returns:
            Statistics dictionary
        """
        return {
            "total_registered": len(self._registered_nodes),
            "registered_types": list(self._registered_nodes.keys()),
            "has_metadata": len(self._node_metadata) > 0,
        }

    def get_builtin_nodes(self) -> List[str]:
        """
        Get list of built-in node types

        Returns:
            List of built-in node type names
        """
        return list(self._builtin_nodes)

    def get_custom_nodes(self) -> List[str]:
        """
        Get list of custom (non-builtin) node types

        Returns:
            List of custom node type names
        """
        all_nodes = set(self._registered_nodes.keys())
        builtin_nodes = set(self._builtin_nodes)
        
        # Return custom nodes (all registered nodes minus built-in nodes)
        return list(all_nodes - builtin_nodes)

    def __contains__(self, name: str) -> bool:
        """Check if node type is registered"""
        return name in self._registered_nodes

    def __len__(self) -> int:
        """Return the number of registered node types"""
        return len(self._registered_nodes)

    def __repr__(self) -> str:
        """String representation of the registry"""
        stats = self.get_stats()
        return f"NodeRegistry(types={stats['total_registered']})"


# Global node registry instance
_global_registry = NodeRegistry()


def get_global_registry() -> NodeRegistry:
    """
    Get global node registry

    Returns:
        Global node registry instance
    """
    return _global_registry


def register_node(
    name: str, node_class: Type[BaseNode], metadata: Optional[Dict[str, Any]] = None, is_builtin: bool = False
) -> None:
    """
    Register node type to global registry

    Args:
        name: node type name
        node_class: node class
        metadata: node metadata
        is_builtin: whether this is a built-in node
    """
    _global_registry.register(name, node_class, metadata, is_builtin)


def create_node(node_type: str, **kwargs: Any) -> Optional[BaseNode]:
    """
    Create node instance from global registry

    Args:
        node_type: node type name
        **kwargs: node constructor parameters

    Returns:
        Node instance, return None if type does not exist
    """
    return _global_registry.create(node_type, **kwargs)


def get_registered_nodes() -> List[str]:
    """
    Get all registered node type names from global registry

    Returns:
        List of node type names
    """
    return _global_registry.get_registered()


def is_node_registered(name: str) -> bool:
    """
    Check if node type is registered in global registry

    Args:
        name: node type name

    Returns:
        Return True if registered, otherwise return False
    """
    return _global_registry.is_registered(name)


def get_builtin_nodes() -> List[str]:
    """
    Get list of built-in node types from global registry

    Returns:
        List of built-in node type names
    """
    return _global_registry.get_builtin_nodes()


def get_custom_nodes() -> List[str]:
    """
    Get list of custom (non-builtin) node types from global registry

    Returns:
        List of custom node type names
    """
    return _global_registry.get_custom_nodes()


def unregister_node(name: str) -> bool:
    """
    Unregister node type from global registry

    Args:
        name: node type name

    Returns:
        Return True if found and removed, otherwise return False
    """
    return _global_registry.unregister(name)


def get_node_class(name: str) -> Optional[Type[BaseNode]]:
    """
    Get node class by name from global registry

    Args:
        name: node type name

    Returns:
        Node class if found, None otherwise
    """
    return _global_registry.get_node_class(name)
