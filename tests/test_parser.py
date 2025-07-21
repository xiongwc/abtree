import pytest
import tempfile
import os
from abtree.parser.xml_parser import XMLParser
from abtree.parser.tree_builder import TreeBuilder
from abtree.engine.behavior_tree import BehaviorTree
from abtree.forest.core import BehaviorForest

SIMPLE_TREE_XML = '''
<BehaviorTree name="TestTree">
    <Sequence name="TestSequence">
        <AlwaysTrue name="TestCondition"/>
    </Sequence>
</BehaviorTree>
'''

SIMPLE_FOREST_XML = '''
<BehaviorForest name="TestForest">
    <BehaviorTree name="Tree1">
        <Sequence name="Seq1">
            <AlwaysTrue name="Cond1"/>
        </Sequence>
    </BehaviorTree>
    <BehaviorTree name="Tree2">
        <Sequence name="Seq2">
            <AlwaysTrue name="Cond2"/>
        </Sequence>
    </BehaviorTree>
</BehaviorForest>
'''

COMPLEX_TREE_XML = '''
<BehaviorTree name="ComplexTree" description="A complex behavior tree">
    <Selector name="RootSelector">
        <Sequence name="SuccessPath">
            <AlwaysTrue name="Condition1"/>
            <AlwaysTrue name="Condition2"/>
        </Sequence>
        <Sequence name="FallbackPath">
            <AlwaysFalse name="Condition3"/>
            <AlwaysTrue name="Condition4"/>
        </Sequence>
    </Selector>
</BehaviorTree>
'''

FOREST_WITH_COMMUNICATION_XML = '''
<BehaviorForest name="CommunicationForest">
    <BehaviorTree name="PublisherTree">
        <Sequence name="PublisherSeq">
            <AlwaysTrue name="PublisherCond"/>
        </Sequence>
    </BehaviorTree>
    <BehaviorTree name="SubscriberTree">
        <Sequence name="SubscriberSeq">
            <AlwaysTrue name="SubscriberCond"/>
        </Sequence>
    </BehaviorTree>
    <Communication>
        <ComTopic name="test_topic">
            <ComPublisher service="PublisherTree"/>
            <ComSubscriber service="SubscriberTree"/>
        </ComTopic>
    </Communication>
</BehaviorForest>
'''

def test_parse_string_tree():
    parser = XMLParser()
    tree = parser.parse_string(SIMPLE_TREE_XML)
    assert isinstance(tree, BehaviorTree)
    assert tree.name == "TestTree"
    assert tree.root is not None

def test_parse_string_forest():
    parser = XMLParser()
    forest = parser.parse_string(SIMPLE_FOREST_XML)
    assert isinstance(forest, BehaviorForest)
    assert forest.name == "TestForest"
    assert len(forest.nodes) == 2

def test_parse_string_invalid():
    parser = XMLParser()
    with pytest.raises(ValueError):
        parser.parse_string("<InvalidRoot></InvalidRoot>")

def test_parse_complex_tree():
    parser = XMLParser()
    tree = parser.parse_string(COMPLEX_TREE_XML)
    assert isinstance(tree, BehaviorTree)
    assert tree.name == "ComplexTree"
    assert tree.description == "A complex behavior tree"
    assert tree.root is not None
    assert tree.root.name == "RootSelector"

def test_parse_forest_with_communication():
    parser = XMLParser()
    forest = parser.parse_string(FOREST_WITH_COMMUNICATION_XML)
    assert isinstance(forest, BehaviorForest)
    assert forest.name == "CommunicationForest"
    assert len(forest.nodes) == 2
    assert len(forest.middleware) > 0

def test_parse_file():
    parser = XMLParser()
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        f.write(SIMPLE_TREE_XML)
        temp_file = f.name
    
    try:
        tree = parser.parse_file(temp_file)
        assert isinstance(tree, BehaviorTree)
        assert tree.name == "TestTree"
    finally:
        os.unlink(temp_file)

def test_parse_file_not_found():
    parser = XMLParser()
    with pytest.raises(ValueError):
        parser.parse_file("nonexistent_file.xml")

def test_tree_builder_basic():
    builder = TreeBuilder()
    tree = builder.build_tree({
        "name": "TestTree",
        "description": "Test Description",
        "root": {
            "type": "Sequence",
            "name": "RootSeq",
            "children": [
                {"type": "AlwaysTrue", "name": "Cond1"},
                {"type": "AlwaysTrue", "name": "Cond2"}
            ]
        }
    })
    assert isinstance(tree, BehaviorTree)
    assert tree.name == "TestTree"

def test_tree_builder_with_attributes():
    builder = TreeBuilder()
    tree = builder.build_tree({
        "name": "AttrTree",
        "root": {
            "type": "Repeater",
            "name": "RepeatNode",
            "repeat_count": 3,
            "children": [
                {"type": "AlwaysTrue", "name": "Child"}
            ]
        }
    })
    assert isinstance(tree, BehaviorTree)
    assert tree.name == "AttrTree"

def test_tree_builder_invalid_node_type():
    builder = TreeBuilder()
    try:
        builder.build_tree({
            "name": "InvalidTree",
            "root": {
                "type": "InvalidNodeType",
                "name": "InvalidNode"
            }
        })
        assert False, "Expected ValueError for invalid node type"
    except ValueError:
        pass

def test_tree_builder_empty_tree():
    builder = TreeBuilder()
    try:
        builder.build_tree({
            "name": "EmptyTree"
        })
        assert False, "Expected ValueError for empty tree"
    except ValueError:
        pass

def test_xml_parser_attributes():
    parser = XMLParser()
    
    xml_with_attrs = '''
    <BehaviorTree name="AttrTree" description="Tree with attributes">
        <Repeater name="RepeatNode" repeat_count="3">
            <AlwaysTrue name="Child"/>
        </Repeater>
    </BehaviorTree>
    '''
    
    tree = parser.parse_string(xml_with_attrs)
    assert isinstance(tree, BehaviorTree)
    assert tree.name == "AttrTree"
    assert tree.description == "Tree with attributes"

def test_xml_parser_nested_structure():
    parser = XMLParser()
    
    nested_xml = '''
    <BehaviorTree name="NestedTree">
        <Selector name="RootSel">
            <Sequence name="Seq1">
                <AlwaysTrue name="Cond1"/>
                <AlwaysTrue name="Cond2"/>
            </Sequence>
            <Sequence name="Seq2">
                <AlwaysFalse name="Cond3"/>
                <AlwaysTrue name="Cond4"/>
            </Sequence>
        </Selector>
    </BehaviorTree>
    '''
    
    tree = parser.parse_string(nested_xml)
    assert isinstance(tree, BehaviorTree)
    assert tree.name == "NestedTree"
    assert tree.root.name == "RootSel"
    assert len(tree.root.children) == 2

def test_xml_parser_error_handling():
    parser = XMLParser()
    
    # Test malformed XML
    with pytest.raises(ValueError):
        parser.parse_string("<BehaviorTree><unclosed_tag>")
    
    # Test empty XML
    with pytest.raises(ValueError):
        parser.parse_string("")
    
    # Test XML without root node
    with pytest.raises(ValueError):
        parser.parse_string("<BehaviorTree></BehaviorTree>")

def test_tree_builder_complex_structure():
    builder = TreeBuilder()
    complex_tree = {
        "name": "ComplexTree",
        "description": "A complex tree structure",
        "root": {
            "type": "Parallel",
            "name": "RootParallel",
            "policy": "SUCCEED_ON_ALL",
            "children": [
                {
                    "type": "Sequence",
                    "name": "Seq1",
                    "children": [
                        {"type": "AlwaysTrue", "name": "Cond1"},
                        {"type": "AlwaysTrue", "name": "Cond2"}
                    ]
                },
                {
                    "type": "Selector",
                    "name": "Sel1",
                    "children": [
                        {"type": "AlwaysFalse", "name": "Cond3"},
                        {"type": "AlwaysTrue", "name": "Cond4"}
                    ]
                }
            ]
        }
    }
    tree = builder.build_tree(complex_tree)
    assert isinstance(tree, BehaviorTree)
    assert tree.name == "ComplexTree"

def test_xml_parser_forest_node_types():
    parser = XMLParser()
    
    forest_xml = '''
    <BehaviorForest name="TypedForest">
        <BehaviorTree name="MasterTree">
            <AlwaysTrue name="MasterCond"/>
        </BehaviorTree>
        <BehaviorTree name="WorkerTree">
            <AlwaysTrue name="WorkerCond"/>
        </BehaviorTree>
        <BehaviorTree name="MonitorTree">
            <AlwaysTrue name="MonitorCond"/>
        </BehaviorTree>
    </BehaviorForest>
    '''
    
    forest = parser.parse_string(forest_xml)
    assert isinstance(forest, BehaviorForest)
    assert forest.name == "TypedForest"
    assert len(forest.nodes) == 3
    
    # Check that node types are determined correctly
    master_node = forest.get_node("MasterTree")
    worker_node = forest.get_node("WorkerTree")
    monitor_node = forest.get_node("MonitorTree")
    
    assert master_node is not None
    assert worker_node is not None
    assert monitor_node is not None 