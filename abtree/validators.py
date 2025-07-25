"""
Validation Utilities - Behavior Tree and Node Validation Functions

Provides validation functions for behavior trees and nodes to ensure the correctness of data structures.
"""

from dataclasses import dataclass
from typing import Any, Dict, List

from .nodes.base import BaseNode
from .engine.behavior_tree import BehaviorTree


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
    errors: List[str] = []
    warnings: List[str] = []

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

    # Check event dispatcher
    if not tree.event_dispatcher:
        warnings.append("Behavior tree has no event dispatcher")

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
    errors: List[str] = []
    warnings: List[str] = []

    # Check node name
    if not node.name:
        errors.append(f"Node name cannot be empty (type: {node.__class__.__name__})")

    # Check node type
    if not isinstance(node, BaseNode):
        errors.append(f"Node must inherit from BaseNode (type: {node.__class__.__name__})")

    # Check node-specific validation
    specific_errors = _validate_node_specific(node)
    errors.extend(specific_errors)

    # Check children
    if hasattr(node, 'children') and node.children:
        for i, child in enumerate(node.children):
            child_result = validate_node(child)
            if not child_result.is_valid:
                errors.extend([f"Child {i}: {error}" for error in child_result.errors])
            warnings.extend([f"Child {i}: {warning}" for warning in child_result.warnings])

    is_valid = len(errors) == 0
    return ValidationResult(is_valid, errors, warnings)


def _validate_node_specific(node: BaseNode) -> List[str]:
    """
    Validate node-specific rules

    Args:
        node: Node to validate

    Returns:
        List of validation errors
    """
    errors: List[str] = []

    # Action nodes should not have children
    if hasattr(node, 'children') and node.children and hasattr(node, 'execute'):
        errors.append("Action nodes should not have children")

    # Composite nodes should have children
    if hasattr(node, 'children') and not node.children and hasattr(node, 'tick'):
        if not hasattr(node, 'execute'):  # Not an action node
            errors.append("Composite nodes should have children")

    # Decorator nodes should have exactly one child
    if hasattr(node, 'children') and len(node.children) != 1 and hasattr(node, 'decorate'):
        errors.append("Decorator nodes should have exactly one child")

    return errors


def validate_blackboard_data(data: Dict[str, Any]) -> ValidationResult:
    """
    Validate blackboard data

    Args:
        data: Blackboard data to validate

    Returns:
        Validation result
    """
    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(data, dict):
        errors.append("Blackboard data must be a dictionary")

    # Check for circular references
    try:
        import json
        json.dumps(data)
    except (TypeError, ValueError):
        errors.append("Blackboard data contains non-serializable objects")

    is_valid = len(errors) == 0
    return ValidationResult(is_valid, errors, warnings)


def validate_xml_structure(xml_content: str) -> ValidationResult:
    """
    Validate XML structure

    Args:
        xml_content: XML content to validate

    Returns:
        Validation result
    """
    errors: List[str] = []
    warnings: List[str] = []

    try:
        import xml.etree.ElementTree as ET
        ET.fromstring(xml_content)
    except ET.ParseError as e:
        errors.append(f"Invalid XML structure: {e}")

    # Check for required elements
    if "<BehaviorTree" not in xml_content and "<BehaviorForest" not in xml_content:
        errors.append("XML must contain BehaviorTree or BehaviorForest element")

    is_valid = len(errors) == 0
    return ValidationResult(is_valid, errors, warnings)


def get_tree_statistics(tree: BehaviorTree) -> Dict[str, Any]:
    """
    Get behavior tree statistics

    Args:
        tree: Behavior tree to analyze

    Returns:
        Tree statistics
    """
    all_nodes = tree.get_all_nodes()
    
    # Count node types
    node_types: Dict[str, int] = {}
    for node in all_nodes:
        node_type = node.__class__.__name__
        node_types[node_type] = node_types.get(node_type, 0) + 1
    
    # Calculate depth
    def get_node_depth(node: BaseNode, current_depth: int = 0) -> int:
        max_depth = current_depth
        if hasattr(node, 'children') and node.children:
            for child in node.children:
                child_depth = get_node_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
        return max_depth
    
    tree_depth = get_node_depth(tree.root) if tree.root else 0
    
    return {
        "total_nodes": len(all_nodes),
        "node_types": node_types,
        "tree_depth": tree_depth,
        "has_root": tree.root is not None,
        "has_blackboard": tree.blackboard is not None,
        "has_event_dispatcher": tree.event_dispatcher is not None,
        "has_tick_manager": tree.tick_manager is not None,
    }


def print_validation_result(result: ValidationResult, title: str = "Validation Result") -> None:
    """
    Print validation result

    Args:
        result: Validation result to print
        title: Title for the output
    """
    print(f"\n=== {title} ===")
    print(f"Valid: {result.is_valid}")
    
    if result.errors:
        print(f"\nErrors ({len(result.errors)}):")
        for error in result.errors:
            print(f"  ❌ {error}")
    
    if result.warnings:
        print(f"\nWarnings ({len(result.warnings)}):")
        for warning in result.warnings:
            print(f"  ⚠️  {warning}")
    
    if not result.errors and not result.warnings:
        print("  ✅ No issues found")
    
    print() 