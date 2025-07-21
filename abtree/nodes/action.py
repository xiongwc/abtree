"""
Action node - a node type that executes specific behavior actions

Action nodes are leaf nodes in the behavior tree, used to execute specific actions,
such as movement, attack, collection, etc. Users need to inherit this class to implement specific actions.
"""

from abc import abstractmethod
from dataclasses import dataclass

from .base import BaseNode
from ..engine.blackboard import Blackboard
from ..core.status import Status


@dataclass
class Action(BaseNode):
    """
    Action node base class

    Action nodes are leaf nodes in the behavior tree, used to execute specific actions.
    Users need to inherit this class and implement the execute method to implement specific actions.
    """

    def __post_init__(self):
        """Ensure no children after initialization"""
        super().__post_init__()
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

    def get_child(self, index: int):
        """Action nodes do not have children"""
        return None

    def get_child_count(self) -> int:
        """Action nodes do not have children"""
        return 0

    def has_children(self) -> bool:
        """Action nodes do not have children"""
        return False


# Predefined action node examples


@dataclass
class Wait(Action):
    """
    Wait node

    Wait for a specified time and return success.
    """

    duration: float = 1.0  # Wait time (seconds)
    elapsed: float = 0.0  # Elapsed time

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

        # Check if the wait is complete
        if self.elapsed >= wait_duration:
            self.elapsed = 0.0  # Reset timer
            return Status.SUCCESS

        # Add elapsed time
        self.elapsed += 0.016  # Assume 60 FPS, approximately 16ms per frame

        if self.elapsed >= wait_duration:
            self.elapsed = 0.0
            return Status.SUCCESS
        else:
            return Status.RUNNING

    def reset(self) -> None:
        """Reset node status"""
        super().reset()
        self.elapsed = 0.0

    def set_duration(self, duration: float) -> None:
        """
        Set wait time

        Args:
            duration: Wait time (seconds)
        """
        self.duration = duration


@dataclass
class Log(Action):
    """
    Log node

    Output log information.
    """

    message: str = ""
    level: str = "INFO"

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

        # Output log
        print(f"[{log_level}] {log_message}")

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


@dataclass
class SetBlackboard(Action):
    """
    Set blackboard data node

    Set data in the blackboard.
    """

    key: str = ""
    value: any = None

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

    def set_key_value(self, key: str, value: any) -> None:
        """
        Set key-value pair

        Args:
            key: Key
            value: Value
        """
        self.key = key
        self.value = value
