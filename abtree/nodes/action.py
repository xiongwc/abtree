"""
Action node - a node type that executes specific behavior actions

Action nodes are leaf nodes in the behavior tree, used to execute specific actions,
such as movement, attack, collection, etc. Users need to inherit this class to implement specific actions.
"""

import asyncio
from abc import abstractmethod
from typing import Any, Optional, List, Dict
import functools

from ..core.status import Status
from ..engine.blackboard import Blackboard
from ..utils.logger import get_logger, logger
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

    async def tick(self, *args, **kwargs) -> Status:
        """
        Execute action node

        Call the execute method to execute specific actions.
        Automatically passes node attributes as arguments to execute method.

        Returns:
            Execution status
        """
        try:
            # Update execution time
            self.update_tick_time()

            # Get node attributes that might be passed to execute
            node_args = []
            node_kwargs: Dict[str, Any] = {}
            
            # Check if execute method has specific parameter names
            import inspect
            sig = inspect.signature(self.execute)
            param_names = list(sig.parameters.keys())
            
            # Skip 'self' parameter
            if param_names and param_names[0] == 'self':
                param_names = param_names[1:]
            
            # Use stored execute attributes from XML parser if available
            if hasattr(self, '_execute_attributes'):
                stored_attrs = self._execute_attributes
                for param_name in param_names:
                    if param_name in stored_attrs:
                        stored_value = stored_attrs[param_name]
                        if stored_value is None:
                            # If stored value is None, it might be a blackboard mapping
                            # Try to get mapped value from blackboard
                            mapped_value = self.get_mapped_value(param_name, None)
                            node_args.append(mapped_value)
                        else:
                            node_args.append(stored_value)
                    elif hasattr(self, param_name):
                        node_args.append(getattr(self, param_name))
                    elif param_name in kwargs:
                        node_args.append(kwargs[param_name])
                    else:
                        # Use default value if available
                        param = sig.parameters.get(param_name)
                        if param and param.default != inspect.Parameter.empty:
                            node_args.append(param.default)
                        else:
                            node_args.append(None)
            else:
                # Original logic for backward compatibility
                for param_name in param_names:
                    if hasattr(self, param_name):
                        node_args.append(getattr(self, param_name))
                    elif param_name in kwargs:
                        node_args.append(kwargs[param_name])
                    else:
                        # Use default value if available
                        param = sig.parameters.get(param_name)
                        if param and param.default != inspect.Parameter.empty:
                            node_args.append(param.default)
                        else:
                            node_args.append(None)

            # Execute specific actions with node attributes
            # Check if execute method has specific parameter names (not *args, **kwargs)
            if param_names and len(param_names) > 0:
                # Execute with positional arguments in the correct order
                result = await self.execute(*node_args)
            else:
                # Execute with *args, **kwargs signature
                result = await self.execute(*node_args, **kwargs)

            # Set status
            self.status = result
            return result

        except Exception as e:
            # Execution error, return failure
            print(f"Action node '{self.name}' execution error: {e}")
            self.status = Status.FAILURE
            return Status.FAILURE

    @abstractmethod
    async def execute(self, *args, **kwargs) -> Status:
        """
        Execute specific actions

        Subclasses must implement this method to execute specific actions.
        Parameters can be passed from node attributes or from tick() arguments.

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

    async def execute(self, *args, **kwargs) -> Status:
        """
        Execute wait

        Returns:
            Execution status
        """
        # Get wait time from blackboard, if not set then use default value
        wait_duration = self.get_mapped_value("duration", self.duration)

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

    def __init__(self, name: str = "", message: Any = None, level: str = "INFO"):
        """Initialize Log node with level as name if not specified"""
        super().__init__(name)
        self.message = message
        self.level = level

    async def execute(self, message: Any, level: str = "INFO") -> Status:
        """
        Execute log output

        Returns:
            Execution status
        """

        # Try to get message from blackboard mapping first, then from parameter
        try:
            message = self.get_port("message")
        except ValueError:
            # If not mapped to blackboard, use the parameter value
            pass
        
        # Try to get level from blackboard mapping first, then from parameter
        try:
            level = self.get_port("level")
        except ValueError:
            # If not mapped to blackboard, use the parameter value
            pass

        logger = get_logger(level.upper())
        
        # Use getattr to dynamically call the appropriate logging method
        log_method = getattr(logger, level.lower(), logger.info)
        log_method(message)

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

    async def execute(self, *args, **kwargs) -> Status:
        """
        Execute set blackboard data

        Returns:
            Execution status
        """
        if not self.key or self.blackboard is None:
            return Status.FAILURE

        # Set blackboard data
        self.blackboard.set(self.key, self.value)

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


class CommPublisher(Action):
    """publisher action that emits events"""
    
    def __init__(self, name: str):
        super().__init__(name)
    
    async def execute(self, topic:str, message: Any):
        event_dispatcher = self.get_event_dispatcher()
        if event_dispatcher:
            await event_dispatcher.emit(f"topic_{topic}", source=self.name, data=message)
        else:
            logger.error("No event dispatcher found in blackboard")
            return Status.FAILURE
        return Status.SUCCESS


class CommSubscriber(Action):
    """subscriber action that waits for events"""
    
    def __init__(self, name: str):
        super().__init__(name)
    async def execute(self, topic:str, message: Any, timeout: float = None):
        event_dispatcher = self.get_event_dispatcher()
        if event_dispatcher:            
            event_triggered = await event_dispatcher.wait_for(f"topic_{topic}", timeout=timeout)
            if event_triggered:
                event_info = event_dispatcher.get_event_info(f"topic_{topic}")
                received_message = event_info.data if event_info and event_info.data else "No message data"
                self.set_port("message", received_message)
            else:
                logger.warning(f"Timeout waiting for event: topic_{topic}")
                return Status.FAILURE
        else:
            logger.error(f"No event dispatcher found in blackboard")
            return Status.FAILURE
        return Status.SUCCESS


class CommExternalInput(Action):
    """External input action that processes data from external sources"""
    
    def __init__(self, name: str, channel: str = ""):
        super().__init__(name)
        self.channel = channel
    
    async def execute(self, channel: str = None, timeout: float = None):
        """
        Execute external input processing
        
        Args:
            channel: Input channel name (optional, uses self.channel if not provided)
            timeout: Timeout for waiting for input (optional)
            
        Returns:
            Execution status
        """
        if channel is None:
            channel = self.channel
        
        if not channel:
            logger.error("No channel specified for external input")
            return Status.FAILURE
        
        # Get the forest through the behavior tree
        tree = self.get_tree()
        if tree is None:
            logger.error("No behavior tree found for external input")
            return Status.FAILURE
        
        # Get the forest from the tree's metadata or parent
        forest = None
        if hasattr(tree, 'forest'):
            forest = tree.forest
        elif hasattr(tree, 'metadata') and 'forest' in tree.metadata:
            forest = tree.metadata['forest']
        
        if forest is None:
            logger.error("No forest found for external input")
            return Status.FAILURE
        
        # Wait for input data from the specified channel
        # This is a simplified implementation - in practice, you might want to
        # implement a more sophisticated waiting mechanism
        try:
            # For now, we'll just check if there's data in the input queue
            input_queue = forest.get_external_io_stats().get("input_queue_size", 0)
            if input_queue > 0:
                # Process the input data
                self.set_mapped_value("channel", channel)
                self.set_mapped_value("status", "received")
                return Status.SUCCESS
            else:
                if timeout and timeout > 0:
                    # Wait for a short time before checking again
                    await asyncio.sleep(min(timeout, 0.1))
                    return Status.RUNNING
                else:
                    return Status.FAILURE
        except Exception as e:
            logger.error(f"External input error: {e}")
            return Status.FAILURE
    
    def set_channel(self, channel: str) -> None:
        """
        Set input channel
        
        Args:
            channel: Input channel name
        """
        self.channel = channel


class CommExternalOutput(Action):
    """External output action that sends data to external destinations"""
    
    def __init__(self, name: str, channel: str = ""):
        super().__init__(name)
        self.channel = channel
    
    async def execute(self, channel: str = None, data: Any = None):
        """
        Execute external output processing
        
        Args:
            channel: Output channel name (optional, uses self.channel if not provided)
            data: Data to output (optional, uses mapped data if not provided)
            
        Returns:
            Execution status
        """
        if channel is None:
            channel = self.channel
        
        if not channel:
            logger.error("No channel specified for external output")
            return Status.FAILURE
        
        # Get the data to output
        if data is None:
            data = self.get_mapped_value("data")
        
        if data is None:
            logger.error("No data specified for external output")
            return Status.FAILURE
        
        # Get the forest through the behavior tree
        tree = self.get_tree()
        if tree is None:
            logger.error("No behavior tree found for external output")
            return Status.FAILURE
        
        # Get the forest from the tree's metadata or parent
        forest = None
        if hasattr(tree, 'forest'):
            forest = tree.forest
        elif hasattr(tree, 'metadata') and 'forest' in tree.metadata:
            forest = tree.metadata['forest']
        
        if forest is None:
            logger.error("No forest found for external output")
            return Status.FAILURE
        
        try:
            # Send data to external output
            await forest.output(channel, data, source=self.name)
            self.set_mapped_value("channel", channel)
            self.set_mapped_value("data", data)
            self.set_mapped_value("status", "sent")
            return Status.SUCCESS
        except Exception as e:
            logger.error(f"External output error: {e}")
            return Status.FAILURE
    
    def set_channel(self, channel: str) -> None:
        """
        Set output channel
        
        Args:
            channel: Output channel name
        """
        self.channel = channel
    
    def set_data(self, data: Any) -> None:
        """
        Set output data
        
        Args:
            data: Data to output
        """
        self.set_mapped_value("data", data)