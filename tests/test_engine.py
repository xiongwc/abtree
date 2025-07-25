import pytest
import asyncio
from abtree.engine.behavior_tree import BehaviorTree
from abtree.engine.blackboard import Blackboard
from abtree.engine.event_system import EventSystem
from abtree.engine.tick_manager import TickManager
from abtree.core.status import Status
from abtree.nodes.base import BaseNode

class DummyNode(BaseNode):
    async def tick(self):
        return Status.SUCCESS

class FailingNode(BaseNode):
    async def tick(self):
        return Status.FAILURE

class RunningNode(BaseNode):
    def __init__(self, name: str, max_ticks: int = 3):
        super().__init__(name=name)
        self.max_ticks = max_ticks
        self.tick_count = 0
    
    async def tick(self):
        self.tick_count += 1
        if self.tick_count >= self.max_ticks:
            return Status.SUCCESS
        return Status.RUNNING

def test_blackboard_basic():
    bb = Blackboard()
    bb.set('a', 1)
    assert bb.get('a') == 1
    assert bb.has('a')
    assert bb.remove('a')
    assert not bb.has('a')
    bb.set('b', 2)
    bb.clear()
    assert len(bb) == 0

def test_blackboard_operations():
    bb = Blackboard()
    bb.set('key1', 'value1')
    bb.set('key2', 42)
    bb.set('key3', [1, 2, 3])
    
    assert bb.get('key1') == 'value1'
    assert bb.get('key2') == 42
    assert bb.get('key3') == [1, 2, 3]
    assert bb.get('nonexistent', 'default') == 'default'
    
    assert 'key1' in bb
    assert 'nonexistent' not in bb
    
    assert bb.keys() == ['key1', 'key2', 'key3']
    assert len(bb.values()) == 3
    assert len(bb.items()) == 3

@pytest.mark.asyncio
async def test_blackboard_async():
    bb = Blackboard()
    await bb.set_async('x', 42)
    assert await bb.get_async('x') == 42
    assert await bb.has_async('x')
    async with bb.transaction() as bbt:
        bbt.set('y', 99)
    assert bb.get('y') == 99

def test_blackboard_dict_operations():
    bb = Blackboard()
    bb['key1'] = 'value1'
    assert bb['key1'] == 'value1'
    assert 'key1' in bb
    del bb['key1']
    assert 'key1' not in bb

@pytest.mark.asyncio
async def test_event_system_basic():
    es = EventSystem()
    
    # Test emit and wait
    await es.emit('test', source='test_source')
    success = await es.wait_for('test', timeout=1.0)
    assert success
    
    # Test event info
    info = es.get_event_info('test')
    assert info is not None
    assert info.name == 'test'
    assert info.source == 'test_source'
    assert info.trigger_count == 1

@pytest.mark.asyncio
async def test_event_system_advanced():
    es = EventSystem()
    
    # Test multiple events
    await es.emit('event1', source='source1')
    await es.emit('event2', source='source2')
    
    # Test wait for any
    triggered_event = await es.wait_for_any(['event1', 'event2'], timeout=1.0)
    assert triggered_event in ['event1', 'event2']
    
    # Test wait for all
    success = await es.wait_for_all(['event1', 'event2'], timeout=1.0)
    assert success
    
    # Test event info
    info1 = es.get_event_info('event1')
    info2 = es.get_event_info('event2')
    assert info1 is not None
    assert info2 is not None
    assert info1.source == 'source1'
    assert info2.source == 'source2'

@pytest.mark.asyncio
async def test_event_system_global_listeners():
    es = EventSystem()
    
    # Create global listener
    global_listener = es.create_global_listener()
    
    # Emit events
    await es.emit('event1', source='source1')
    await es.emit('event2', source='source2')
    
    # Wait for global listener to be triggered
    await global_listener.wait()
    
    # Check that global listener was triggered
    assert global_listener.is_set()
    
    # Clean up
    es.remove_global_listener(global_listener)

@pytest.mark.asyncio
async def test_behavior_tree_tick():
    tree = BehaviorTree()
    node = DummyNode(name='root')
    tree.load_from_node(node)
    result = await tree.tick()
    assert result == Status.SUCCESS
    assert tree.root == node
    tree.reset()
    assert tree.root.status == Status.FAILURE

@pytest.mark.asyncio
async def test_behavior_tree_event_emit():
    tree = BehaviorTree()
    node = DummyNode(name='root')
    tree.load_from_node(node)
    
    # Start a task to wait for the event
    event_task = asyncio.create_task(
        tree.event_system.wait_for('tree_tick_start', timeout=1.0)
    )
    
    # Execute tick which should trigger the event
    await tree.tick()
    
    # Wait for the event
    success = await event_task
    assert success

@pytest.mark.asyncio
async def test_behavior_tree_with_failing_node():
    tree = BehaviorTree()
    node = FailingNode(name='root')
    tree.load_from_node(node)
    result = await tree.tick()
    assert result == Status.FAILURE

@pytest.mark.asyncio
async def test_behavior_tree_with_running_node():
    tree = BehaviorTree()
    node = RunningNode(name='root', max_ticks=2)
    tree.load_from_node(node)
    
    # First tick should return RUNNING
    result = await tree.tick()
    assert result == Status.RUNNING
    
    # Second tick should return SUCCESS
    result = await tree.tick()
    assert result == Status.SUCCESS

def test_behavior_tree_node_operations():
    tree = BehaviorTree()
    node1 = DummyNode(name='node1')
    node2 = DummyNode(name='node2')
    
    tree.load_from_node(node1)
    assert tree.find_node('node1') == node1
    assert tree.find_node('node2') is None
    
    tree.set_root(node2)
    assert tree.root == node2
    assert tree.find_node('node2') == node2

def test_behavior_tree_blackboard_operations():
    tree = BehaviorTree()
    tree.set_blackboard_data('test_key', 'test_value')
    assert tree.get_blackboard_data('test_key') == 'test_value'
    assert tree.get_blackboard_data('nonexistent', 'default') == 'default'

def test_behavior_tree_stats():
    tree = BehaviorTree(name='TestTree', description='Test Description')
    node = DummyNode(name='root')
    tree.load_from_node(node)
    
    stats = tree.get_tree_stats()
    assert stats['name'] == 'TestTree'
    assert stats['description'] == 'Test Description'
    assert stats['has_root'] is True
    assert stats['total_nodes'] == 1

@pytest.mark.asyncio
async def test_tick_manager_basic():
    tm = TickManager()
    node = DummyNode(name='root')
    tm.set_root_node(node)
    tm.set_blackboard(Blackboard())
    
    result = await tm.tick_once()
    assert result == Status.SUCCESS

@pytest.mark.asyncio
async def test_tick_manager_with_callbacks():
    tm = TickManager()
    node = DummyNode(name='root')
    tm.set_root_node(node)
    tm.set_blackboard(Blackboard())
    
    tick_called = False
    status_changed = False
    
    def on_tick(status):
        nonlocal tick_called
        tick_called = True
    
    def on_status_change(old_status, new_status):
        nonlocal status_changed
        status_changed = True
    
    tm.set_on_tick_callback(on_tick)
    tm.set_on_status_change_callback(on_status_change)
    
    await tm.tick_once()
    assert tick_called
    assert status_changed

def test_tick_manager_configuration():
    tm = TickManager(tick_rate=30.0)
    assert tm.tick_rate == 30.0
    
    tm.set_tick_rate(60.0)
    assert tm.tick_rate == 60.0
    
    stats = tm.get_stats()
    assert 'tick_count' in stats
    assert 'running' in stats

@pytest.mark.asyncio
async def test_tick_manager_start_stop():
    tm = TickManager()
    node = DummyNode(name='root')
    tm.set_root_node(node)
    tm.set_blackboard(Blackboard())
    
    # Start tick manager
    start_task = asyncio.create_task(tm.start())
    await asyncio.sleep(0.1)  # Let it run briefly
    
    # Stop tick manager
    await tm.stop()
    await start_task
    
    assert not tm.running

def test_behavior_tree_context_manager():
    async def test_context():
        async with BehaviorTree() as tree:
            node = DummyNode(name='root')
            tree.load_from_node(node)
            result = await tree.tick()
            assert result == Status.SUCCESS
    
    asyncio.get_event_loop().run_until_complete(test_context()) 