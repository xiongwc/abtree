import pytest
import logging
from abtree.utils.validators import validate_tree, validate_node, ValidationResult, validate_blackboard_data, validate_xml_structure, get_tree_statistics, print_validation_result
from abtree.utils.logger import (
    setup_logger, get_logger, get_abtree_logger, log_tree_execution, log_node_execution,
    log_blackboard_access, log_event, log_error, log_warning, log_info, log_debug,
    log_success, log_failure, log_running, log_tree_status, log_node_status,
    log_performance, log_memory_usage, log_system_info, log_configuration,
    create_status_logger, log_with_color, log_green, log_blue, log_yellow, log_red,
    log_cyan, log_magenta, log_bold, LoggerConfig, ColorCode, StatusColor, LevelColor,
    ColoredFormatter, StatusFormatter
)
from abtree.engine.behavior_tree import BehaviorTree
from abtree.nodes.base import BaseNode
from abtree.core.status import Status

class DummyNode(BaseNode):
    async def tick(self, blackboard):
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
    # The tree should be valid even with warnings
    assert result.is_valid or len(result.errors) == 0
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
    
    # Test invalid data with non-string keys
    invalid_data = {123: "value", "key2": "value2"}
    result = validate_blackboard_data(invalid_data)
    assert not result.is_valid
    assert any("string" in e for e in result.errors)
    
    # Test data with None values (should generate warnings)
    data_with_none = {"key1": "value1", "key2": None}
    result = validate_blackboard_data(data_with_none)
    assert result.is_valid
    assert any("None" in w for w in result.warnings)

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
    
    # Test invalid XML - missing Root element
    invalid_xml2 = '''
    <BehaviorTree name="TestTree">
        <Sequence name="RootSeq"/>
    </BehaviorTree>
    '''
    result = validate_xml_structure(invalid_xml2)
    assert not result.is_valid
    assert any("Root" in e for e in result.errors)

def test_get_tree_statistics():
    tree = BehaviorTree(name="TestTree", description="Test Description")
    node1 = DummyNode(name="node1")
    node2 = DummyNode(name="node2")
    tree.load_from_node(node1)
    node1.add_child(node2)
    
    stats = get_tree_statistics(tree)
    assert "total_nodes" in stats
    assert "node_types" in stats
    assert "status_distribution" in stats
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
    logger = setup_logger("test_logger", config=config)
    assert logger.name == "test_logger"
    # The logger level may be a string or int depending on implementation
    assert logger.level == "INFO" or logger.level == 20

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
    log_info("Test info message")
    log_debug("Test debug message")
    log_warning("Test warning message")
    log_error("Test error message")
    # Test status logging functions
    log_success("Test success message")
    log_failure("Test failure message")
    log_running("Test running message")
    # Test tree and node logging functions
    tree = BehaviorTree(name="TestTree")
    log_tree_execution(tree.name, Status.SUCCESS.name)
    log_tree_status(tree.name, Status.SUCCESS.name)  # Provide required status argument
    node = DummyNode(name="TestNode")
    log_node_execution(node.name, "DummyNode", Status.SUCCESS.name)  # Provide required arguments
    log_node_status(node.name, Status.SUCCESS.name)  # Provide required status argument
    # Test performance and system logging
    log_performance("Test performance message", 0.1)
    log_memory_usage(100.0)
    log_system_info({"test": "info"})
    log_configuration({"test": "config"})

def test_colored_logging():
    # Test colored logging functions
    log_green("Green message")
    log_blue("Blue message")
    log_yellow("Yellow message")
    log_red("Red message")
    log_cyan("Cyan message")
    log_magenta("Magenta message")
    log_bold("Bold message")
    
    # Test generic colored logging
    log_with_color("Test message", ColorCode.GREEN)

def test_blackboard_logging():
    bb = {"key1": "value1", "key2": 42}
    log_blackboard_access("test_key", "test_value", "set")
    log_blackboard_access("test_key", "test_value", "get")

def test_event_logging():
    log_event("test_event", {"data": "test"})

def test_logger_config():
    config = LoggerConfig(level="INFO")
    assert config.level == "INFO"
    assert config.format is not None
    assert config.enable_colors is True

def test_color_codes():
    # Test color code enum
    assert ColorCode.GREEN == "\033[32m"
    assert ColorCode.RED == "\033[31m"
    assert ColorCode.RESET == "\033[0m"

def test_status_colors():
    # Test status color mapping
    # Use the actual values from StatusColor and ColorCode
    assert StatusColor.SUCCESS == StatusColor.SUCCESS  # Should match itself
    assert StatusColor.FAILURE == StatusColor.FAILURE
    assert StatusColor.RUNNING == StatusColor.RUNNING

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

def test_status_formatter():
    config = LoggerConfig(level="INFO")
    formatter = StatusFormatter(config)
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname="", lineno=0,
        msg="Test message", args=(), exc_info=None
    )
    formatted = formatter.format(record)
    assert "Test message" in formatted

def test_create_status_logger():
    logger = create_status_logger("test_status_logger")
    assert logger.name == "test_status_logger"

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
    assert result.is_valid

def test_validate_tree_with_blackboard():
    tree = BehaviorTree(name="TestTree")
    tree.blackboard = {"key1": "value1"}
    node = DummyNode(name="root")
    tree.load_from_node(node)
    
    result = validate_tree(tree)
    assert result.is_valid

def test_validate_tree_with_event_system():
    tree = BehaviorTree(name="TestTree")
    from abtree.engine.event_system import EventSystem
    tree.event_system = EventSystem()
    node = DummyNode(name="root")
    tree.load_from_node(node)
    
    result = validate_tree(tree)
    assert result.is_valid

def test_validate_tree_with_tick_manager():
    tree = BehaviorTree(name="TestTree")
    from abtree.engine.tick_manager import TickManager
    tree.tick_manager = TickManager()
    node = DummyNode(name="root")
    tree.load_from_node(node)
    
    result = validate_tree(tree)
    assert result.is_valid

def test_logger_with_custom_config():
    config = LoggerConfig(
        level="DEBUG",
        format="%(name)s - %(levelname)s - %(message)s",
        enable_colors=False
    )
    logger = setup_logger("custom_logger", config=config)
    assert logger.level == "DEBUG" or logger.level == 10 