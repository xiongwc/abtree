"""
Test XML Parser Unregistered Nodes

This test suite verifies that the XML parser correctly throws exceptions
when encountering unregistered node types in XML configurations.
"""

import pytest
from abtree.parser.xml_parser import XMLParser
from abtree.registry.node_registry import register_node, get_global_registry


class TestXMLParserUnregisteredNodes:
    """Test cases for XML parser unregistered node handling"""

    def test_unregistered_node_in_behavior_tree(self):
        """Test that XML parser throws exception for unregistered node in behavior tree"""
        xml_config = """
        <BehaviorTree name="TestTree">
            <UnregisteredNode name="test" />
        </BehaviorTree>
        """
        
        parser = XMLParser()
        
        with pytest.raises(ValueError) as exc_info:
            parser.parse_string(xml_config)
        
        error_message = str(exc_info.value)
        assert "UnregisteredNode" in error_message
        assert "are not registered" in error_message
        assert "Available registered node types" in error_message

    def test_unregistered_node_in_behavior_forest(self):
        """Test that XML parser throws exception for unregistered node in behavior forest"""
        xml_config = """
        <BehaviorForest name="TestForest">
            <BehaviorTree name="TestTree">
                <UnregisteredNode name="test" />
            </BehaviorTree>
        </BehaviorForest>
        """
        
        parser = XMLParser()
        
        with pytest.raises(ValueError) as exc_info:
            parser.parse_string(xml_config)
        
        error_message = str(exc_info.value)
        assert "UnregisteredNode" in error_message
        assert ("are not registered" in error_message or "is not registered" in error_message)

    def test_multiple_unregistered_nodes(self):
        """Test that XML parser throws exception for multiple unregistered nodes"""
        xml_config = """
        <BehaviorTree name="TestTree">
            <Sequence name="root">
                <UnregisteredNode1 name="test1" />
                <UnregisteredNode2 name="test2" />
            </Sequence>
        </BehaviorTree>
        """
        
        parser = XMLParser()
        
        with pytest.raises(ValueError) as exc_info:
            parser.parse_string(xml_config)
        
        error_message = str(exc_info.value)
        assert "UnregisteredNode1" in error_message
        assert ("are not registered" in error_message or "is not registered" in error_message)

    def test_llm_agent_unregistered_nodes(self):
        """Test that XML parser throws exception for LLMModel and LLMChat nodes when not registered"""
        xml_config = """
        <BehaviorForest name="LLMForest">
            <BehaviorTree name="LLMTree">
                <CommExternalInput name="chat_input" channel="chat_input" timeout="3.0" data="{messages}"/>
                <Log message="{messages}" />
                <LLMModel api_key="your-api-key" api_base="https://api.openai.com/v1" model="gpt-3.5-turbo" />
                <LLMChat model="{model}" messages="{messages}" />
                <CommExternalOutput name="chat_output" channel="chat_output" data="{response}"/>
            </BehaviorTree>
        </BehaviorForest>
        """
        
        parser = XMLParser()
        
        with pytest.raises(ValueError) as exc_info:
            parser.parse_string(xml_config)
        
        error_message = str(exc_info.value)
        assert "LLMModel" in error_message
        assert ("are not registered" in error_message or "is not registered" in error_message)

    def test_registered_node_works(self):
        """Test that XML parser works correctly with registered nodes"""
        xml_config = """
        <BehaviorTree name="TestTree">
            <Log name="test" message="Hello World" />
        </BehaviorTree>
        """
        
        parser = XMLParser()
        result = parser.parse_string(xml_config)
        
        assert result is not None
        assert hasattr(result, 'name')
        assert result.name == "TestTree"

    def test_registered_node_after_registration(self):
        """Test that XML parser works after registering custom nodes"""
        # Define a simple test node class
        from abtree.nodes.base import BaseNode
        from abtree.core.status import Status
        
        class TestNode(BaseNode):
            def __init__(self, name: str = ""):
                super().__init__(name)
                
            async def execute(self, param1: str = None):
                return Status.SUCCESS
                
            async def tick(self):
                return Status.SUCCESS
        
        # Register the node
        register_node("TestNode", TestNode)
        
        xml_config = """
        <BehaviorTree name="TestTree">
            <TestNode name="test" param1="value" />
        </BehaviorTree>
        """
        
        parser = XMLParser()
        result = parser.parse_string(xml_config)
        
        assert result is not None
        assert hasattr(result, 'name')
        assert result.name == "TestTree"

    def test_error_message_includes_available_nodes(self):
        """Test that error message includes list of available registered nodes"""
        xml_config = """
        <BehaviorTree name="TestTree">
            <UnregisteredNode name="test" />
        </BehaviorTree>
        """
        
        parser = XMLParser()
        
        with pytest.raises(ValueError) as exc_info:
            parser.parse_string(xml_config)
        
        error_message = str(exc_info.value)
        
        # Check that error message includes available node types
        assert "Available registered node types" in error_message
        
        # Check that some common built-in nodes are mentioned
        registry = get_global_registry()
        registered_nodes = registry.get_registered()
        
        # Verify that at least some built-in nodes are mentioned
        common_nodes = ["Log", "Sequence", "Selector"]
        for node in common_nodes:
            if node in registered_nodes:
                assert node in error_message

    def test_error_message_includes_registration_instructions(self):
        """Test that error message includes instructions for registering custom nodes"""
        xml_config = """
        <BehaviorTree name="TestTree">
            <UnregisteredNode name="test" />
        </BehaviorTree>
        """
        
        parser = XMLParser()
        
        with pytest.raises(ValueError) as exc_info:
            parser.parse_string(xml_config)
        
        error_message = str(exc_info.value)
        
        # Check that error message includes registration instructions
        assert "register_node" in error_message
        assert "YourNodeClass" in error_message

    def test_nested_unregistered_nodes(self):
        """Test that XML parser throws exception for unregistered nodes in nested structures"""
        xml_config = """
        <BehaviorTree name="TestTree">
            <Sequence name="root">
                <Log name="log1" message="First log" />
                <Selector name="selector">
                    <UnregisteredNode name="test" />
                    <Log name="log2" message="Second log" />
                </Selector>
            </Sequence>
        </BehaviorTree>
        """
        
        parser = XMLParser()
        
        with pytest.raises(ValueError) as exc_info:
            parser.parse_string(xml_config)
        
        error_message = str(exc_info.value)
        assert "UnregisteredNode" in error_message
        assert ("are not registered" in error_message or "is not registered" in error_message)

    def test_unregistered_node_with_attributes(self):
        """Test that XML parser throws exception for unregistered node with attributes"""
        xml_config = """
        <BehaviorTree name="TestTree">
            <UnregisteredNode name="test" attr1="value1" attr2="value2" />
        </BehaviorTree>
        """
        
        parser = XMLParser()
        
        with pytest.raises(ValueError) as exc_info:
            parser.parse_string(xml_config)
        
        error_message = str(exc_info.value)
        assert "UnregisteredNode" in error_message
        assert ("are not registered" in error_message or "is not registered" in error_message)

    def test_unregistered_node_with_parameter_mapping(self):
        """Test that XML parser throws exception for unregistered node with parameter mapping"""
        xml_config = """
        <BehaviorTree name="TestTree">
            <UnregisteredNode name="test" param1="{blackboard_key}" />
        </BehaviorTree>
        """
        
        parser = XMLParser()
        
        with pytest.raises(ValueError) as exc_info:
            parser.parse_string(xml_config)
        
        error_message = str(exc_info.value)
        assert "UnregisteredNode" in error_message
        assert ("are not registered" in error_message or "is not registered" in error_message)

    def test_cleanup_after_test(self):
        """Test cleanup to ensure no side effects from previous tests"""
        # This test ensures that the registry is clean after previous tests
        registry = get_global_registry()
        
        # Clean up any test nodes that might have been registered
        if "TestNode" in registry.get_registered():
            registry.unregister("TestNode")
        if "LLMModel" in registry.get_registered():
            registry.unregister("LLMModel")
        if "LLMChat" in registry.get_registered():
            registry.unregister("LLMChat")
        
        # Verify that test nodes are not registered
        assert "TestNode" not in registry.get_registered()
        assert "LLMModel" not in registry.get_registered()
        assert "LLMChat" not in registry.get_registered()
        
        # Verify that UnregisteredNode is not registered
        assert "UnregisteredNode" not in registry.get_registered()


class TestXMLParserUnregisteredNodesIntegration:
    """Integration tests for XML parser unregistered node handling"""

    def test_llm_agent_example_without_registration(self):
        """Test the actual LLM Agent example without node registration"""
        xml_config = """
        <BehaviorForest name="LLMForest">
            <BehaviorTree name="LLMTree">
                <CommExternalInput name="chat_input" channel="chat_input" timeout="3.0" data="{messages}"/>
                <Log message="{messages}" />
                <LLMModel api_key="your-api-key" api_base="https://api.openai.com/v1" model="gpt-3.5-turbo" />
                <LLMChat model="{model}" messages="{messages}" />
                <CommExternalOutput name="chat_output" channel="chat_output" data="{response}"/>
            </BehaviorTree>
        </BehaviorForest>
        """
        
        parser = XMLParser()
        
        with pytest.raises(ValueError) as exc_info:
            parser.parse_string(xml_config)
        
        error_message = str(exc_info.value)
        assert "LLMModel" in error_message
        assert ("are not registered" in error_message or "is not registered" in error_message)

    def test_llm_agent_example_with_registration(self):
        """Test the LLM Agent example with proper node registration"""
        # Define mock LLM node classes
        from abtree.nodes.base import BaseNode
        from abtree.core.status import Status
        
        class MockLLMModel(BaseNode):
            def __init__(self, name: str = ""):
                super().__init__(name)
                
            async def execute(self, api_key: str = None, api_base: str = None, model: str = None):
                return Status.SUCCESS
                
            async def tick(self):
                return Status.SUCCESS
        
        class MockLLMChat(BaseNode):
            def __init__(self, name: str = ""):
                super().__init__(name)
                
            async def execute(self, model=None, messages: str = None, response=None, stream: bool = True):
                return Status.SUCCESS
                
            async def tick(self):
                return Status.SUCCESS
        
        # Register the nodes
        register_node("LLMModel", MockLLMModel)
        register_node("LLMChat", MockLLMChat)
        
        xml_config = """
        <BehaviorForest name="LLMForest">
            <BehaviorTree name="LLMTree">
                <Sequence name="LLMSequence">
                    <CommExternalInput name="chat_input" channel="chat_input" timeout="3.0" data="{messages}"/>
                    <Log message="{messages}" />
                    <LLMModel api_key="your-api-key" api_base="https://api.openai.com/v1" model="gpt-3.5-turbo" />
                    <LLMChat model="{model}" messages="{messages}" />
                    <CommExternalOutput name="chat_output" channel="chat_output" data="{response}"/>
                </Sequence>
            </BehaviorTree>
        </BehaviorForest>
        """
        
        parser = XMLParser()
        result = parser.parse_string(xml_config)
        
        assert result is not None
        assert hasattr(result, 'name')
        assert result.name == "LLMForest"
        assert len(result.nodes) == 1
        assert "LLMTree" in result.nodes 