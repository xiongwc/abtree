"""
XML Parser - Load behavior trees and forests from XML files

Supports parsing behavior tree structures and behavior forests from XML files including:
- Single behavior trees
- Multiple behavior trees in forests
- Communication patterns (Pub/Sub, Req/Resp, Shared Blackboard, etc.)
- Service configurations
"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Union

from ..engine.behavior_tree import BehaviorTree
from ..forest.core import BehaviorForest, ForestNode, ForestNodeType
from ..forest.communication import (
    CommunicationMiddleware,
    CommunicationType,
    Message,
    Request,
    Response,
    Task,
)
from ..nodes.base import BaseNode
from ..registry.node_registry import get_global_registry
from ..core.status import Status


@dataclass
class CommunicationConfig:
    """Communication configuration container"""
    topics: Optional[Dict[str, Dict[str, List[str]]]] = None  # topic_name -> {publishers: [], subscribers: []}
    services: Optional[Dict[str, Dict[str, Union[str, List[str]]]]] = None  # service_name -> {server: str, clients: []}
    shared_keys: Optional[Set[str]] = None
    states: Optional[Dict[str, List[str]]] = None  # state_name -> [watchers]
    calls: Optional[Dict[str, Dict[str, List[str]]]] = None  # call_name -> {providers: [], callers: []}
    tasks: Optional[Dict[str, Dict[str, Union[str, List[str]]]]] = None  # task_name -> {publisher: str, claimants: []}
    
    def __post_init__(self) -> None:
        if self.topics is None:
            self.topics = {}
        if self.services is None:
            self.services = {}
        if self.shared_keys is None:
            self.shared_keys = set()
        if self.states is None:
            self.states = {}
        if self.calls is None:
            self.calls = {}
        if self.tasks is None:
            self.tasks = {}


@dataclass
class XMLParser:
    """
    XML Parser

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
            return self._parse_element(root_element)
        except Exception as e:
            raise ValueError(f"Failed to parse XML file: {e}")

    def parse_string(self, xml_string: str) -> Union[BehaviorTree, BehaviorForest]:
        """
        Parse behavior tree or forest from XML string

        Args:
            xml_string: XML string

        Returns:
            Parsed behavior tree or forest
        """
        try:
            root_element = ET.fromstring(xml_string)
            return self._parse_element(root_element)
        except Exception as e:
            raise ValueError(f"Failed to parse XML string: {e}")

    def _parse_element(self, element: ET.Element) -> Union[BehaviorTree, BehaviorForest]:
        """
        Parse XML element

        Args:
            element: XML element

        Returns:
            Behavior tree or forest
        """
        # Check root element type
        if element.tag == "BehaviorTree":
            return self._parse_behavior_tree(element)
        elif element.tag in ["BehaviorForest", "BehaviorForestService"]:
            return self._parse_behavior_forest(element)
        else:
            raise ValueError("Root element must be BehaviorTree, BehaviorForest, or BehaviorForestService")

    def _parse_behavior_tree(self, element: ET.Element) -> BehaviorTree:
        """
        Parse single behavior tree

        Args:
            element: Behavior tree XML element

        Returns:
            Parsed behavior tree
        """
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
        # Ensure blackboard is initialized before loading nodes
        behavior_tree._init_default_components()
        behavior_tree.load_from_node(root_node)

        return behavior_tree

    def _parse_behavior_forest(self, element: ET.Element) -> BehaviorForest:
        """
        Parse behavior forest

        Args:
            element: Behavior forest XML element

        Returns:
            Parsed behavior forest
        """
        # Get forest attributes
        forest_name = element.get("name", "BehaviorForest")
        forest_description = element.get("description", "")

        # Create behavior forest
        forest = BehaviorForest(name=forest_name)

        # Parse behavior trees and communication
        communication_config = CommunicationConfig()
        
        for child in element:
            if child.tag == "BehaviorTree":
                self._parse_forest_behavior_tree(child, forest)
            elif child.tag == "Communication":
                communication_config = self._parse_communication(child)

        # Setup communication middleware
        self._setup_communication(forest, communication_config)

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

        # Parse root node directly from the behavior tree element
        root_node = None
        for child in element:
            if child.tag != "Root":  # Skip Root tags, directly parse other nodes
                root_node = self._parse_node(child)
                break

        if root_node is None:
            raise ValueError(f"Root node not found in behavior tree: {tree_name}")

        # Create behavior tree
        behavior_tree = BehaviorTree(
            name=tree_name, description=tree_description
        )
        behavior_tree.load_from_node(root_node)
        
        # Determine node type based on tree name
        node_type = self._determine_node_type(tree_name)
        
        # Create forest node
        forest_node = ForestNode(
            name=tree_name,
            tree=behavior_tree,
            node_type=node_type
        )
        
        # Add node to forest
        forest.add_node(forest_node)

    def _determine_node_type(self, tree_name: str) -> ForestNodeType:
        """
        Determine forest node type based on tree name

        Args:
            tree_name: Name of the behavior tree

        Returns:
            Forest node type
        """
        name_lower = tree_name.lower()
        
        if "trigger" in name_lower or "master" in name_lower or "coordinator" in name_lower:
            return ForestNodeType.MASTER
        elif "monitor" in name_lower or "watch" in name_lower:
            return ForestNodeType.MONITOR
        elif "service" in name_lower or "worker" in name_lower:
            return ForestNodeType.WORKER
        else:
            return ForestNodeType.WORKER

    def _parse_communication(self, element: ET.Element) -> CommunicationConfig:
        """
        Parse communication configuration

        Args:
            element: Communication XML element

        Returns:
            Communication configuration
        """
        config = CommunicationConfig()
        
        for child in element:
            if child.tag == "ComTopic":
                self._parse_topic(child, config)
            elif child.tag == "ComService":
                self._parse_service(child, config)
            elif child.tag == "ComShared":
                self._parse_shared(child, config)
            elif child.tag == "ComState":
                self._parse_state(child, config)
            elif child.tag == "ComCall":
                self._parse_call(child, config)
            elif child.tag == "ComTask":
                self._parse_task(child, config)
        
        return config

    def _parse_topic(self, element: ET.Element, config: CommunicationConfig) -> None:
        """Parse topic configuration"""
        topic_name = element.get("name", "")
        publishers: List[str] = []
        subscribers: List[str] = []
        
        for child in element:
            if child.tag == "ComPublisher":
                service = child.get("service", "")
                if service:
                    publishers.append(service)
            elif child.tag == "ComSubscriber":
                service = child.get("service", "")
                if service:
                    subscribers.append(service)
        
        if config.topics is not None:
            config.topics[topic_name] = {
                "publishers": publishers,
                "subscribers": subscribers
            }

    def _parse_service(self, element: ET.Element, config: CommunicationConfig) -> None:
        """Parse service configuration"""
        service_name = element.get("name", "")
        server = ""
        clients: List[str] = []
        
        for child in element:
            if child.tag == "ComServer":
                server = child.get("service", "")
            elif child.tag == "ComClient":
                service = child.get("service", "")
                if service:
                    clients.append(service)
        
        if config.services is not None:
            config.services[service_name] = {
                "server": server,
                "clients": clients
            }

    def _parse_shared(self, element: ET.Element, config: CommunicationConfig) -> None:
        """Parse shared blackboard configuration"""
        for child in element:
            if child.tag == "ComKey":
                key_name = child.get("name", "")
                if key_name and config.shared_keys is not None:
                    config.shared_keys.add(key_name)

    def _parse_state(self, element: ET.Element, config: CommunicationConfig) -> None:
        """Parse state watching configuration"""
        state_name = element.get("name", "")
        watchers: List[str] = []
        
        for child in element:
            if child.tag == "ComWatcher":
                service = child.get("service", "")
                if service:
                    watchers.append(service)
        
        if config.states is not None:
            config.states[state_name] = watchers

    def _parse_call(self, element: ET.Element, config: CommunicationConfig) -> None:
        """Parse behavior call configuration"""
        call_name = element.get("name", "")
        providers: List[str] = []
        callers: List[str] = []
        
        for child in element:
            if child.tag == "ComProvider":
                service = child.get("service", "")
                if service:
                    providers.append(service)
            elif child.tag == "ComCaller":
                service = child.get("service", "")
                if service:
                    callers.append(service)
        
        if config.calls is not None:
            config.calls[call_name] = {
                "providers": providers,
                "callers": callers
            }

    def _parse_task(self, element: ET.Element, config: CommunicationConfig) -> None:
        """Parse task board configuration"""
        task_name = element.get("name", "")
        publisher = ""
        claimants: List[str] = []
        
        for child in element:
            if child.tag == "ComPublisher":
                publisher = child.get("service", "")
            elif child.tag == "ComClaimant":
                service = child.get("service", "")
                if service:
                    claimants.append(service)
        
        if config.tasks is not None:
            config.tasks[task_name] = {
                "publisher": publisher,
                "claimants": claimants
            }

    def _setup_communication(self, forest: BehaviorForest, config: CommunicationConfig) -> None:
        """
        Setup communication middleware based on configuration

        Args:
            forest: Behavior forest
            config: Communication configuration
        """
        # Setup unified communication middleware
        if (config.topics or config.services or config.shared_keys or 
            config.states or config.calls or config.tasks):
            communication = CommunicationMiddleware("ForestCommunication")
            forest.add_middleware(communication)

    def _validate_node_parameters(self, node: BaseNode, attributes: Dict[str, Any]) -> None:
        """
        Validate node parameters against the execute method signature
        
        Args:
            node: Node instance
            attributes: Attributes to validate
        """
        # Check if node has execute method
        if not hasattr(node, 'execute'):
            return
            
        # Get execute method signature
        import inspect
        try:
            sig = inspect.signature(node.execute)
            param_names = list(sig.parameters.keys())
            
            # Skip 'self' parameter
            if param_names and param_names[0] == 'self':
                param_names = param_names[1:]
            
            # Check if all required parameters are provided in XML attributes
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                # 跳过*args和**kwargs参数
                if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                    continue
                if param.default == inspect.Parameter.empty:
                    if param_name not in attributes:
                        print(f"Warning: Required parameter '{param_name}' not provided in XML for node '{node.name}'")
                else:
                    # Parameter has default value, so it's optional
                    if param_name in attributes:
                        print(f"Info: Optional parameter '{param_name}' provided in XML for node '{node.name}'")
        except Exception as e:
            print(f"Warning: Could not validate parameters for node '{node.name}': {e}")

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

        # Extract parameter mappings if present
        param_mappings = attributes.pop("_param_mappings", {})

        # Ensure name parameter is not duplicated
        if "name" in attributes:
            del attributes["name"]

        # Create node from global registry
        registry = get_global_registry()
        
        # Separate __init__ parameters from execute parameters
        init_attributes = {"name": node_name}
        execute_attributes = {}
        
        # Get the node class to inspect its execute method
        node_class = registry.get_node_class(node_type)
        if node_class is None:
            raise ValueError(f"Unknown node type: {node_type}")
        
        # Check if node has execute method to determine parameter separation
        if hasattr(node_class, 'execute'):
            import inspect
            try:
                # First, check __init__ method signature
                init_sig = inspect.signature(node_class.__init__)
                init_param_names = list(init_sig.parameters.keys())
                # Skip 'self' parameter
                if init_param_names and init_param_names[0] == 'self':
                    init_param_names = init_param_names[1:]
                
                # Then check execute method signature
                execute_sig = inspect.signature(node_class.execute)
                execute_param_names = list(execute_sig.parameters.keys())
                # Skip 'self' parameter
                if execute_param_names and execute_param_names[0] == 'self':
                    execute_param_names = execute_param_names[1:]
                
                # Separate attributes based on both signatures
                for key, value in attributes.items():
                    if key in init_param_names:
                        init_attributes[key] = value
                    elif key in execute_param_names:
                        execute_attributes[key] = value
                    else:
                        # If not found in either, default to init
                        init_attributes[key] = value
            except Exception:
                # If we can't inspect, pass all to init
                init_attributes.update(attributes)
        else:
            # No execute method, pass all to init
            init_attributes.update(attributes)
        
        # Create the actual node with only init parameters
        node = registry.create(node_type, **init_attributes)

        if node is None:
            raise ValueError(f"Unknown node type: {node_type}")

        # Store execute parameters for later use
        if execute_attributes:
            setattr(node, '_execute_attributes', execute_attributes)

        # Add parameter mappings to execute attributes for validation
        for param_name, blackboard_key in param_mappings.items():
            if param_name not in execute_attributes:
                execute_attributes[param_name] = None  # Placeholder for blackboard mapping
                setattr(node, '_execute_attributes', execute_attributes)

        # Validate node parameters against execute method signature
        if execute_attributes:
            self._validate_node_parameters(node, execute_attributes)

        # Ensure node has children attribute initialized
        if not hasattr(node, 'children'):
            node.children = []
        if not hasattr(node, 'parent'):
            node.parent = None
        if not hasattr(node, 'status'):
            node.status = Status.FAILURE
        if not hasattr(node, '_last_tick_time'):
            node._last_tick_time = 0.0

        # 设置参数映射关系
        for node_attr, blackboard_key in param_mappings.items():
            node.set_param_mapping(node_attr, blackboard_key)

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
        attributes: Dict[str, Any] = {}
        param_mappings: Dict[str, str] = {}

        for key, value in element.attrib.items():
            if key == "name":
                continue  # name attribute handled separately

            # Process variable substitution in string values
            if isinstance(value, str) and "{" in value and "}" in value:
                # Check if it is parameter mapping format: attr_name="{blackboard_key}"
                import re
                # Modify regular expression to ensure it can correctly match {blackboard_key} format
                mapping_match = re.match(r'^\{([^}]+)\}$', value)
                if mapping_match:
                    # This is parameter mapping format
                    blackboard_key = mapping_match.group(1)
                    param_mappings[key] = blackboard_key
                    # Don't add to attributes since this is a parameter mapping
                    # The value will be resolved at execution time
                else:
                    # This is variable substitution format
                    value = self._substitute_variables(value)
                    attributes[key] = value
            else:
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
                except (ValueError, TypeError):
                    attributes[key] = value

        # Add parameter mapping information to attributes for subsequent processing
        if param_mappings:
            attributes["_param_mappings"] = param_mappings

        return attributes

    def _substitute_variables(self, value: str) -> str:
        """
        Substitute variables in string values
        
        Args:
            value: String value that may contain {variable} placeholders
            
        Returns:
            String with variables substituted
        """
        import re
        
        # Define available variables
        variables = {
            "message": "Hello World",  # Default message
            "topic": "news",           # Default topic
            "duration": "1.0",         # Default duration
            "timeout": "2.0",          # Default timeout
        }
        
        # Find all {variable} patterns and replace them
        def replace_var(match):
            var_name = match.group(1)
            return variables.get(var_name, match.group(0))
        
        return re.sub(r'\{(\w+)\}', replace_var, value)


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
    
    <Communication>
        <ComTopic name="service_events">
            <ComPublisher service="TriggerService" />
            <ComSubscriber service="MonitorService" />
        </ComTopic>
        <ComShared>
            <ComKey name="robots_enabled" />
            <ComKey name="timer_enabled" />
        </ComShared>
    </Communication>
</BehaviorForest>
""" 