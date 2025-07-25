import pytest
from abtree.nodes.base import BaseNode
from abtree.nodes.composite import Sequence, Selector, Parallel
from abtree.nodes.decorator import Inverter, Repeater, UntilSuccess, UntilFailure, Decorator
from abtree.nodes.action import Action, Log, SetBlackboard, Wait
from abtree.nodes.condition import Condition, CheckBlackboard, IsTrue, IsFalse, Compare, AlwaysTrue, AlwaysFalse
from abtree.core.status import Status
from abtree.engine.blackboard import Blackboard

class DummyNode(BaseNode):
    async def tick(self):
        return Status.SUCCESS

class DummyFailureNode(BaseNode):
    async def tick(self):
        return Status.FAILURE

class DummyAction(Action):
    async def execute(self):
        return Status.SUCCESS

class DummyCondition(Condition):
    async def evaluate(self):
        return True

class DummyDecorator(Decorator):
    async def tick(self):
        return await self.child.tick()

@pytest.mark.asyncio
async def test_sequence_node():
    """Test sequence node functionality"""
    # Create test nodes
    success_node = DummyNode("success")
    failure_node = DummyFailureNode("failure")
    
    # Create sequence with success nodes
    seq = Sequence("test_sequence", [success_node, success_node])
    blackboard = Blackboard()
    seq.set_blackboard(blackboard)
    
    # Test successful sequence
    result = await seq.tick()
    assert result == Status.SUCCESS
    
    # Create sequence with failure node
    seq = Sequence("test_sequence", [success_node, failure_node])
    seq.set_blackboard(blackboard)
    
    # Test failed sequence
    result = await seq.tick()
    assert result == Status.FAILURE

@pytest.mark.asyncio
async def test_selector_node():
    """Test selector node functionality"""
    # Create test nodes
    success_node = DummyNode("success")
    failure_node = DummyFailureNode("failure")
    
    # Create selector with success node
    sel = Selector("test_selector", [success_node, failure_node])
    blackboard = Blackboard()
    sel.set_blackboard(blackboard)
    
    # Test successful selector
    result = await sel.tick()
    assert result == Status.SUCCESS
    
    # Create selector with only failure nodes
    sel = Selector("test_selector", [failure_node, failure_node])
    sel.set_blackboard(blackboard)
    
    # Test failed selector
    result = await sel.tick()
    assert result == Status.FAILURE

@pytest.mark.asyncio
async def test_parallel_node():
    """Test parallel node functionality"""
    # Create test nodes
    success_node = DummyNode("success")
    failure_node = DummyFailureNode("failure")
    
    # Create parallel with all success nodes
    par = Parallel("test_parallel", [success_node, success_node])
    blackboard = Blackboard()
    par.set_blackboard(blackboard)
    
    # Test successful parallel
    result = await par.tick()
    assert result == Status.SUCCESS

@pytest.mark.asyncio
async def test_inverter_node():
    """Test inverter node functionality"""
    # Create test nodes
    success_node = DummyNode("success")
    
    # Create inverter with success node
    inverter = Inverter("test_inverter", child=success_node)
    blackboard = Blackboard()
    inverter.set_blackboard(blackboard)
    
    # Test inverted result
    result = await inverter.tick()
    assert result == Status.FAILURE

@pytest.mark.asyncio
async def test_repeater_node():
    """Test repeater node functionality"""
    # Create test node
    success_node = DummyNode("success")
    
    # Create repeater
    repeater = Repeater("test_repeater", child=success_node, repeat_count=2)
    blackboard = Blackboard()
    repeater.set_blackboard(blackboard)
    
    # Test repeater
    result = await repeater.tick()
    assert result == Status.RUNNING

@pytest.mark.asyncio
async def test_until_success_node():
    """Test until success node functionality"""
    # Create test node
    success_node = DummyNode("success")
    
    # Create until success
    until_success = UntilSuccess("test_until_success", child=success_node)
    blackboard = Blackboard()
    until_success.set_blackboard(blackboard)
    
    # Test until success
    result = await until_success.tick()
    assert result == Status.SUCCESS

@pytest.mark.asyncio
async def test_until_failure_node():
    """Test until failure node functionality"""
    # Create test node
    failure_node = DummyFailureNode("failure")
    
    # Create until failure
    until_failure = UntilFailure("test_until_failure", child=failure_node)
    blackboard = Blackboard()
    until_failure.set_blackboard(blackboard)
    
    # Test until failure
    result = await until_failure.tick()
    assert result == Status.SUCCESS

@pytest.mark.asyncio
async def test_decorator_node():
    """Test decorator node functionality"""
    # Create test node
    success_node = DummyNode("success")
    
    # Create decorator
    decorator = DummyDecorator("test_decorator", success_node)
    blackboard = Blackboard()
    decorator.set_blackboard(blackboard)
    
    # Test decorator
    result = await decorator.tick()
    assert result == Status.SUCCESS

@pytest.mark.asyncio
async def test_action_node():
    """Test action node functionality"""
    # Create action node
    action = DummyAction("test_action")
    blackboard = Blackboard()
    action.set_blackboard(blackboard)
    
    # Test action
    result = await action.tick()
    assert result == Status.SUCCESS

@pytest.mark.asyncio
async def test_log_node():
    """Test log node functionality"""
    # Create log node
    log = Log("test_log", "Test message")
    blackboard = Blackboard()
    log.set_blackboard(blackboard)
    
    # Test log
    result = await log.tick()
    assert result == Status.SUCCESS

@pytest.mark.asyncio
async def test_wait_node():
    """Test wait node functionality"""
    # Create wait node
    wait = Wait("test_wait", 0.1)
    blackboard = Blackboard()
    wait.set_blackboard(blackboard)
    
    # Test wait (first tick should be running)
    result = await wait.tick()
    assert result == Status.RUNNING
    
    # Wait a bit and test again
    import asyncio
    await asyncio.sleep(0.15)
    result = await wait.tick()
    assert result == Status.SUCCESS

@pytest.mark.asyncio
async def test_condition_node():
    """Test condition node functionality"""
    # Create condition node
    condition = DummyCondition("test_condition")
    blackboard = Blackboard()
    condition.set_blackboard(blackboard)
    
    # Test condition
    result = await condition.tick()
    assert result == Status.SUCCESS

@pytest.mark.asyncio
async def test_check_blackboard_node():
    """Test check blackboard node functionality"""
    # Create blackboard
    blackboard = Blackboard()
    blackboard.set("test_key", "test_value")
    
    # Create check blackboard node
    check = CheckBlackboard("test_check", "test_key", "test_value")
    check.set_blackboard(blackboard)
    
    # Test check
    result = await check.tick()
    assert result == Status.SUCCESS

@pytest.mark.asyncio
async def test_is_true_node():
    """Test is true node functionality"""
    # Create blackboard
    blackboard = Blackboard()
    blackboard.set("test_key", True)
    
    # Create is true node
    is_true = IsTrue("test_is_true", "test_key")
    is_true.set_blackboard(blackboard)
    
    # Test is true
    result = await is_true.tick()
    assert result == Status.SUCCESS

@pytest.mark.asyncio
async def test_is_false_node():
    """Test is false node functionality"""
    # Create blackboard
    blackboard = Blackboard()
    blackboard.set("test_key", False)
    
    # Create is false node
    is_false = IsFalse("test_is_false", "test_key")
    is_false.set_blackboard(blackboard)
    
    # Test is false
    result = await is_false.tick()
    assert result == Status.SUCCESS

@pytest.mark.asyncio
async def test_compare_node():
    """Test compare node functionality"""
    # Create blackboard
    blackboard = Blackboard()
    blackboard.set("test_key", 10)
    
    # Create compare node
    compare = Compare("test_compare", "test_key", "==", 10)
    compare.set_blackboard(blackboard)
    
    # Test compare
    result = await compare.tick()
    assert result == Status.SUCCESS

@pytest.mark.asyncio
async def test_always_true_node():
    """Test always true node functionality"""
    # Create always true node
    always_true = AlwaysTrue("test_always_true")
    blackboard = Blackboard()
    always_true.set_blackboard(blackboard)
    
    # Test always true
    result = await always_true.tick()
    assert result == Status.SUCCESS

@pytest.mark.asyncio
async def test_always_false_node():
    """Test always false node functionality"""
    # Create always false node
    always_false = AlwaysFalse("test_always_false")
    blackboard = Blackboard()
    always_false.set_blackboard(blackboard)
    
    # Test always false
    result = await always_false.tick()
    assert result == Status.FAILURE

@pytest.mark.asyncio
async def test_sequence_with_blackboard():
    """Test sequence node with blackboard integration"""
    # Create blackboard
    blackboard = Blackboard()
    blackboard.set("counter", 0)
    
    # Create sequence with nodes that use blackboard
    seq = Sequence("test_sequence", [DummyNode("node1"), DummyNode("node2")])
    seq.set_blackboard(blackboard)
    
    # Test sequence
    result = await seq.tick()
    assert result == Status.SUCCESS 