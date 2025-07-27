"""
XML Parser - Load behavior trees and forests from XML files

Supports parsing behavior tree structures and behavior forests from XML files including:
- Single behavior trees
- Multiple behavior trees in forests
- Communication patterns (Pub/Sub, Req/Resp, Shared Blackboard, etc.)
- Service configurations
"""

import xml.etree.ElementTree as ET
import inspect
import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Union, Tuple, Type

from ..engine.behavior_tree import BehaviorTree
from ..forest.core import BehaviorForest, ForestNode, ForestNodeType
from ..forest.communication import CommunicationMiddleware
from ..nodes.base import BaseNode
from ..registry.node_registry import get_global_registry
from ..core.status import Status


@dataclass
class XMLParser:
    """
    XML Parser for Behavior Trees and Forests
    
    Responsible for parsing behavior tree structures and behavior forests from XML files.
    Supports parsing of custom node types and communication patterns.
    """

    def parse_file(self, file_path: str) -> Union[BehaviorTree, BehaviorForest]:
        """
        Parse behavior tree or forest from XML file

        Args:
            file_path: XML file path

        Returns:
            Parsed behavior tree or forest
        """
        try:
            tree = ET.parse(file_path)
            root_element = tree.getroot()
            return self._parse_root_element(root_element)
        except FileNotFoundError:
            raise ValueError(f"XML file not found: {file_path}")
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format in file {file_path}: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing XML file {file_path}: {e}")

    def parse_string(self, xml_string: str) -> Union[BehaviorTree, BehaviorForest]:
        """
        Parse behavior tree or forest from XML string

        Args:
            xml_string: XML string

        Returns:
            Parsed behavior tree or forest
        """
        try:
            if not xml_string.strip():
                raise ValueError("Empty XML string provided")
            root_element = ET.fromstring(xml_string)
            return self._parse_root_element(root_element)
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing XML string: {e}")

    def _parse_root_element(self, element: ET.Element) -> Union[BehaviorTree, BehaviorForest]:
        """
        Parse root XML element and determine type

        Args:
            element: Root XML element

        Returns:
            Behavior tree or forest
        """
        if element.tag == "BehaviorTree":
            return self._parse_behavior_tree(element)
        elif element.tag in ["BehaviorForest", "BehaviorForestService"]:
            return self._parse_behavior_forest(element)
        else:
            raise ValueError(
                f"Root element must be BehaviorTree, BehaviorForest, or BehaviorForestService, "
                f"got: {element.tag}"
            )

    # ============================================================================
    # Behavior Tree Parsing
    # ============================================================================

    def _parse_behavior_tree(self, element: ET.Element) -> BehaviorTree:
        """
        Parse single behavior tree

        Args:
            element: Behavior tree XML element

        Returns:
            Parsed behavior tree
        """
        tree_name = element.get("name", "BehaviorTree")
        tree_description = element.get("description", "")

        # Find root node (first non-Root child element)
        root_node = self._find_root_node(element)
        if root_node is None:
            raise ValueError("Root node not found in behavior tree")

        # Create and initialize behavior tree
        behavior_tree = BehaviorTree(name=tree_name, description=tree_description)
        behavior_tree._init_default_components()
        behavior_tree.load_from_node(root_node)

        return behavior_tree

    def _find_root_node(self, element: ET.Element) -> Optional[BaseNode]:
        """
        Find the root node in a behavior tree element

        Args:
            element: Behavior tree XML element

        Returns:
            Root node or None if not found
        """
        for child in element:
            if child.tag != "Root":  # Skip Root tags
                return self._parse_node(child)
        return None

    # ============================================================================
    # Behavior Forest Parsing
    # ============================================================================

    def _parse_behavior_forest(self, element: ET.Element) -> BehaviorForest:
        """
        Parse behavior forest

        Args:
            element: Behavior forest XML element

        Returns:
            Parsed behavior forest
        """
        forest_name = element.get("name", "BehaviorForest")
        forest_description = element.get("description", "")

        # Create behavior forest
        forest = BehaviorForest(name=forest_name)

        # Parse all behavior trees in the forest
        for child in element:
            if child.tag == "BehaviorTree":
                self._parse_forest_behavior_tree(child, forest)

        # Auto-setup communication middleware if needed
        self._auto_setup_communication(forest)

        return forest

    def _parse_forest_behavior_tree(self, element: ET.Element, forest: BehaviorForest) -> None:
        """
        Parse behavior tree element within forest

        Args:
            element: Behavior tree XML element
            forest: Behavior forest to add tree to
        """
        tree_name = element.get("name", "BehaviorTree")
        tree_description = element.get("description", "")

        # Find root node
        root_node = self._find_root_node(element)
        if root_node is None:
            raise ValueError(f"Root node not found in behavior tree: {tree_name}")

        # Create behavior tree
        behavior_tree = BehaviorTree(name=tree_name, description=tree_description)
        behavior_tree.load_from_node(root_node)
        
        # Determine node type and create forest node
        node_type = self._determine_forest_node_type(tree_name)
        forest_node = ForestNode(
            name=tree_name,
            tree=behavior_tree,
            node_type=node_type
        )
        
        # Add node to forest
        forest.add_node(forest_node)

    def _determine_forest_node_type(self, tree_name: str) -> ForestNodeType:
        """
        Determine forest node type based on tree name

        Args:
            tree_name: Name of the behavior tree

        Returns:
            Forest node type
        """
        name_lower = tree_name.lower()
        
        if any(keyword in name_lower for keyword in ["trigger", "master", "coordinator"]):
            return ForestNodeType.MASTER
        elif any(keyword in name_lower for keyword in ["monitor", "watch"]):
            return ForestNodeType.MONITOR
        else:
            return ForestNodeType.WORKER

    def _auto_setup_communication(self, forest: BehaviorForest) -> None:
        """
        Automatically setup communication middleware if communication nodes are detected

        Args:
            forest: Behavior forest
        """
        if self._has_communication_nodes_in_forest(forest):
            communication = CommunicationMiddleware("AutoDetectedCommunication")
            forest.add_middleware(communication)

    def _has_communication_nodes_in_forest(self, forest: BehaviorForest) -> bool:
        """
        Check if any trees in the forest contain communication nodes

        Args:
            forest: Behavior forest to check

        Returns:
            True if communication nodes are found
        """
        for forest_node in forest.nodes.values():
            if forest_node.tree and forest_node.tree.root:
                if self._has_communication_nodes_recursive(forest_node.tree.root):
                    return True
        return False

    def _has_communication_nodes_recursive(self, node: BaseNode) -> bool:
        """
        Recursively check if a node or its descendants contain communication nodes

        Args:
            node: Node to check

        Returns:
            True if communication nodes are found
        """
        if self._is_communication_node(node):
            return True
        
        for child in node.children:
            if self._has_communication_nodes_recursive(child):
                return True
        
        return False

    def _is_communication_node(self, node: BaseNode) -> bool:
        """
        Check if a node is a communication node

        Args:
            node: Node to check

        Returns:
            True if node is a communication node
        """
        communication_node_types = {
            'CommPublisher', 'CommSubscriber', 
            'ComExternalInput', 'ComExternalOutput',
            'CommService', 'CommClient',
            'CommWatcher', 'CommProvider', 'CommCaller',
            'CommTask', 'ComClaimant'
        }
        
        return node.__class__.__name__ in communication_node_types

    # ============================================================================
    # Node Parsing
    # ============================================================================

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

        # Parse attributes and parameter mappings
        attributes, param_mappings = self._parse_node_attributes(element)
        
        # Remove name from attributes to avoid duplication
        attributes.pop("name", None)

        # Create node with proper parameter separation
        node = self._create_node_with_parameters(node_type, node_name, attributes)

        # Setup parameter mappings
        self._setup_parameter_mappings(node, param_mappings)

        # Parse child nodes
        for child_element in element:
            if child_element.tag != "Root":  # Skip Root tags
                child_node = self._parse_node(child_element)
                node.add_child(child_node)

        return node

    def _parse_node_attributes(self, element: ET.Element) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """
        Parse node attributes and parameter mappings

        Args:
            element: XML element

        Returns:
            Tuple of (attributes, parameter_mappings)
        """
        attributes: Dict[str, Any] = {}
        param_mappings: Dict[str, str] = {}

        for key, value in element.attrib.items():
            if key == "name":
                continue  # name attribute handled separately

            # Check for parameter mapping format: {blackboard_key}
            if self._is_parameter_mapping(value):
                blackboard_key = self._extract_blackboard_key(value)
                param_mappings[key] = blackboard_key
            else:
                # Convert attribute value to appropriate type
                attributes[key] = self._convert_attribute_value(value)

        return attributes, param_mappings

    def _is_parameter_mapping(self, value: str) -> bool:
        """
        Check if a value is a parameter mapping format

        Args:
            value: String value to check

        Returns:
            True if it's a parameter mapping
        """
        return isinstance(value, str) and re.match(r'^\{[^}]+\}$', value) is not None

    def _extract_blackboard_key(self, value: str) -> str:
        """
        Extract blackboard key from parameter mapping format

        Args:
            value: Parameter mapping string like "{blackboard_key}"

        Returns:
            Extracted blackboard key
        """
        match = re.match(r'^\{([^}]+)\}$', value)
        if not match:
            raise ValueError(f"Invalid parameter mapping format: {value}")
        return match.group(1)

    def _convert_attribute_value(self, value: str) -> Any:
        """
        Convert attribute value to appropriate type

        Args:
            value: String value to convert

        Returns:
            Converted value
        """
        try:
            # Try to convert to integer
            if value.isdigit():
                return int(value)
            # Try to convert to float
            elif value.replace(".", "").replace("-", "").isdigit():
                return float(value)
            # Try to convert to boolean
            elif value.lower() in ["true", "false"]:
                return value.lower() == "true"
            # Try to convert to JSON object
            elif value.startswith('{') and value.endswith('}'):
                return json.loads(value)
            # Try to convert to JSON array
            elif value.startswith('[') and value.endswith(']'):
                return json.loads(value)
            else:
                return value
        except (ValueError, TypeError, json.JSONDecodeError):
            return value

    def _create_node_with_parameters(self, node_type: str, node_name: str, attributes: Dict[str, Any]) -> BaseNode:
        """
        Create node with proper parameter separation between __init__ and execute

        Args:
            node_type: Type of node to create
            node_name: Name of the node
            attributes: All attributes

        Returns:
            Created node
        """
        registry = get_global_registry()
        
        # Get node class
        node_class = registry.get_node_class(node_type)
        if node_class is None:
            self._raise_node_not_registered_error(node_type)
            # This line should never be reached due to the exception above
            raise RuntimeError("Node class is None after error handling")

        # Separate parameters for __init__ and execute
        init_params, execute_params = self._separate_node_parameters(node_class, attributes)
        
        # Create node with init parameters
        node = registry.create(node_type, name=node_name, **init_params)
        if node is None:
            self._raise_node_creation_error(node_type)
            # This line should never be reached due to the exception above
            raise RuntimeError("Node creation returned None after error handling")

        # Store execute parameters for later use
        if execute_params:
            setattr(node, '_execute_attributes', execute_params)

        # Initialize node properties
        self._initialize_node_properties(node)

        return node

    def _separate_node_parameters(self, node_class: Type[BaseNode], attributes: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Separate parameters for __init__ and execute methods

        Args:
            node_class: Node class to inspect
            attributes: All attributes

        Returns:
            Tuple of (init_parameters, execute_parameters)
        """
        init_params = {}
        execute_params = {}

        try:
            # Get __init__ method signature
            init_sig = inspect.signature(node_class.__init__)
            init_param_names = self._get_method_parameter_names(init_sig)
            
            # Get execute method signature if it exists
            execute_param_names = []
            if hasattr(node_class, 'execute'):
                execute_sig = inspect.signature(node_class.execute)
                execute_param_names = self._get_method_parameter_names(execute_sig)

            # Separate attributes based on method signatures
            for key, value in attributes.items():
                if key in init_param_names:
                    init_params[key] = value
                elif key in execute_param_names:
                    execute_params[key] = value
                else:
                    # Default to init if not found in either
                    init_params[key] = value

        except Exception:
            # If inspection fails, pass all to init
            init_params.update(attributes)

        return init_params, execute_params

    def _get_method_parameter_names(self, signature: inspect.Signature) -> List[str]:
        """
        Get parameter names from method signature, excluding 'self'

        Args:
            signature: Method signature

        Returns:
            List of parameter names
        """
        param_names = list(signature.parameters.keys())
        if param_names and param_names[0] == 'self':
            param_names = param_names[1:]
        return param_names

    def _initialize_node_properties(self, node: BaseNode) -> None:
        """
        Initialize required node properties

        Args:
            node: Node to initialize
        """
        if not hasattr(node, 'children'):
            node.children = []
        if not hasattr(node, 'parent'):
            node.parent = None
        if not hasattr(node, 'status'):
            node.status = Status.FAILURE
        if not hasattr(node, '_last_tick_time'):
            node._last_tick_time = 0.0

    def _setup_parameter_mappings(self, node: BaseNode, param_mappings: Dict[str, str]) -> None:
        """
        Setup parameter mappings for the node

        Args:
            node: Node to setup mappings for
            param_mappings: Parameter mappings dictionary
        """
        for node_attr, blackboard_key in param_mappings.items():
            node.set_param_mapping(node_attr, blackboard_key)

    def _raise_node_not_registered_error(self, node_type: str) -> None:
        """
        Raise error for unregistered node type

        Args:
            node_type: Type of node that's not registered
        """
        registry = get_global_registry()
        registered_nodes = registry.get_registered()
        registered_nodes_str = ", ".join(sorted(registered_nodes)) if registered_nodes else "none"
        
        raise ValueError(
            f"Node type '{node_type}' is not registered in the node registry. "
            f"Available registered node types: {registered_nodes_str}. "
            f"To register a custom node type, use: "
            f"from abtree.registry.node_registry import register_node; "
            f"register_node('{node_type}', YourNodeClass)"
        )

    def _raise_node_creation_error(self, node_type: str) -> None:
        """
        Raise error for node creation failure

        Args:
            node_type: Type of node that failed to create
        """
        registry = get_global_registry()
        registered_nodes = registry.get_registered()
        registered_nodes_str = ", ".join(sorted(registered_nodes)) if registered_nodes else "none"
        
        raise ValueError(
            f"Failed to create node instance of type '{node_type}'. "
            f"Available registered node types: {registered_nodes_str}. "
            f"To register a custom node type, use: "
            f"from abtree.registry.node_registry import register_node; "
            f"register_node('{node_type}', YourNodeClass)"
        )


# Example XML formats:
"""
Single Behavior Tree:
<BehaviorTree name="ExampleTree" description="Example behavior tree">
    <Sequence name="Main sequence">
        <CheckBlackboard name="Check condition" key="enemy_visible" expected_value="true" />
        <Log name="Output log" message="Enemy visible" />
        <Wait name="Wait" duration="1.0" />
    </Sequence>
</BehaviorTree>

Behavior Forest:
<BehaviorForest name="RobotForest" description="Robot Forest">
    <BehaviorTree name="TriggerService" description="Trigger Service">
        <Selector name="Trigger Controller">
            <Sequence name="Timer Trigger">
                <CheckBlackboard name="Check Timer" key="timer_enabled" expected_value="true" />
                <Wait name="Timer Wait" duration="5.0" />
                <Log name="Timer Log" message="Timer triggered" />
            </Sequence>
        </Selector>
    </BehaviorTree>    
</BehaviorForest>
""" 