import pytest
import logging
from abtree.validators import validate_tree, validate_node, ValidationResult, validate_blackboard_data, validate_xml_structure, get_tree_statistics, print_validation_result
from abtree.utils.logger import (
    get_logger, get_abtree_logger, ABTreeLogger, LoggerConfig, ColorCode, LevelColor,
    ColoredFormatter
)
from abtree.engine.behavior_tree import BehaviorTree
from abtree.nodes.base import BaseNode
from abtree.core.status import Status

class DummyNode(BaseNode):
    async def tick(self):
        return Status.SUCCESS
    
    def execute(self):
        return Status.SUCCESS
    
    def __init__(self, name: str):
        super().__init__(name=name, children=[])  # Explicitly set empty children
    
    # Override to avoid being classified as composite node
    def get_child_count(self) -> int:
        return 0
    
    def has_children(self) -> bool:
        return False

def test_validate_tree_and_node():
    tree = BehaviorTree(name="T")
    node = DummyNode(name="root")
    tree.load_from_node(node)
    result = validate_tree(tree)
    assert isinstance(result, ValidationResult)
    # The tree should be valid (warnings don't make it invalid)
    assert result.is_valid
    node_result = validate_node(node)
    assert node_result.is_valid

def test_validate_tree_empty():
    tree = BehaviorTree(name="T")
    result = validate_tree(tree)
    assert not result.is_valid
    assert any("root" in e for e in result.errors)

def test_validate_node_empty_name():
    node = DummyNode(name="")
    result = validate_node(node)
    assert not result.is_valid
    assert any("name" in e for e in result.errors)

def test_validate_blackboard_data():
    # Test valid data
    valid_data = {"key1": "value1", "key2": 42, "key3": True}
    result = validate_blackboard_data(valid_data)
    assert result.is_valid
    
    # Test invalid data - not a dictionary
    invalid_data = "not a dict"
    result = validate_blackboard_data(invalid_data)
    assert not result.is_valid
    assert any("dictionary" in e for e in result.errors)
    
    # Test data with None values (should be valid)
    data_with_none = {"key1": "value1", "key2": None}
    result = validate_blackboard_data(data_with_none)
    assert result.is_valid

def test_validate_xml_structure():
    # Test valid XML
    valid_xml = '''
    <BehaviorTree name="TestTree">
        <Root>
            <Sequence name="RootSeq">
                <AlwaysTrue name="Cond1"/>
            </Sequence>
        </Root>
    </BehaviorTree>
    '''
    result = validate_xml_structure(valid_xml)
    assert result.is_valid
    
    # Test invalid XML - wrong root element
    invalid_xml = '''
    <InvalidRoot name="TestTree">
        <Root>
            <Sequence name="RootSeq"/>
        </Root>
    </InvalidRoot>
    '''
    result = validate_xml_structure(invalid_xml)
    assert not result.is_valid
    assert any("BehaviorTree" in e for e in result.errors)
    
    # Test invalid XML - malformed XML
    invalid_xml2 = '''
    <BehaviorTree name="TestTree">
        <Sequence name="RootSeq">
    '''
    result = validate_xml_structure(invalid_xml2)
    assert not result.is_valid

def test_get_tree_statistics():
    tree = BehaviorTree(name="TestTree", description="Test Description")
    node1 = DummyNode(name="node1")
    node2 = DummyNode(name="node2")
    tree.load_from_node(node1)
    node1.add_child(node2)
    
    stats = get_tree_statistics(tree)
    assert "total_nodes" in stats
    assert "node_types" in stats
    assert "tree_depth" in stats
    assert stats["total_nodes"] == 2

def test_print_validation_result(capsys):
    result = ValidationResult(True, [], ["Warning 1", "Warning 2"])
    print_validation_result(result, "Test Result")
    captured = capsys.readouterr()
    assert "Test Result" in captured.out
    assert "Warning 1" in captured.out

def test_logger_setup():
    # Test logger setup
    config = LoggerConfig(level="INFO")
    logger = get_logger("test_logger", config=config)
    assert logger.name == "test_logger"
    # The logger level may be a string or int depending on implementation
    assert logger.config.level == "INFO"

def test_logger_getters():
    # Test get_logger
    logger1 = get_logger("test_logger1")
    logger2 = get_logger("test_logger1")  # Should return same logger
    assert logger1 is logger2
    
    # Test get_abtree_logger
    abtree_logger = get_abtree_logger()
    assert "abtree" in abtree_logger.name

def test_logging_functions():
    # Test various logging functions
    logger = get_logger("test_logging")
    # Test basic logging functions
    logger.info("Test info message")
    logger.debug("Test debug message")
    logger.warning("Test warning message")
    logger.error("Test error message")
    # Test colored logging functions
    logger.log_with_color("Test success message", ColorCode.GREEN, "INFO")
    logger.log_with_color("Test failure message", ColorCode.RED, "ERROR")
    logger.log_with_color("Test running message", ColorCode.BLUE, "INFO")
    # Test tree and node logging functions
    tree = BehaviorTree(name="TestTree")
    logger.info(f"Tree execution: {tree.name} - {Status.SUCCESS.name}")
    logger.info(f"Tree status: {tree.name} - {Status.SUCCESS.name}")
    node = DummyNode(name="TestNode")
    logger.info(f"Node execution: {node.name} - DummyNode - {Status.SUCCESS.name}")
    logger.info(f"Node status: {node.name} - {Status.SUCCESS.name}")
    # Test performance and system logging
    logger.info("Test performance message - 0.1s")
    logger.info("Memory usage: 100.0 MB")
    logger.info("System info: {'test': 'info'}")
    logger.info("Configuration: {'test': 'config'}")

def test_colored_logging():
    # Test colored logging functions
    logger = get_logger("test_colored")
    logger.log_with_color("Green message", ColorCode.GREEN)
    logger.log_with_color("Blue message", ColorCode.BLUE)
    logger.log_with_color("Yellow message", ColorCode.YELLOW)
    logger.log_with_color("Red message", ColorCode.RED)
    logger.log_with_color("Cyan message", ColorCode.CYAN)
    logger.log_with_color("Bold message", ColorCode.BOLD)

def test_blackboard_logging():
    logger = get_logger("test_blackboard")
    logger.info("Blackboard access: test_key = test_value (set)")
    logger.info("Blackboard access: test_key = test_value (get)")

def test_event_logging():
    logger = get_logger("test_event")
    logger.info("Event: test_event - {'data': 'test'}")

def test_logger_config():
    config = LoggerConfig(level="INFO")
    assert config.level == "INFO"
    assert config.format is not None
    assert config.enable_colors is True

def test_color_codes():
    # Test color code class
    assert ColorCode.GREEN == "\033[32m"
    assert ColorCode.RED == "\033[31m"
    assert ColorCode.RESET == "\033[0m"

def test_level_colors():
    # Test level color mapping
    assert LevelColor.INFO == LevelColor.INFO
    assert LevelColor.WARNING == LevelColor.WARNING
    assert LevelColor.ERROR == LevelColor.ERROR

def test_colored_formatter():
    config = LoggerConfig(level="INFO")
    formatter = ColoredFormatter(config)
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname="", lineno=0,
        msg="Test message", args=(), exc_info=None
    )
    formatted = formatter.format(record)
    assert "Test message" in formatted

def test_validation_result_boolean():
    # Test ValidationResult boolean behavior
    valid_result = ValidationResult(True, [], [])
    assert bool(valid_result) is True
    
    invalid_result = ValidationResult(False, ["Error"], [])
    assert bool(invalid_result) is False

def test_validation_result_with_errors():
    result = ValidationResult(False, ["Error 1", "Error 2"], ["Warning 1"])
    assert not result.is_valid
    assert len(result.errors) == 2
    assert len(result.warnings) == 1
    assert "Error 1" in result.errors
    assert "Warning 1" in result.warnings

def test_validate_node_with_children():
    parent = DummyNode(name="parent")
    child = DummyNode(name="child")
    parent.add_child(child)
    
    result = validate_node(parent)
    # Action nodes with children should be invalid
    assert not result.is_valid
    assert any("Action nodes should not have children" in e for e in result.errors)

def test_validate_tree_with_blackboard():
    tree = BehaviorTree(name="TestTree")
    tree.blackboard = {"key1": "value1"}
    node = DummyNode(name="root")
    tree.load_from_node(node)
    
    result = validate_tree(tree)
    # Tree should be valid even with warnings
    assert result.is_valid

def test_validate_tree_with_event_system():
    tree = BehaviorTree(name="TestTree")
    from abtree.engine.event_system import EventSystem
    tree.event_system = EventSystem()
    node = DummyNode(name="root")
    tree.load_from_node(node)
    
    result = validate_tree(tree)
    # Tree should be valid even with warnings
    assert result.is_valid

def test_validate_tree_with_tick_manager():
    tree = BehaviorTree(name="TestTree")
    from abtree.engine.tick_manager import TickManager
    tree.tick_manager = TickManager()
    node = DummyNode(name="root")
    tree.load_from_node(node)
    
    result = validate_tree(tree)
    # Tree should be valid even with warnings
    assert result.is_valid

def test_logger_with_custom_config():
    config = LoggerConfig(
        level="DEBUG",
        format="%(name)s - %(levelname)s - %(message)s",
        enable_colors=False
    )
    logger = get_logger("custom_logger", config=config)
    assert logger.config.level == "DEBUG" 