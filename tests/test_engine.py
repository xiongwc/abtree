import pytest
import asyncio
from abtree.engine.behavior_tree import BehaviorTree
from abtree.engine.blackboard import Blackboard
from abtree.engine.event_system import EventSystem, Event, EventPriority
from abtree.engine.tick_manager import TickManager
from abtree.core.status import Status
from abtree.nodes.base import BaseNode

class DummyNode(BaseNode):
    async def tick(self, blackboard):
        return Status.SUCCESS

class FailingNode(BaseNode):
    async def tick(self, blackboard):
        return Status.FAILURE

class RunningNode(BaseNode):
    def __init__(self, name: str, max_ticks: int = 3):
        super().__init__(name=name)
        self.max_ticks = max_ticks
        self.tick_count = 0
    
    async def tick(self, blackboard):
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

def test_event_system_basic():
    es = EventSystem()
    called = []
    def cb(event):
        called.append(event.name)
    es.on('test', cb)
    asyncio.get_event_loop().run_until_complete(es.emit('test', data=123))
    assert 'test' in called
    es.clear('test')
    assert es.get_listeners('test') == []

@pytest.mark.asyncio
async def test_event_system_advanced():
    es = EventSystem()
    events_received = []
    
    def callback1(event):
        events_received.append(f"cb1:{event.name}")
    
    def callback2(event):
        events_received.append(f"cb2:{event.name}")
    
    # Test multiple listeners
    es.on('test_event', callback1)
    es.on('test_event', callback2)
    
    await es.emit('test_event', data={'test': 'data'})
    assert len(events_received) == 2
    assert 'cb1:test_event' in events_received
    assert 'cb2:test_event' in events_received
    
    # Test event history
    history = es.get_event_history('test_event')
    assert len(history) == 1
    assert history[0].name == 'test_event'
    
    # Test unsubscribe
    es.off('test_event', callback1)
    events_received.clear()
    await es.emit('test_event')
    assert len(events_received) == 1
    assert 'cb2:test_event' in events_received

@pytest.mark.asyncio
async def test_event_system_global_listeners():
    es = EventSystem()
    global_events = []
    
    def global_callback(event):
        global_events.append(event.name)
    
    es.on_any(global_callback)
    await es.emit('event1')
    await es.emit('event2')
    
    assert len(global_events) == 2
    assert 'event1' in global_events
    assert 'event2' in global_events

@pytest.mark.asyncio
async def test_behavior_tree_tick():
    tree = BehaviorTree()
    node = DummyNode(name='root')
    tree.load_from_root(node)
    result = await tree.tick()
    assert result == Status.SUCCESS
    assert tree.root == node
    tree.reset()
    assert tree.root.status == Status.FAILURE

@pytest.mark.asyncio
async def test_behavior_tree_event_emit():
    tree = BehaviorTree()
    node = DummyNode(name='root')
    tree.load_from_root(node)
    events = []
    def on_tick_start(event):
        events.append(event.name)
    tree.event_system.on('tree_tick_start', on_tick_start)
    await tree.tick()
    assert 'tree_tick_start' in events

@pytest.mark.asyncio
async def test_behavior_tree_with_failing_node():
    tree = BehaviorTree()
    node = FailingNode(name='root')
    tree.load_from_root(node)
    result = await tree.tick()
    assert result == Status.FAILURE

@pytest.mark.asyncio
async def test_behavior_tree_with_running_node():
    tree = BehaviorTree()
    node = RunningNode(name='root', max_ticks=2)
    tree.load_from_root(node)
    
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
    
    tree.load_from_root(node1)
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
    tree.load_from_root(node)
    
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
            tree.load_from_root(node)
            result = await tree.tick()
            assert result == Status.SUCCESS
    
    asyncio.get_event_loop().run_until_complete(test_context()) 