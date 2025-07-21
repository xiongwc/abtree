"""
Validation Utilities - Behavior Tree and Node Validation Functions

Provides validation functions for behavior trees and nodes to ensure the correctness of data structures.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from ..core.base import BaseNode
from ..core.behavior_tree import BehaviorTree
from ..core.status import Status


@dataclass
class ValidationResult:
    """Validation result"""

    is_valid: bool
    errors: List[str]
    warnings: List[str]

    def __bool__(self) -> bool:
        return self.is_valid


def validate_tree(tree: BehaviorTree) -> ValidationResult:
    """
    Validate behavior tree

    Args:
        tree: Behavior tree to validate

    Returns:
        Validation result
    """
    errors = []
    warnings = []

    # Check behavior tree basic information
    if not tree.name:
        errors.append("Behavior tree name cannot be empty")

    if not tree.root:
        errors.append("Behavior tree must have a root node")
        return ValidationResult(False, errors, warnings)

    # Validate root node
    root_result = validate_node(tree.root)
    if not root_result.is_valid:
        errors.extend(root_result.errors)
    warnings.extend(root_result.warnings)

    # Check node count
    all_nodes = tree.get_all_nodes()
    if len(all_nodes) == 0:
        errors.append("Behavior tree cannot be empty")
    elif len(all_nodes) == 1:
        warnings.append("Behavior tree has only one node, which may be too simple")

    # Check node name uniqueness
    node_names = [node.name for node in all_nodes]
    duplicate_names = [name for name in set(node_names) if node_names.count(name) > 1]
    if duplicate_names:
        warnings.append(f"Duplicate node names: {duplicate_names}")

    # Check blackboard system
    if not tree.blackboard:
        warnings.append("Behavior tree has no blackboard system")

    # Check event system
    if not tree.event_system:
        warnings.append("Behavior tree has no event system")

    # Check Tick manager
    if not tree.tick_manager:
        warnings.append("Behavior tree has no Tick manager")

    is_valid = len(errors) == 0
    return ValidationResult(is_valid, errors, warnings)


def validate_node(node: BaseNode) -> ValidationResult:
    """
    Validate node

    Args:
        node: Node to validate

    Returns:
        Validation result
    """
    errors = []
    warnings = []

    # Check node name
    if not node.name:
        errors.append(f"Node name cannot be empty (type: {node.__class__.__name__})")

    # 检查节点类型
    if not isinstance(node, BaseNode):
        errors.append(f"Node must inherit from BaseNode (type: {type(node).__name__})")

    # 检查子节点
    for i, child in enumerate(node.children):
        if child is None:
            errors.append(f"Node '{node.name}' has a None child at position {i+1}")
        else:
            child_result = validate_node(child)
            if not child_result.is_valid:
                errors.extend(child_result.errors)
            warnings.extend(child_result.warnings)

    # Check node specific properties
    node_specific_errors = _validate_node_specific(node)
    errors.extend(node_specific_errors)

    # Check node status
    if node.status not in Status:
        warnings.append(f"Node '{node.name}' has an invalid status: {node.status}")

    is_valid = len(errors) == 0
    return ValidationResult(is_valid, errors, warnings)


def _validate_node_specific(node: BaseNode) -> List[str]:
    """
    Validate node specific properties

    Args:
        node: Node to validate

    Returns:
        List of errors
    """
    errors = []

    # Check action node
    if hasattr(node, "execute"):
        if not callable(getattr(node, "execute")):
            errors.append(f"Action node '{node.name}' has an uncallable execute method")

    # Check condition node
    if hasattr(node, "evaluate"):
        if not callable(getattr(node, "evaluate")):
            errors.append(f"Condition node '{node.name}' has an uncallable evaluate method")

    # Check decorator node
    if hasattr(node, "child"):
        if node.child is None and len(node.children) == 0:
            errors.append(f"Decorator node '{node.name}' has no children")

    # Check composite node
    if hasattr(node, "children"):
        if len(node.children) == 0:
            errors.append(f"Composite node '{node.name}' has no children")

    # Check specific node type properties
    if hasattr(node, "duration"):
        if getattr(node, "duration", 0) < 0:
            errors.append(f"Node '{node.name}' has a negative duration")

    if hasattr(node, "repeat_count"):
        repeat_count = getattr(node, "repeat_count", 0)
        if repeat_count < -1:
            errors.append(f"Node '{node.name}' has a repeat_count less than -1")

    if hasattr(node, "policy"):
        policy = getattr(node, "policy", None)
        if (
            policy is not None
            and policy not in Status.__class__.__bases__[0].__subclasses__()
        ):
            errors.append(f"Node '{node.name}' has an invalid policy")

    return errors


def validate_blackboard_data(data: Dict[str, Any]) -> ValidationResult:
    """
    Validate blackboard data

    Args:
        data: Blackboard data

    Returns:
        Validation result
    """
    errors = []
    warnings = []

    # Check data type
    for key, value in data.items():
        if not isinstance(key, str):
            errors.append(f"Blackboard key must be a string, found: {type(key).__name__}")

        # Check special values
        if value is None:
            warnings.append(f"Blackboard key '{key}' has a None value")

    # Check key name format
    for key in data.keys():
        if not key or key.strip() == "":
            errors.append("Blackboard key cannot be empty")
        elif key.startswith("__"):
            warnings.append(f"Blackboard key '{key}' starts with double underscores, possibly reserved")

    is_valid = len(errors) == 0
    return ValidationResult(is_valid, errors, warnings)


def validate_xml_structure(xml_content: str) -> ValidationResult:
    """
    Validate XML structure

    Args:
        xml_content: XML content

    Returns:
        Validation result
    """
    errors = []
    warnings = []

    try:
        import xml.etree.ElementTree as ET

        root = ET.fromstring(xml_content)

        # Check root element
        if root.tag != "BehaviorTree":
            errors.append("XML root element must be BehaviorTree")

        # Check required attributes
        if not root.get("name"):
            warnings.append("Behavior tree is missing name attribute")

        # Check child elements
        root_elements = [child for child in root if child.tag == "Root"]
        if len(root_elements) == 0:
            errors.append("XML is missing Root element")
        elif len(root_elements) > 1:
            errors.append("XML can only have one Root element")

        # Check node structure
        for root_element in root_elements:
            for child in root_element:
                if child.tag == "Root":
                    errors.append("Root element cannot contain Root element")

    except ET.ParseError as e:
        errors.append(f"XML parsing error: {e}")
    except Exception as e:
        errors.append(f"XML validation error: {e}")

    is_valid = len(errors) == 0
    return ValidationResult(is_valid, errors, warnings)


def get_tree_statistics(tree: BehaviorTree) -> Dict[str, Any]:
    """
    Get behavior tree statistics

    Args:
        tree: Behavior tree

    Returns:
        Statistics dictionary
    """
    if not tree.root:
        return {"error": "Behavior tree has no root node"}

    all_nodes = tree.get_all_nodes()
    node_types = {}
    status_distribution = {status.name: 0 for status in Status}

    for node in all_nodes:
        # 统计节点类型
        node_type = node.__class__.__name__
        node_types[node_type] = node_types.get(node_type, 0) + 1

        # 统计状态分布
        status_name = node.status.name
        status_distribution[status_name] += 1

    return {
        "total_nodes": len(all_nodes),
        "node_types": node_types,
        "status_distribution": status_distribution,
        "tree_depth": tree.root.get_depth() if tree.root else 0,
        "max_depth": max([node.get_depth() for node in all_nodes]) if all_nodes else 0,
        "has_blackboard": tree.blackboard is not None,
        "has_event_system": tree.event_system is not None,
        "has_tick_manager": tree.tick_manager is not None,
    }


def print_validation_result(result: ValidationResult, title: str = "Validation Result") -> None:
    """
    Print validation result

    Args:
        result: Validation result
        title: Title
    """
    print(f"\n=== {title} ===")

    if result.is_valid:
        print("✅ Validation passed")
    else:
        print("❌ Validation failed")

    if result.errors:
        print("\nErrors:")
        for error in result.errors:
            print(f"  ❌ {error}")

    if result.warnings:
        print("\nWarnings:")
        for warning in result.warnings:
            print(f"  ⚠️  {warning}")

    print()
