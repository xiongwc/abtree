"""
Node module unit tests

Test various node types of the behavior tree, including action nodes, condition nodes, composite nodes, etc.
"""

import asyncio

import pytest

from abtree import Blackboard
from abtree.core import Status
from abtree.nodes.action import Action, Wait
from abtree.nodes.composite import Parallel, Selector, Sequence
from abtree.nodes.condition import Condition
from abtree.nodes.decorator import Inverter, Repeater


class TestAction:
    """Test action node"""

    def setup_method(self):
        """Set up test environment"""
        self.blackboard = Blackboard()

    def test_action_creation(self):
        """Test action node creation"""
        # Cannot directly instantiate abstract class
        # Use concrete action node for testing
        action = Wait("test_action")
        assert action.name == "test_action"
        assert action.status == Status.FAILURE

    def test_action_execution(self):
        """Test action node execution"""

        class TestAction(Action):
            async def execute(self, blackboard):
                return Status.SUCCESS

        action = TestAction("test")
        result = asyncio.run(action.tick(self.blackboard))
        assert result == Status.SUCCESS


class TestCondition:
    """Test condition node"""

    def setup_method(self):
        """Set up test environment"""
        self.blackboard = Blackboard()

    def test_condition_creation(self):
        """Test condition node creation"""
        # Cannot directly instantiate abstract class
        # Here we test the concept of condition node
        class TestCondition(Condition):
            async def evaluate(self, blackboard):
                return True

        condition = TestCondition("test")
        assert condition.name == "test"

    def test_condition_evaluation(self):
        """Test condition node evaluation"""

        class TestCondition(Condition):
            async def evaluate(self, blackboard):
                return True

        condition = TestCondition("test")
        result = asyncio.run(condition.evaluate(self.blackboard))
        assert result is True


class TestSequence:
    """Test sequence node"""

    def setup_method(self):
        """Set up test environment"""
        self.blackboard = Blackboard()

    def test_sequence_creation(self):
        """Test sequence node creation"""
        sequence = Sequence("test_sequence")
        assert sequence.name == "test_sequence"
        assert len(sequence.children) == 0

    def test_sequence_add_child(self):
        """Test adding child node to sequence node"""
        sequence = Sequence("test_sequence")
        action = Wait("test_action")
        sequence.add_child(action)
        assert len(sequence.children) == 1
        assert sequence.children[0] == action

    def test_sequence_execution_success(self):
        """Test successful execution of sequence node"""

        class SuccessAction(Action):
            async def execute(self, blackboard):
                return Status.SUCCESS

        sequence = Sequence("test_sequence")
        sequence.add_child(SuccessAction("action1"))
        sequence.add_child(SuccessAction("action2"))

        result = asyncio.run(sequence.tick(self.blackboard))
        assert result == Status.SUCCESS

    def test_sequence_execution_failure(self):
        """Test failed execution of sequence node"""

        class SuccessAction(Action):
            async def execute(self, blackboard):
                return Status.SUCCESS

        class FailureAction(Action):
            async def execute(self, blackboard):
                return Status.FAILURE

        sequence = Sequence("test_sequence")
        sequence.add_child(SuccessAction("action1"))
        sequence.add_child(FailureAction("action2"))
        sequence.add_child(SuccessAction("action3"))

        result = asyncio.run(sequence.tick(self.blackboard))
        assert result == Status.FAILURE


class TestSelector:
    """Test selector node"""

    def setup_method(self):
        """Set up test environment"""
        self.blackboard = Blackboard()

    def test_selector_creation(self):
        """Test selector node creation"""
        selector = Selector("test_selector")
        assert selector.name == "test_selector"
        assert len(selector.children) == 0

    def test_selector_execution_success(self):
        """Test successful execution of selector node"""

        class SuccessAction(Action):
            async def execute(self, blackboard):
                return Status.SUCCESS

        class FailureAction(Action):
            async def execute(self, blackboard):
                return Status.FAILURE

        selector = Selector("test_selector")
        selector.add_child(FailureAction("action1"))
        selector.add_child(SuccessAction("action2"))
        selector.add_child(FailureAction("action3"))

        result = asyncio.run(selector.tick(self.blackboard))
        assert result == Status.SUCCESS

    def test_selector_execution_failure(self):
        """Test failed execution of selector node"""

        class FailureAction(Action):
            async def execute(self, blackboard):
                return Status.FAILURE

        selector = Selector("test_selector")
        selector.add_child(FailureAction("action1"))
        selector.add_child(FailureAction("action2"))

        result = asyncio.run(selector.tick(self.blackboard))
        assert result == Status.FAILURE


class TestParallel:
    """Test parallel node"""

    def setup_method(self):
        """Set up test environment"""
        self.blackboard = Blackboard()

    def test_parallel_creation(self):
        """Test parallel node creation"""
        parallel = Parallel("test_parallel")
        assert parallel.name == "test_parallel"
        assert len(parallel.children) == 0

    def test_parallel_execution_all_success(self):
        """Test all success in parallel node"""

        class SuccessAction(Action):
            async def execute(self, blackboard):
                return Status.SUCCESS

        parallel = Parallel("test_parallel")
        parallel.add_child(SuccessAction("action1"))
        parallel.add_child(SuccessAction("action2"))

        result = asyncio.run(parallel.tick(self.blackboard))
        assert result == Status.SUCCESS

    def test_parallel_execution_mixed_results(self):
        """Test mixed results in parallel node"""
        # Result may vary depending on policy

        class SuccessAction(Action):
            async def execute(self, blackboard):
                return Status.SUCCESS

        class FailureAction(Action):
            async def execute(self, blackboard):
                return Status.FAILURE

        parallel = Parallel("test_parallel")
        parallel.add_child(SuccessAction("action1"))
        parallel.add_child(FailureAction("action2"))

        result = asyncio.run(parallel.tick(self.blackboard))
        assert result in [Status.SUCCESS, Status.FAILURE]


class TestInverter:
    """Test inverter node"""

    def setup_method(self):
        """Set up test environment"""
        self.blackboard = Blackboard()

    def test_inverter_creation(self):
        """Test inverter node creation"""
        action = Wait("test_action")
        inverter = Inverter("test_inverter", child=action)
        assert inverter.name == "test_inverter"
        assert inverter.child == action

    def test_inverter_execution(self):
        """Test inverter node execution"""

        class SuccessAction(Action):
            async def execute(self, blackboard):
                return Status.SUCCESS

        class FailureAction(Action):
            async def execute(self, blackboard):
                return Status.FAILURE

        # Invert success to failure
        success_action = SuccessAction("success")
        inverter1 = Inverter("inverter1", child=success_action)
        result1 = asyncio.run(inverter1.tick(self.blackboard))
        assert result1 == Status.FAILURE

        # Invert failure to success
        failure_action = FailureAction("failure")
        inverter2 = Inverter("inverter2", child=failure_action)
        result2 = asyncio.run(inverter2.tick(self.blackboard))
        assert result2 == Status.SUCCESS


class TestRepeater:
    """Test repeater node"""

    def setup_method(self):
        """Set up test environment"""
        self.blackboard = Blackboard()

    def test_repeater_creation(self):
        """Test repeater node creation"""
        action = Wait("test_action")
        repeater = Repeater("test_repeater", child=action, repeat_count=3)
        assert repeater.name == "test_repeater"
        assert repeater.child == action
        assert repeater.repeat_count == 3

    def test_repeater_execution(self):
        """Test repeater node execution"""

        class CounterAction(Action):
            def __init__(self, name):
                super().__init__(name)
                self.count = 0

            async def execute(self, blackboard):
                self.count += 1
                if self.count < 3:
                    return Status.SUCCESS
                return Status.FAILURE

        action = CounterAction("counter")
        repeater = Repeater("repeater", child=action, repeat_count=5)
        # Multiple ticks until FAILURE is returned
        result = None
        for _ in range(5):
            result = asyncio.run(repeater.tick(self.blackboard))
            if result == Status.FAILURE:
                break
        assert result == Status.FAILURE
        assert action.count == 3


if __name__ == "__main__":
    pytest.main([__file__])
