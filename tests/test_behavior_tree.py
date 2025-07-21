"""
Behavior Tree Integration Tests

Test the complete functionality of the behavior tree, including creation, execution, status management, etc.
"""

import asyncio

import pytest

from abtree import BehaviorTree, Inverter, Parallel, Selector, Sequence
from abtree.core import Policy, Status
from abtree.nodes.action import Action, Wait
from abtree.nodes.condition import Condition


class TestAction(Action):
    """Test action node for testing"""

    def __init__(self, name: str, return_status: Status = Status.SUCCESS):
        super().__init__(name)
        self.return_status = return_status
        self.execution_count = 0

    async def execute(self, blackboard):
        self.execution_count += 1
        return self.return_status


class TestCondition(Condition):
    """Test condition node for testing"""

    def __init__(self, name: str, return_value: bool = True):
        super().__init__(name)
        self.return_value = return_value
        self.evaluation_count = 0

    async def evaluate(self, blackboard):
        self.evaluation_count += 1
        return self.return_value


class TestBehaviorTree:
    """Test behavior tree"""

    def setup_method(self):
        """Set up test environment"""
        self.blackboard = None

    def test_tree_creation(self):
        """Test behavior tree creation"""
        root = Sequence("root")
        tree = BehaviorTree(name="test_tree")
        tree.load_from_root(root)

        assert tree.name == "test_tree"
        assert tree.root == root
        assert tree.blackboard is not None

    def test_tree_execution_simple(self):
        """Test simple behavior tree execution"""
        # Create a simple behavior tree
        root = Sequence("root")
        action1 = TestAction("action1")
        action2 = TestAction("action2")

        root.add_child(action1)
        root.add_child(action2)

        tree = BehaviorTree(name="simple_tree")
        tree.load_from_root(root)

        # Execute behavior tree
        result = asyncio.run(tree.tick())

        assert result == Status.SUCCESS
        assert action1.execution_count == 1
        assert action2.execution_count == 1

    def test_tree_execution_with_conditions(self):
        """Test behavior tree execution with conditions"""
        # Create a behavior tree with conditions
        root = Selector("root")

        # First branch: condition is true
        branch1 = Sequence("branch1")
        condition1 = TestCondition("condition1", True)
        action1 = TestAction("action1")
        branch1.add_child(condition1)
        branch1.add_child(action1)

        # Second branch: condition is false
        branch2 = Sequence("branch2")
        condition2 = TestCondition("condition2", False)
        action2 = TestAction("action2")
        branch2.add_child(condition2)
        branch2.add_child(action2)

        root.add_child(branch1)
        root.add_child(branch2)

        tree = BehaviorTree(name="conditional_tree")
        tree.load_from_root(root)

        # Execute behavior tree
        result = asyncio.run(tree.tick())

        assert result == Status.SUCCESS
        assert condition1.evaluation_count == 1
        assert action1.execution_count == 1
        assert condition2.evaluation_count == 0  # Will not execute
        assert action2.execution_count == 0  # Will not execute

    def test_tree_execution_with_failure(self):
        """Test behavior tree execution with failure"""
        # Create a behavior tree with failure
        root = Sequence("root")
        action1 = TestAction("action1", Status.SUCCESS)
        action2 = TestAction("action2", Status.FAILURE)
        action3 = TestAction("action3", Status.SUCCESS)

        root.add_child(action1)
        root.add_child(action2)
        root.add_child(action3)

        tree = BehaviorTree(name="failure_tree")
        tree.load_from_root(root)

        # Execute behavior tree
        result = asyncio.run(tree.tick())

        assert result == Status.FAILURE
        assert action1.execution_count == 1
        assert action2.execution_count == 1
        assert action3.execution_count == 0  # Will not execute

    def test_tree_execution_with_parallel(self):
        """Test parallel behavior tree execution"""
        # Create a parallel behavior tree
        root = Parallel("root", policy=Policy.SUCCEED_ON_ALL)
        action1 = TestAction("action1", Status.SUCCESS)
        action2 = TestAction("action2", Status.SUCCESS)

        root.add_child(action1)
        root.add_child(action2)

        tree = BehaviorTree(name="parallel_tree")
        tree.load_from_root(root)

        # Execute behavior tree
        result = asyncio.run(tree.tick())

        assert result == Status.SUCCESS
        assert action1.execution_count == 1
        assert action2.execution_count == 1

    def test_tree_execution_with_inverter(self):
        """Test behavior tree execution with inverter"""
        # Create a behavior tree with inverter
        root = Sequence("root")
        action = TestAction("action", Status.SUCCESS)
        inverter = Inverter("inverter", child=action)

        root.add_child(inverter)

        tree = BehaviorTree(name="inverter_tree")
        tree.load_from_root(root)

        # Execute behavior tree
        result = asyncio.run(tree.tick())

        assert result == Status.FAILURE  # Success is inverted to failure
        assert action.execution_count == 1

    def test_tree_blackboard_operations(self):
        """Test behavior tree blackboard operations"""
        root = Sequence("root")
        tree = BehaviorTree(name="blackboard_tree")
        tree.load_from_root(root)
        # Confirm blackboard type
        from abtree.core.blackboard import Blackboard

        assert isinstance(tree.blackboard, Blackboard)
        # Directly use blackboard.set
        tree.blackboard.set("test_key", "test_value")
        assert tree.get_blackboard_data("test_key") == "test_value"
        # Get a non-existent key
        assert tree.get_blackboard_data("nonexistent_key", "default") == "default"

    def test_tree_multiple_ticks(self):
        """Test multiple executions of behavior tree"""
        root = Sequence("root")
        action = TestAction("action", Status.SUCCESS)
        root.add_child(action)

        tree = BehaviorTree(name="multi_tick_tree")
        tree.load_from_root(root)

        # Execute multiple times
        for i in range(3):
            result = asyncio.run(tree.tick())
            assert result == Status.SUCCESS

        assert action.execution_count == 3

    def test_tree_with_running_status(self):
        """Test behavior tree with running status"""

        class RunningAction(Action):
            def __init__(self, name: str, max_runs: int = 2):
                super().__init__(name)
                self.max_runs = max_runs
                self.run_count = 0

            async def execute(self, blackboard):
                self.run_count += 1
                if self.run_count >= self.max_runs:
                    return Status.SUCCESS
                return Status.RUNNING

        root = Sequence("root")
        action = RunningAction("running_action", 3)
        root.add_child(action)

        tree = BehaviorTree(name="running_tree")
        tree.load_from_root(root)

        # First execution
        result1 = asyncio.run(tree.tick())
        assert result1 == Status.RUNNING
        assert action.run_count == 1

        # Second execution
        result2 = asyncio.run(tree.tick())
        assert result2 == Status.RUNNING
        assert action.run_count == 2

        # Third execution
        result3 = asyncio.run(tree.tick())
        assert result3 == Status.SUCCESS
        assert action.run_count == 3

    def test_tree_complex_scenario(self):
        """Test complex scenario behavior tree"""
        # Create a complex behavior tree
        root = Selector("root")

        # High priority branch
        high_priority = Sequence("high_priority")
        high_condition = TestCondition("high_condition", True)
        high_action = TestAction("high_action")
        high_priority.add_child(high_condition)
        high_priority.add_child(high_action)

        # Low priority branch
        low_priority = Sequence("low_priority")
        low_condition = TestCondition("low_condition", False)
        low_action = TestAction("low_action")
        low_priority.add_child(low_condition)
        low_priority.add_child(low_action)

        # Default branch
        default_branch = Sequence("default_branch")
        default_action = TestAction("default_action")
        default_branch.add_child(default_action)

        root.add_child(high_priority)
        root.add_child(low_priority)
        root.add_child(default_branch)

        tree = BehaviorTree(name="complex_tree")
        tree.load_from_root(root)

        # Execute behavior tree
        result = asyncio.run(tree.tick())

        assert result == Status.SUCCESS
        assert high_condition.evaluation_count == 1
        assert high_action.execution_count == 1
        assert low_condition.evaluation_count == 0  # Will not execute
        assert low_action.execution_count == 0  # Will not execute
        assert default_action.execution_count == 0  # Will not execute


if __name__ == "__main__":
    pytest.main([__file__])
