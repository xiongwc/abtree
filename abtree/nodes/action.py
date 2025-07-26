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


class CommPubExternal(Action):
    """External publisher action that publishes data to external world through forest"""
    
    def __init__(self, name: str, topic: str = "", data: Any = None):
        super().__init__(name)
        self.topic = topic
        self.data = data
    
    async def execute(self, topic: str = None, data: Any = None) -> Status:
        """
        Execute external publishing
        
        Args:
            topic: Topic to publish to external world (optional, uses instance topic if not provided)
            data: Data to publish (optional, uses instance data if not provided)
            
        Returns:
            Execution status
        """
        # Use provided parameters or fall back to instance attributes
        publish_topic = topic if topic is not None else self.topic
        publish_data = data if data is not None else self.data
        
        if not publish_topic:
            logger.error("No topic specified for external publishing")
            return Status.FAILURE
        
        try:
            # Get forest from blackboard
            forest = self.blackboard.get("__forest") if self.blackboard else None
            if not forest:
                logger.error("No forest found in blackboard")
                return Status.FAILURE
            
            # Get communication middleware from forest
            comm_middleware = None
            for middleware in forest.middleware:
                if hasattr(middleware, 'pub_external'):
                    comm_middleware = middleware
                    break
            
            if not comm_middleware:
                logger.error("No communication middleware found in forest")
                return Status.FAILURE
            
            # Publish to external world through middleware
            await comm_middleware.pub_external(publish_topic, publish_data, self.name)
            logger.info(f"Published to external topic '{publish_topic}': {publish_data}")
            return Status.SUCCESS
        except Exception as e:
            logger.error(f"Error publishing to external topic '{publish_topic}': {e}")
            return Status.FAILURE
    
    def set_topic_data(self, topic: str, data: Any) -> None:
        """
        Set topic and data for external publishing
        
        Args:
            topic: Topic to publish to
            data: Data to publish
        """
        self.topic = topic
        self.data = data


class CommSubExternal(Action):
    """External subscriber action that receives data from external world through forest"""
    
    def __init__(self, name: str, topic: str = "", timeout: float = None):
        super().__init__(name)
        self.topic = topic
        self.timeout = timeout
        self._received_data = None
        self._data_received = False
    
    async def execute(self, topic: str = None, timeout: float = None) -> Status:
        """
        Execute external subscription
        
        Args:
            topic: Topic to subscribe to (optional, uses instance topic if not provided)
            timeout: Timeout for waiting for data (optional, uses instance timeout if not provided)
            
        Returns:
            Execution status
        """
        # Use provided parameters or fall back to instance attributes
        subscribe_topic = topic if topic is not None else self.topic
        subscribe_timeout = timeout if timeout is not None else self.timeout
        
        if not subscribe_topic:
            logger.error("No topic specified for external subscription")
            return Status.FAILURE
        
        try:
            # Get forest from blackboard
            forest = self.blackboard.get("__forest") if self.blackboard else None
            if not forest:
                logger.error("No forest found in blackboard")
                return Status.FAILURE
            
            # Get communication middleware from forest
            comm_middleware = None
            for middleware in forest.middleware:
                if hasattr(middleware, 'get_external_data_queue'):
                    comm_middleware = middleware
                    break
            
            if not comm_middleware:
                logger.error("No communication middleware found in forest")
                return Status.FAILURE
            
            # Check for external data in the queue
            external_data = comm_middleware.get_external_data_queue(subscribe_topic)
            
            if external_data:
                # Get the most recent data
                latest_data = external_data[-1]
                self._received_data = latest_data["data"]
                self._data_received = True
                
                # Store received data in blackboard for other nodes to access
                if self.blackboard:
                    self.blackboard.set(f"external_data_{subscribe_topic}", self._received_data)
                    self.blackboard.set(f"external_data_source_{subscribe_topic}", latest_data["source"])
                    self.blackboard.set(f"external_data_timestamp_{subscribe_topic}", latest_data["timestamp"])
                
                logger.info(f"Received external data from topic '{subscribe_topic}': {self._received_data}")
                return Status.SUCCESS
            else:
                if subscribe_timeout is not None and subscribe_timeout > 0:
                    # Wait for data with timeout
                    import asyncio
                    await asyncio.sleep(subscribe_timeout)
                    # Check again after timeout
                    external_data = comm_middleware.get_external_data_queue(subscribe_topic)
                    if external_data:
                        latest_data = external_data[-1]
                        self._received_data = latest_data["data"]
                        self._data_received = True
                        
                        if self.blackboard:
                            self.blackboard.set(f"external_data_{subscribe_topic}", self._received_data)
                            self.blackboard.set(f"external_data_source_{subscribe_topic}", latest_data["source"])
                            self.blackboard.set(f"external_data_timestamp_{subscribe_topic}", latest_data["timestamp"])
                        
                        logger.info(f"Received external data from topic '{subscribe_topic}' after timeout: {self._received_data}")
                        return Status.SUCCESS
                    else:
                        logger.warning(f"Timeout waiting for external data from topic '{subscribe_topic}'")
                        return Status.FAILURE
                else:
                    logger.warning(f"No external data available for topic '{subscribe_topic}'")
                    return Status.FAILURE
                    
        except Exception as e:
            logger.error(f"Error subscribing to external topic '{subscribe_topic}': {e}")
            return Status.FAILURE
    
    def get_received_data(self) -> Any:
        """
        Get the last received external data
        
        Returns:
            The received data or None if no data was received
        """
        return self._received_data
    
    def has_received_data(self) -> bool:
        """
        Check if data was received
        
        Returns:
            True if data was received, False otherwise
        """
        return self._data_received
    
    def set_topic_timeout(self, topic: str, timeout: float) -> None:
        """
        Set topic and timeout for external subscription
        
        Args:
            topic: Topic to subscribe to
            timeout: Timeout for waiting for data
        """
        self.topic = topic
        self.timeout = timeout
    
    def reset_received_data(self) -> None:
        """Reset received data state"""
        self._received_data = None
        self._data_received = False
