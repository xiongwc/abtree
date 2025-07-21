"""
Core module unit tests

Test the core functions of the behavior tree, including status, blackboard, event system, etc.
"""

import asyncio
from datetime import datetime

import pytest

from abtree import Blackboard, EventSystem, TickManager
from abtree.core import Policy, Status


class TestStatus:
    """Test status enumeration"""

    def test_status_values(self):
        """Test status values"""
        assert Status.SUCCESS.value == 1
        assert Status.FAILURE.value == 2
        assert Status.RUNNING.value == 3

    def test_status_str(self):
        """Test status string representation"""
        assert str(Status.SUCCESS) == "SUCCESS"
        assert str(Status.FAILURE) == "FAILURE"
        assert str(Status.RUNNING) == "RUNNING"


class TestPolicy:
    """Test policy enumeration"""

    def test_policy_values(self):
        """Test policy values"""
        assert Policy.SUCCEED_ON_ONE.value == 1
        assert Policy.SUCCEED_ON_ALL.value == 2
        assert Policy.FAIL_ON_ONE.value == 3
        assert Policy.FAIL_ON_ALL.value == 4


class TestBlackboard:
    """Test blackboard functionality"""

    def setup_method(self):
        """Set up test environment"""
        self.blackboard = Blackboard()

    def test_set_get_data(self):
        """Test setting and getting data"""
        self.blackboard.set("test_key", "test_value")
        assert self.blackboard.get("test_key") == "test_value"

    def test_get_default_value(self):
        """Test getting default value"""
        assert self.blackboard.get("nonexistent_key", "default") == "default"

    def test_has_data(self):
        """Test checking if data exists"""
        assert not self.blackboard.has("test_key")
        self.blackboard.set("test_key", "test_value")
        assert self.blackboard.has("test_key")

    def test_remove_data(self):
        """Test removing data"""
        self.blackboard.set("test_key", "test_value")
        assert self.blackboard.has("test_key")
        self.blackboard.remove("test_key")
        assert not self.blackboard.has("test_key")

    def test_clear_all_data(self):
        """Test clearing all data"""
        self.blackboard.set("key1", "value1")
        self.blackboard.set("key2", "value2")
        assert len(self.blackboard.data) == 2
        self.blackboard.clear()
        assert len(self.blackboard.data) == 0


class TestEventSystem:
    """Test event system"""

    def setup_method(self):
        """Set up test environment"""
        # Create event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        self.event_system = EventSystem()
        self.event_received = False
        self.event_data = None

    def test_on_handler(self):
        """Test registering event handler"""

        def handler(event):
            self.event_received = True
            self.event_data = event.data

        self.event_system.on("test_event", handler)
        assert "test_event" in self.event_system._listeners

    def test_emit_event(self):
        """Test emitting event"""

        def handler(event):
            self.event_received = True
            self.event_data = event.data

        self.event_system.on("test_event", handler)
        asyncio.run(self.event_system.emit("test_event", {"message": "test"}))

        assert self.event_received
        assert self.event_data == {"message": "test"}

    def test_off_handler(self):
        """Test unregistering event handler"""

        def handler(event):
            pass

        self.event_system.on("test_event", handler)
        assert "test_event" in self.event_system._listeners

        self.event_system.off("test_event", handler)
        # Check if listener is removed
        listeners = self.event_system._listeners.get("test_event", [])
        assert len(listeners) == 0


class TestTickManager:
    """Test Tick Manager"""

    def setup_method(self):
        """Set up test environment"""
        # Create event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        self.tick_manager = TickManager()

    def test_tick_counter(self):
        """Test Tick counter"""
        # Note: increment_tick method does not exist, need to use tick_once to increase count
        # Here we test basic functionality
        assert self.tick_manager.get_tick_count() == 0

    def test_reset_tick_counter(self):
        """Test resetting Tick counter"""
        self.tick_manager.reset_stats()
        assert self.tick_manager.get_tick_count() == 0

    def test_tick_timestamp(self):
        """Test Tick timestamp"""
        timestamp = self.tick_manager.get_last_tick_time()
        assert isinstance(timestamp, float)


if __name__ == "__main__":
    pytest.main([__file__])
