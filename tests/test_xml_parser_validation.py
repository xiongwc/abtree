#!/usr/bin/env python3
"""
Test XML Parser Validation

Tests for XML parser validation logic, specifically for BehaviorTree structure validation.
"""

import pytest
from abtree.parser.xml_parser import XMLParser
from abtree import Action, register_node
from abtree.core import Status


class TestAction(Action):
    """Test action node for testing"""
    
    async def execute(self):
        return Status.SUCCESS


class TestAction2(Action):
    """Another test action node for testing"""
    
    async def execute(self):
        return Status.SUCCESS


class TestXMLParserValidation:
    """Test class for XML parser validation"""
    
    def setup_method(self):
        """Setup method to register test nodes"""
        register_node("TestAction", TestAction)
        register_node("TestAction2", TestAction2)
        self.parser = XMLParser()
    
    def test_valid_single_root_node(self):
        """Test that a BehaviorTree with a single root node is valid"""
        xml_config = """
        <BehaviorTree name="TestTree">
            <TestAction name="RootAction" />
        </BehaviorTree>
        """
        
        # Should not raise any exception
        result = self.parser.parse_string(xml_config)
        assert result is not None
        assert result.name == "TestTree"
    
    def test_valid_sequence_root_node(self):
        """Test that a BehaviorTree with a Sequence as root node is valid"""
        xml_config = """
        <BehaviorTree name="TestTree">
            <Sequence name="RootSequence">
                <TestAction name="Action1" />
                <TestAction2 name="Action2" />
            </Sequence>
        </BehaviorTree>
        """
        
        # Should not raise any exception
        result = self.parser.parse_string(xml_config)
        assert result is not None
        assert result.name == "TestTree"
    
    def test_invalid_multiple_root_nodes(self):
        """Test that a BehaviorTree with multiple direct child nodes raises an exception"""
        xml_config = """
        <BehaviorTree name="TestTree">
            <TestAction name="Action1" />
            <TestAction2 name="Action2" />
        </BehaviorTree>
        """
        
        # Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            self.parser.parse_string(xml_config)
        
        error_message = str(exc_info.value)
        assert "BehaviorTree can only have one root node" in error_message
        assert "TestAction" in error_message
        assert "TestAction2" in error_message
        assert "wrap multiple nodes in a composite node" in error_message
    
    def test_invalid_multiple_different_node_types(self):
        """Test that a BehaviorTree with multiple different node types raises an exception"""
        xml_config = """
        <BehaviorTree name="TestTree">
            <Log name="LogNode" message="test" />
            <TestAction name="ActionNode" />
        </BehaviorTree>
        """
        
        # Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            self.parser.parse_string(xml_config)
        
        error_message = str(exc_info.value)
        assert "BehaviorTree can only have one root node" in error_message
        assert "Log" in error_message
        assert "TestAction" in error_message
    
    def test_empty_behavior_tree(self):
        """Test that an empty BehaviorTree returns None for root node"""
        xml_config = """
        <BehaviorTree name="TestTree">
        </BehaviorTree>
        """
        
        # Should raise ValueError for no root node
        with pytest.raises(ValueError) as exc_info:
            self.parser.parse_string(xml_config)
        
        error_message = str(exc_info.value)
        assert "Root node not found in behavior tree" in error_message
    
    def test_behavior_tree_with_only_root_tags(self):
        """Test that a BehaviorTree with only Root tags returns None for root node"""
        xml_config = """
        <BehaviorTree name="TestTree">
            <Root>
                <TestAction name="Action1" />
            </Root>
        </BehaviorTree>
        """
        
        # Should raise ValueError for no root node (Root tags are ignored)
        with pytest.raises(ValueError) as exc_info:
            self.parser.parse_string(xml_config)
        
        error_message = str(exc_info.value)
        assert "Root node not found in behavior tree" in error_message
    
    def test_valid_behavior_forest_with_multiple_trees(self):
        """Test that a BehaviorForest with multiple trees is valid"""
        xml_config = """
        <BehaviorForest name="TestForest">
            <BehaviorTree name="Tree1">
                <TestAction name="Action1" />
            </BehaviorTree>
            <BehaviorTree name="Tree2">
                <TestAction2 name="Action2" />
            </BehaviorTree>
        </BehaviorForest>
        """
        
        # Should not raise any exception
        result = self.parser.parse_string(xml_config)
        assert result is not None
        assert result.name == "TestForest"
    
    def test_invalid_behavior_forest_with_invalid_tree(self):
        """Test that a BehaviorForest with an invalid tree raises an exception"""
        xml_config = """
        <BehaviorForest name="TestForest">
            <BehaviorTree name="Tree1">
                <TestAction name="Action1" />
                <TestAction2 name="Action2" />
            </BehaviorTree>
        </BehaviorForest>
        """
        
        # Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            self.parser.parse_string(xml_config)
        
        error_message = str(exc_info.value)
        assert "BehaviorTree can only have one root node" in error_message
    
    def test_complex_valid_structure(self):
        """Test a complex but valid structure with nested composite nodes"""
        xml_config = """
        <BehaviorTree name="TestTree">
            <Selector name="RootSelector">
                <Sequence name="Sequence1">
                    <TestAction name="Action1" />
                    <TestAction2 name="Action2" />
                </Sequence>
                <Sequence name="Sequence2">
                    <TestAction name="Action3" />
                    <TestAction2 name="Action4" />
                </Sequence>
            </Selector>
        </BehaviorTree>
        """
        
        # Should not raise any exception
        result = self.parser.parse_string(xml_config)
        assert result is not None
        assert result.name == "TestTree"
    
    def test_error_message_includes_suggestions(self):
        """Test that the error message includes helpful suggestions"""
        xml_config = """
        <BehaviorTree name="TestTree">
            <TestAction name="Action1" />
            <TestAction2 name="Action2" />
            <Log name="LogNode" message="test" />
        </BehaviorTree>
        """
        
        with pytest.raises(ValueError) as exc_info:
            self.parser.parse_string(xml_config)
        
        error_message = str(exc_info.value)
        assert "wrap multiple nodes in a composite node" in error_message
        assert "Sequence" in error_message
        assert "Selector" in error_message
        assert "Parallel" in error_message 