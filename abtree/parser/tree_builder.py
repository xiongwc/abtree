"""
Tree Builder - Behavior Tree Export and Construction

Provides functions to export behavior trees to XML format,
as well as to build behavior trees from node trees.
"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Any, Dict, Optional

from ..engine.behavior_tree import BehaviorTree
from ..nodes.base import BaseNode


@dataclass
class TreeBuilder:
    """
    Tree Builder

    Responsible for exporting behavior trees to XML format, as well as building behavior trees from node trees.
    """

    def build_tree(self, tree_dict: dict, name: str = "BehaviorTree", description: str = "") -> BehaviorTree:
        """
        Build behavior tree from dictionary

        Args:
            tree_dict: Dictionary containing tree structure
            name: Default behavior tree name
            description: Default behavior tree description

        Returns:
            constructed behavior tree
        """
        # Extract name and description from dict if available
        tree_name = tree_dict.get("name", name)
        tree_description = tree_dict.get("description", description)
        
        # Build the root node from the dict
        root = self._build_node(tree_dict.get("root", {}))
        
        tree = BehaviorTree(name=tree_name, description=tree_description)
        tree.load_from_root(root)
        return tree

    def _build_node(self, node_dict: dict) -> BaseNode:
        """
        Build a node from dictionary
        
        Args:
            node_dict: Dictionary containing node information
            
        Returns:
            Built node
        """
        if not node_dict:
            raise ValueError("Empty node dictionary")
        
        node_type = node_dict.get("type")
        if not node_type:
            raise ValueError("Node type not specified")
        
        # Create node based on type
        node: BaseNode
        if node_type == "Sequence":
            from ..nodes.composite import Sequence
            node = Sequence(name=node_dict.get("name", "Sequence"))
        elif node_type == "Selector":
            from ..nodes.composite import Selector
            node = Selector(name=node_dict.get("name", "Selector"))
        elif node_type == "Parallel":
            from ..nodes.composite import Parallel
            policy = node_dict.get("policy", "SUCCEED_ON_ONE")
            node = Parallel(name=node_dict.get("name", "Parallel"), policy=policy)
        elif node_type == "Repeater":
            from ..nodes.decorator import Repeater
            repeat_count = node_dict.get("repeat_count", 1)
            node = Repeater(name=node_dict.get("name", "Repeater"), repeat_count=repeat_count)
        elif node_type == "AlwaysTrue":
            from ..nodes.condition import AlwaysTrue
            node = AlwaysTrue(name=node_dict.get("name", "AlwaysTrue"))
        elif node_type == "AlwaysFalse":
            from ..nodes.condition import AlwaysFalse
            node = AlwaysFalse(name=node_dict.get("name", "AlwaysFalse"))
        else:
            raise ValueError(f"Unknown node type: {node_type}")
        
        # Add children if any
        children = node_dict.get("children", [])
        for child_dict in children:
            child_node = self._build_node(child_dict)
            node.add_child(child_node)
        
        return node

    def export_to_xml(self, tree: BehaviorTree, file_path: Optional[str] = None) -> str:
        """
        Export behavior tree to XML

        Args:
            tree: behavior tree to export
            file_path: output file path, if None then only return XML string

        Returns:
            XML string
        """
        # Create root element
        root_element = ET.Element("BehaviorTree")
        root_element.set("name", tree.name)
        if tree.description:
            root_element.set("description", tree.description)

        # Create Root element
        root_node_element = ET.SubElement(root_element, "Root")

        # Recursively export nodes
        if tree.root is not None:
            self._export_node(tree.root, root_node_element)

        # Create XML tree
        xml_tree = ET.ElementTree(root_element)

        # Format XML
        self._indent_xml(root_element)

        # Convert to string
        xml_string = ET.tostring(root_element, encoding="unicode")

        # If file path is specified, write to file
        if file_path:
            xml_tree.write(file_path, encoding="utf-8", xml_declaration=True)

        return xml_string

    def _export_node(self, node: BaseNode, parent_element: ET.Element) -> None:
        """
        Recursively export node

        Args:
            node: node to export
            parent_element: parent XML element
        """
        # Create node element
        node_element = ET.SubElement(parent_element, node.__class__.__name__)
        node_element.set("name", node.name)

        # Export node attributes
        self._export_node_attributes(node, node_element)

        # Recursively export child nodes
        for child in node.children:
            self._export_node(child, node_element)

    def _export_node_attributes(self, node: BaseNode, element: ET.Element) -> None:
        """
        Export node attributes

        Args:
            node: node
            element: XML element
        """
        # Get all attributes of the node
        node_attrs: Dict[str, str] = {}

        # For different types of nodes, export different attributes
        if hasattr(node, "duration"):
            node_attrs["duration"] = str(node.duration)

        if hasattr(node, "message"):
            node_attrs["message"] = str(node.message)

        if hasattr(node, "level"):
            node_attrs["level"] = str(node.level)

        if hasattr(node, "key"):
            node_attrs["key"] = str(node.key)

        if hasattr(node, "expected_value"):
            node_attrs["expected_value"] = str(node.expected_value)

        if hasattr(node, "check_exists"):
            node_attrs["check_exists"] = str(node.check_exists).lower()

        if hasattr(node, "operator"):
            node_attrs["operator"] = str(node.operator)

        if hasattr(node, "value"):
            node_attrs["value"] = str(node.value)

        if hasattr(node, "policy"):
            node_attrs["policy"] = node.policy.name

        if hasattr(node, "repeat_count"):
            node_attrs["repeat_count"] = str(node.repeat_count)

        # Set attributes
        for key, value in node_attrs.items():
            element.set(key, value)

    def _indent_xml(self, elem: ET.Element, level: int = 0) -> None:
        """
        Format XML, add indentation

        Args:
            elem: XML element
            level: indentation level
        """
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for child in elem:
                self._indent_xml(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def create_simple_tree(self, name: str = "SimpleTree") -> BehaviorTree:
        """
        Create a simple example behavior tree

        Args:
            name: behavior tree name

        Returns:
            example behavior tree
        """
        from ..nodes.action import Log, Wait
        from ..nodes.composite import Selector, Sequence
        from ..nodes.condition import AlwaysTrue, CheckBlackboard

        # Create root node
        root = Selector(name="MainSelector")

        # Create first branch
        sequence1 = Sequence(name="Sequence1")
        sequence1.add_child(CheckBlackboard(name="CheckCondition1", key="condition1"))
        sequence1.add_child(Log(name="Log1", message="Condition1 met"))
        sequence1.add_child(Wait(name="Wait1", duration=1.0))

        # Create second branch
        sequence2 = Sequence(name="Sequence2")
        sequence2.add_child(AlwaysTrue(name="AlwaysTrue"))
        sequence2.add_child(Log(name="Log2", message="Execute default branch"))

        # Add to root node
        root.add_child(sequence1)
        root.add_child(sequence2)

        # Create tree
        tree = BehaviorTree(name=name, description="Simple example behavior tree")
        tree.load_from_root(root)
        return tree

    def create_advanced_tree(self, name: str = "AdvancedTree") -> BehaviorTree:
        """
        Create an advanced example behavior tree

        Args:
            name: behavior tree name

        Returns:
            advanced example behavior tree
        """
        from ..core.status import Policy
        from ..nodes.action import Log, SetBlackboard, Wait
        from ..nodes.composite import Parallel, Selector, Sequence
        from ..nodes.condition import CheckBlackboard, Compare, IsTrue
        from ..nodes.decorator import Inverter, Repeater

        # Create root node
        root = Selector(name="MainDecision")

        # Create attack branch
        attack_sequence = Sequence(name="AttackSequence")
        attack_sequence.add_child(
            CheckBlackboard(name="CheckEnemy", key="enemy_visible", expected_value=True)
        )
        attack_sequence.add_child(Log(name="AttackLog", message="Start attack"))
        attack_sequence.add_child(Wait(name="AttackWait", duration=0.5))
        attack_sequence.add_child(
            SetBlackboard(name="SetAttackStatus", key="attacking", value=True)
        )

        # Create patrol branch
        patrol_sequence = Sequence(name="PatrolSequence")
        patrol_sequence.add_child(
            Inverter(
                name="InvertCheck",
                child=CheckBlackboard(
                    name="CheckEnemy", key="enemy_visible", expected_value=True
                ),
            )
        )
        patrol_sequence.add_child(Log(name="PatrolLog", message="Start patrol"))

        # Create parallel tasks
        parallel_tasks = Parallel(name="ParallelTasks", policy=Policy.SUCCEED_ON_ALL)
        parallel_tasks.add_child(
            Repeater(
                name="RepeatCheck",
                repeat_count=3,
                child=CheckBlackboard(
                    name="CheckHealth", key="health", expected_value=100
                ),
            )
        )
        parallel_tasks.add_child(Log(name="StatusLog", message="Check status"))

        # Add to root node
        root.add_child(attack_sequence)
        root.add_child(patrol_sequence)
        root.add_child(parallel_tasks)

        # Create tree
        tree = BehaviorTree(name=name, description="Advanced example behavior tree")
        tree.load_from_root(root)
        return tree

    def validate_tree(self, tree: BehaviorTree) -> bool:
        """
        Validate the validity of the behavior tree

        Args:
            tree: behavior tree to validate

        Returns:
            Return True if the behavior tree is valid, otherwise return False
        """
        try:
            # Check if root node exists
            if tree.root is None:
                return False

            # Recursively validate all nodes
            return self._validate_node(tree.root)

        except Exception:
            return False

    def _validate_node(self, node: BaseNode) -> bool:
        """
        Recursively validate node

        Args:
            node: node to validate

        Returns:
            Return True if the node is valid, otherwise return False
        """
        try:
            # Check node name
            if not node.name:
                return False

            # Check child nodes
            for child in node.children:
                if not self._validate_node(child):
                    return False

            return True

        except Exception:
            return False
