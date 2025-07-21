"""
ABTree - Asynchronous Behavior Tree Framework

A modern, modular, and easy-to-integrate Python asynchronous behavior tree framework,
designed for agent-based systems, game AI, robotics, and other scenarios.
"""

from typing import Any, Optional, Union

from .core.status import Policy, Status
from .engine import BehaviorTree, Blackboard, EventSystem, TickManager
from .forest import (
    BehaviorForest,
    ForestConfig,
    ForestConfigPresets,
    ForestManager,
    ForestNode,
    ForestNodeType,
)
from .forest.middleware import (
    BehaviorCallMiddleware,
    PubSubMiddleware,
    ReqRespMiddleware,
    SharedBlackboardMiddleware,
    StateWatchingMiddleware,
    TaskBoardMiddleware,
)
from .nodes import (
    Action,
    AlwaysFalse,
    AlwaysTrue,
    BaseNode,
    CheckBlackboard,
    Compare,
    Condition,
    Decorator,
    Inverter,
    IsFalse,
    IsTrue,
    Log,
    Parallel,
    Repeater,
    Selector,
    Sequence,
    SetBlackboard,
    UntilFailure,
    UntilSuccess,
    Wait,
)
from .parser.tree_builder import TreeBuilder
from .parser.xml_parser import XMLParser
from .registry.node_registry import (
    NodeRegistry,
    create_node,
    get_registered_nodes,
    register_node,
)


# Register all built-in node types
def _register_builtin_nodes() -> None:
    """Register all built-in node types"""
    from .nodes.action import Action, Log, SetBlackboard, Wait
    from .nodes.composite import Parallel, Selector, Sequence
    from .nodes.condition import (
        AlwaysFalse,
        AlwaysTrue,
        CheckBlackboard,
        Compare,
        Condition,
        IsFalse,
        IsTrue,
    )
    from .nodes.decorator import (
        Decorator,
        Inverter,
        Repeater,
        UntilFailure,
        UntilSuccess,
    )

    # Register composite nodes
    register_node("Sequence", Sequence)  
    register_node("Selector", Selector)  
    register_node("Parallel", Parallel) 

    # Register decorator nodes
    register_node("Inverter", Inverter)  
    register_node("Repeater", Repeater)  
    register_node("UntilSuccess", UntilSuccess)  
    register_node("UntilFailure", UntilFailure)  
    register_node("Decorator", Decorator) 

    # Register action nodes
    # register_node("Action", Action)  # Action is abstract, cannot be registered
    register_node("Wait", Wait)
    register_node("Log", Log)
    register_node("SetBlackboard", SetBlackboard)

    # Register condition nodes
    # register_node("Condition", Condition)  # Condition is abstract, cannot be registered
    register_node("CheckBlackboard", CheckBlackboard)
    register_node("IsTrue", IsTrue)
    register_node("IsFalse", IsFalse)
    register_node("Compare", Compare)
    register_node("AlwaysTrue", AlwaysTrue)
    register_node("AlwaysFalse", AlwaysFalse)


# Register nodes when the module is imported
_register_builtin_nodes()


def create_tree(
    root: Optional[Union[BaseNode, str]] = None,
    xml_string: Optional[str] = None,
    xml_file: Optional[str] = None,
    name: str = "BehaviorTree",
    description: str = "",
    **kwargs: Any
) -> BehaviorTree:
    """
    Create behavior tree with flexible initialization

    Args:
        root: Root node or XML string
        xml_string: XML string for initialization
        xml_file: XML file path for initialization
        name: Behavior tree name
        description: Behavior tree description
        **kwargs: Additional arguments for BehaviorTree

    Returns:
        Created behavior tree

    Raises:
        ValueError: When initialization parameters are invalid
    """
    tree = BehaviorTree(
        name=name,
        description=description,
        **kwargs
    )
    
    if root is not None:
        if isinstance(root, str):
            # If root is a string, treat it as XML string
            tree.load_from_string(root)
        else:
            # If root is a BaseNode, load it directly
            tree.load_from_node(root)
    elif xml_string is not None:
        tree.load_from_string(xml_string)
    elif xml_file is not None:
        tree.load_from_file(xml_file)
    
    return tree


def load_from_xml_string(xml_string: str) -> Union[BehaviorTree, BehaviorForest]:
    """
    Load behavior tree or forest from XML string

    Args:
        xml_string: XML string

    Returns:
        Loaded behavior tree or forest

    Raises:
        ValueError: When XML format error or parsing fails
    """
    parser = XMLParser()
    return parser.parse_string(xml_string)


def load_from_xml_file(file_path: str) -> Union[BehaviorTree, BehaviorForest]:
    """
    Load behavior tree or forest from XML file

    Args:
        file_path: XML file path

    Returns:
        Loaded behavior tree or forest

    Raises:
        ValueError: When file does not exist or XML format error
    """
    parser = XMLParser()
    return parser.parse_file(file_path)


def export_to_xml_string(tree: BehaviorTree) -> str:
    """
    Export behavior tree to XML string

    Args:
        tree: Behavior tree to export

    Returns:
        XML string
    """
    builder = TreeBuilder()
    return builder.export_to_xml(tree)


def export_to_xml_file(tree: BehaviorTree, file_path: str) -> str:
    """
    Export behavior tree to XML file

    Args:
        tree: Behavior tree to export
        file_path: Output file path

    Returns:
        XML string
    """
    builder = TreeBuilder()
    return builder.export_to_xml(tree, file_path)


__all__ = [
    # Core classes
    "BehaviorTree",
    "BaseNode",
    "Blackboard",
    "TickManager",
    "EventSystem",
    # Status and policy
    "Status",
    "Policy",
    # Composite nodes
    "Sequence",
    "Selector",
    "Parallel",
    # Decorator nodes
    "Inverter",
    "Repeater",
    "UntilSuccess",
    "UntilFailure",
    "Decorator",
    # Basic node types
    "Action",
    "Condition",
    "Wait",
    "Log",
    "SetBlackboard",
    "CheckBlackboard",
    "IsTrue",
    "IsFalse",
    "Compare",
    "AlwaysTrue",
    "AlwaysFalse",
    # Registration system
    "NodeRegistry",
    "register_node",
    "create_node",
    "get_registered_nodes",
    # XML parsing and exporting
    "XMLParser",
    "TreeBuilder",
    "create_tree",
    "load_from_xml_string",
    "load_from_xml_file",
    "export_to_xml_string",
    "export_to_xml_file",
    # Forest system
    "BehaviorForest",
    "ForestNode",
    "ForestNodeType",
    "ForestManager",
    "ForestConfig",
    "ForestConfigPresets",
    "PubSubMiddleware",
    "ReqRespMiddleware",
    "SharedBlackboardMiddleware",
    "StateWatchingMiddleware",
    "BehaviorCallMiddleware",
    "TaskBoardMiddleware",
]
