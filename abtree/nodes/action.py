"""
Action node - a node type that executes specific behavior actions

Action nodes are leaf nodes in the behavior tree, used to execute specific actions,
such as movement, attack, collection, etc. Users need to inherit this class to implement specific actions.
"""

import asyncio
from abc import abstractmethod
from typing import Any, Optional, List

from ..core.status import Status
from ..engine.blackboard import Blackboard
from ..utils.logger import get_logger
from .base import BaseNode


class Action(BaseNode):
    """
    Action node base class

    Action nodes are leaf nodes in the behavior tree, used to execute specific actions.
    Users need to inherit this class and implement the execute method to implement specific actions.
    """

    def __init__(self, name: str, children: Optional[List["BaseNode"]] = None):
        super().__init__(name, children)
        # Action nodes should not have children
        if self.children:
            raise ValueError("Action nodes cannot have children")

    async def tick(self, blackboard: Blackboard) -> Status:
        """
        Execute action node

        Call the execute method to execute specific actions.

        Args:
            blackboard: Blackboard system

        Returns:
            Execution status
        """
        try:
            # Update execution time
            self.update_tick_time()

            # Execute specific actions
            result = await self.execute(blackboard)

            # Set status
            self.status = result
            return result

        except Exception as e:
            # Execution error, return failure
            print(f"Action node '{self.name}' execution error: {e}")
            self.status = Status.FAILURE
            return Status.FAILURE

    @abstractmethod
    async def execute(self, blackboard: Blackboard) -> Status:
        """
        Execute specific actions

        Subclasses must implement this method to execute specific actions.

        Args:
            blackboard: Blackboard system, used for data sharing

        Returns:
            Execution status: SUCCESS, FAILURE or RUNNING
        """
        pass

    def add_child(self, child: "BaseNode") -> None:
        """Action nodes cannot add children"""
        raise ValueError("Action nodes cannot have children")

    def remove_child(self, child: "BaseNode") -> bool:
        """Action nodes cannot remove children"""
        return False

    def get_child(self, index: int) -> Optional["BaseNode"]:
        """Action nodes do not have children"""
        return None

    def get_child_count(self) -> int:
        """Action nodes do not have children"""
        return 0

    def has_children(self) -> bool:
        """Action nodes do not have children"""
        return False


# Predefined action node examples


class Wait(Action):
    """
    Wait node

    Wait for a specified time and return success.
    """

    def __init__(self, name: str = "", duration: float = 1.0):
        super().__init__(name)
        self.duration = duration
        self.elapsed = 0.0

    async def execute(self, blackboard: Blackboard) -> Status:
        """
        Execute wait

        Args:
            blackboard: Blackboard system

        Returns:
            Execution status
        """
        # Get wait time from blackboard, if not set then use default value
        wait_duration = blackboard.get("wait_duration", self.duration)

        # Check if this is the first tick
        if self.elapsed == 0.0:
            # Record start time
            import asyncio
            self.start_time = asyncio.get_event_loop().time()
            self.elapsed = 0.001  # Small increment to mark as started
            return Status.RUNNING

        # Calculate elapsed time
        import asyncio
        current_time = asyncio.get_event_loop().time()
        self.elapsed = current_time - self.start_time

        # Check if the wait is complete
        if self.elapsed >= wait_duration:
            self.elapsed = 0.0  # Reset timer
            return Status.SUCCESS
        else:
            return Status.RUNNING

    def reset(self) -> None:
        """Reset node status"""
        super().reset()
        self.elapsed = 0.0
        self.start_time = 0.0

    def set_duration(self, duration: float) -> None:
        """
        Set wait time

        Args:
            duration: Wait time (seconds)
        """
        self.duration = duration


class Log(Action):
    """
    Log node

    Output log information.
    """

    def __init__(self, name: str = "", message: str = "", level: str = "INFO"):
        """Initialize Log node with level as name if not specified"""
        if not name or name == "Log":
            name = level.upper()
        super().__init__(name)
        self.message = message
        self.level = level

    async def execute(self, blackboard: Blackboard) -> Status:
        """
        Execute log output

        Args:
            blackboard: Blackboard system

        Returns:
            Execution status
        """
        # Get message from blackboard, if not set then use default message
        log_message = blackboard.get("log_message", self.message)
        log_level = blackboard.get("log_level", self.level)

        # Create a logger with the level as name
        logger = get_logger(log_level.upper())
        
        # Use getattr to dynamically call the appropriate logging method
        log_method = getattr(logger, log_level.lower(), logger.info)
        log_method(log_message)

        return Status.SUCCESS

    def set_message(self, message: str) -> None:
        """
        Set log message

        Args:
            message: Log message
        """
        self.message = message

    def set_level(self, level: str) -> None:
        """
        Set log level

        Args:
            level: Log level
        """
        self.level = level


class SetBlackboard(Action):
    """
    Set blackboard data node

    Set data in the blackboard.
    """

    def __init__(self, name: str = "", key: str = "", value: Any = None):
        super().__init__(name)
        self.key = key
        self.value = value

    async def execute(self, blackboard: Blackboard) -> Status:
        """
        Execute set blackboard data

        Args:
            blackboard: Blackboard system

        Returns:
            Execution status
        """
        if not self.key:
            return Status.FAILURE

        # Set blackboard data
        blackboard.set(self.key, self.value)

        return Status.SUCCESS

    def set_key_value(self, key: str, value: Any) -> None:
        """
        Set key-value pair

        Args:
            key: Key
            value: Value
        """
        self.key = key
        self.value = value


def blackboard_binding(execute_method):
    """Decorator: Apply to the execute method to automatically handle blackboard synchronization"""
    
    async def wrapper(self, blackboard):
        # Automatically inject blackboard when executing execute
        self._current_blackboard = blackboard
        
        # Get mapping values from blackboard when execute starts
        if hasattr(self, '_param_mappings'):
            for node_attr, blackboard_key in self._param_mappings.items():
                if hasattr(self, node_attr):
                    # Get value from blackboard, if not set then keep original value
                    current_value = getattr(self, node_attr)
                    # If current value is mapping format (e.g. {exchange_value}), get value from blackboard
                    if isinstance(current_value, str) and current_value.startswith('{') and current_value.endswith('}'):
                        # This is mapping format, get actual value from blackboard
                        value = blackboard.get(blackboard_key, current_value)
                    else:
                        # This is normal value, get value from blackboard, if not set then keep original value
                        value = blackboard.get(blackboard_key, current_value)
                    setattr(self, node_attr, value)
        
        # Create property descriptors for mapped attributes to implement automatic synchronization
        if hasattr(self, '_param_mappings'):
            for node_attr, blackboard_key in self._param_mappings.items():
                if hasattr(self, node_attr):
                    # Save original value
                    original_value = getattr(self, node_attr)
                    
                    # Create property descriptor
                    def make_property(attr_name, bb_key):
                        def getter(obj):
                            return getattr(obj, f'_{attr_name}_value', original_value)
                        
                        def setter(obj, value):
                            setattr(obj, f'_{attr_name}_value', value)
                            # Automatically synchronize to blackboard
                            if hasattr(obj, '_current_blackboard') and obj._current_blackboard is not None:
                                obj._current_blackboard.set(bb_key, value)
                        
                        return property(getter, setter)
                    
                    # Set property descriptor
                    setattr(self.__class__, node_attr, make_property(node_attr, blackboard_key))
        
        try:
            # Handle asynchronous functions correctly
            if asyncio.iscoroutinefunction(execute_method):
                result = await execute_method(self, blackboard)
            else:
                result = execute_method(self, blackboard)
            return result
        finally:
            # Clean up after execution
            self._current_blackboard = None
    
    return wrapper
