"""
XML Parser - Load behavior trees from XML files

Supports parsing behavior tree structures from XML files and building corresponding node trees.
"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..engine.behavior_tree import BehaviorTree
from ..nodes.base import BaseNode
from ..registry.node_registry import get_global_registry


@dataclass
class XMLParser:
    """
    XML Parser

    Responsible for parsing behavior tree structures from XML files and building corresponding node trees.
    Supports parsing of custom node types.
    """

    def parse_file(self, file_path: str) -> BehaviorTree:
        """
        Parse behavior tree from XML file

        Args:
            file_path: XML file path

        Returns:
            Parsed behavior tree
        """
        try:
            tree = ET.parse(file_path)
            root_element = tree.getroot()
            return self._parse_element(root_element)
        except Exception as e:
            raise ValueError(f"Failed to parse XML file: {e}")

    def parse_string(self, xml_string: str) -> BehaviorTree:
        """
        Parse behavior tree from XML string

        Args:
            xml_string: XML string

        Returns:
            Parsed behavior tree
        """
        try:
            root_element = ET.fromstring(xml_string)
            return self._parse_element(root_element)
        except Exception as e:
            raise ValueError(f"Failed to parse XML string: {e}")

    def _parse_element(self, element: ET.Element) -> BehaviorTree:
        """
        Parse XML element

        Args:
            element: XML element

        Returns:
            Behavior tree
        """
        # Check root element
        if element.tag != "BehaviorTree":
            raise ValueError("Root element must be BehaviorTree")

        # Get behavior tree attributes
        tree_name = element.get("name", "BehaviorTree")
        tree_description = element.get("description", "")

        # Parse root node - directly use first child node as root node
        root_node = None
        for child in element:
            if child.tag != "Root":  # Skip Root tags, directly parse other nodes
                root_node = self._parse_node(child)
                break

        if root_node is None:
            raise ValueError("Root node not found")

        # Create behavior tree
        behavior_tree = BehaviorTree(
            name=tree_name, description=tree_description
        )
        behavior_tree.load_from_root(root_node)

        return behavior_tree

    def _parse_node(self, element: ET.Element) -> BaseNode:
        """
        Parse node element

        Args:
            element: Node XML element

        Returns:
            Parsed node
        """
        node_type = element.tag
        node_name = element.get("name", node_type)

        # Get node attributes and handle type conversion
        attributes = self._parse_attributes(element)

        # Ensure name parameter is not duplicated
        if "name" in attributes:
            del attributes["name"]

        # Create node from global registry
        registry = get_global_registry()
        # Add name parameter to attributes
        attributes["name"] = node_name
        # Call create method, first parameter is node type name
        node = registry.create(node_type, **attributes)

        if node is None:
            raise ValueError(f"Unknown node type: {node_type}")

        # Parse child nodes
        for child_element in element:
            if child_element.tag != "Root":  # Skip Root tags
                child_node = self._parse_node(child_element)
                node.add_child(child_node)

        return node

    def _parse_attributes(self, element: ET.Element) -> Dict[str, Any]:
        """
        Parse node attributes

        Args:
            element: XML element

        Returns:
            Attributes dictionary
        """
        attributes = {}

        for key, value in element.attrib.items():
            if key == "name":
                continue  # name attribute handled separately

            # Try to convert attribute value types
            try:
                # Try to convert to integer
                if value.isdigit():
                    attributes[key] = int(value)
                # Try to convert to float
                elif value.replace(".", "").replace("-", "").isdigit():
                    attributes[key] = float(value)
                # Try to convert to boolean
                elif value.lower() in ["true", "false"]:
                    attributes[key] = value.lower() == "true"
                else:
                    attributes[key] = value
            except ValueError:
                attributes[key] = value

        return attributes


# Example XML format:
"""
<BehaviorTree name="ExampleTree" description="Example behavior tree">
    <Sequence name="Main sequence">
        <CheckBlackboard name="Check condition" key="enemy_visible" expected_value="true" />
        <Log name="Output log" message="Enemy visible" />
        <Wait name="Wait" duration="1.0" />
    </Sequence>
</BehaviorTree>
"""
