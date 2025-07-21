"""
Pytest configuration file

Set up test environment and shared fixtures.
"""

import asyncio

import pytest

from abtree import BehaviorTree, Sequence
from abtree.core.blackboard import Blackboard


@pytest.fixture
def blackboard():
    """Provide blackboard instance"""
    return Blackboard()


@pytest.fixture
def simple_tree():
    """Provide simple behavior tree instance"""
    root = Sequence("test_root")
    tree = BehaviorTree(root, name="test_tree")
    return tree


@pytest.fixture(autouse=True)
def event_loop():
    """Provide event loop"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_data():
    """Provide test data"""
    return {
        "string_value": "test_string",
        "int_value": 42,
        "float_value": 3.14,
        "bool_value": True,
        "list_value": [1, 2, 3],
        "dict_value": {"key": "value"},
        "none_value": None,
    }


@pytest.fixture
def sample_blackboard_data(test_data):
    """Provide blackboard with sample data"""
    blackboard = Blackboard()
    for key, value in test_data.items():
        blackboard.set(key, value)
    return blackboard


class MockAction:
    """Mock action node"""

    def __init__(self, name: str, return_status="SUCCESS", execution_count=0):
        self.name = name
        self.return_status = return_status
        self.execution_count = execution_count

    async def execute(self, blackboard):
        self.execution_count += 1
        return getattr(Status, self.return_status)


class MockCondition:
    """Mock condition node"""

    def __init__(self, name: str, return_value=True, evaluation_count=0):
        self.name = name
        self.return_value = return_value
        self.evaluation_count = evaluation_count

    async def evaluate(self, blackboard):
        self.evaluation_count += 1
        return self.return_value


@pytest.fixture
def mock_action():
    """Provide mock action node"""
    return MockAction("mock_action")


@pytest.fixture
def mock_condition():
    """Provide mock condition node"""
    return MockCondition("mock_condition")


@pytest.fixture
def mock_success_action():
    """Provide success action node"""
    return MockAction("success_action", "SUCCESS")


@pytest.fixture
def mock_failure_action():
    """Provide failure action node"""
    return MockAction("failure_action", "FAILURE")


@pytest.fixture
def mock_running_action():
    """Provide running action node"""
    return MockAction("running_action", "RUNNING")


@pytest.fixture
def mock_true_condition():
    """Provide true condition node"""
    return MockCondition("true_condition", True)


@pytest.fixture
def mock_false_condition():
    """Provide false condition node"""
    return MockCondition("false_condition", False)


# Test report hooks (temporarily disabled to avoid dependency issues)
# def pytest_html_report_title(report):
#     """Set HTML report title"""
#     report.title = "ABTree Test Report"
#
# def pytest_html_results_summary(prefix, summary, postfix):
#     """Custom test result summary"""
#     prefix.extend([
#         "<h2>Test Coverage</h2>",
#         "<ul>",
#         "<li>Core module tests</li>",
#         "<li>Node type tests</li>",
#         "<li>Behavior tree integration tests</li>",
#         "</ul>"
#     ])
