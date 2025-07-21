"""
Condition Node - Node type for checking conditions

Condition nodes are leaf nodes of the behavior tree, used to check specific conditions,
such as whether the enemy is visible, within range, etc.
"""

from abc import abstractmethod
from dataclasses import dataclass

from ..core.status import Status
from ..engine.blackboard import Blackboard
from .base import BaseNode


@dataclass
class Condition(BaseNode):
    """
    Condition node base class

    Condition nodes are leaf nodes of the behavior tree, used to check specific conditions.
    Users need to inherit this class and implement the evaluate method to perform specific condition checks.
    """

    def __post_init__(self):
        """Ensure no child nodes after initialization"""
        super().__post_init__()
        # Condition nodes should not have child nodes
        if self.children:
            raise ValueError("Condition nodes cannot have child nodes")

    async def tick(self, blackboard: Blackboard) -> Status:
        """
        Execute condition node

        Call the evaluate method to check the condition.

        Args:
            blackboard: blackboard system

        Returns:
            execution status
        """
        try:
            # Update execution time
            self.update_tick_time()

            # Check condition
            result = await self.evaluate(blackboard)

            # Set status
            self.status = Status.SUCCESS if result else Status.FAILURE
            return self.status

        except Exception as e:
            # Return failure if check error
            print(f"Condition node '{self.name}' check error: {e}")
            self.status = Status.FAILURE
            return Status.FAILURE

    @abstractmethod
    async def evaluate(self, blackboard: Blackboard) -> bool:
        """
        Check condition

        Subclasses must implement this method to check specific conditions.

        Args:
            blackboard: blackboard system, for data sharing

        Returns:
            Whether the condition is met: True means met, False means not met
        """
        pass

    def add_child(self, child: "BaseNode") -> None:
        """Condition nodes cannot add child nodes"""
        raise ValueError("Condition nodes cannot have child nodes")

    def remove_child(self, child: "BaseNode") -> bool:
        """Condition nodes cannot remove child nodes"""
        return False

    def get_child(self, index: int):
        """Condition nodes have no child nodes"""
        return None

    def get_child_count(self) -> int:
        """Condition nodes have no child nodes"""
        return 0

    def has_children(self) -> bool:
        """Condition nodes have no child nodes"""
        return False


# Predefined condition nodes examples


@dataclass
class CheckBlackboard(Condition):
    """
    Check blackboard data node

    Check whether the specified key-value pair exists in the blackboard.
    """

    key: str = ""
    expected_value: any = None
    check_exists: bool = False  # Whether to only check if the key exists

    async def evaluate(self, blackboard: Blackboard) -> bool:
        """
        Check blackboard data

        Args:
            blackboard: blackboard system

        Returns:
            Whether the condition is met
        """
        if not self.key:
            return False

        if self.check_exists:
            # Only check if the key exists
            return blackboard.has(self.key)
        else:
            # Check key-value pair
            actual_value = blackboard.get(self.key)
            return actual_value == self.expected_value

    def set_key(self, key: str) -> None:
        """
        Set the key to check

        Args:
            key: key name
        """
        self.key = key

    def set_expected_value(self, value: any) -> None:
        """
        Set expected value

        Args:
            value: expected value
        """
        self.expected_value = value

    def set_check_exists(self, check_exists: bool) -> None:
        """
        Set whether to only check if the key exists

        Args:
            check_exists: whether to only check if the key exists
        """
        self.check_exists = check_exists


@dataclass
class IsTrue(Condition):
    """
    Check true value node

    Check whether the boolean value in the blackboard is true.
    """

    key: str = ""

    async def evaluate(self, blackboard: Blackboard) -> bool:
        """
        Check boolean value

        Args:
            blackboard: blackboard system

        Returns:
            Whether the condition is met
        """
        if not self.key:
            return False

        value = blackboard.get(self.key, False)
        return bool(value)

    def set_key(self, key: str) -> None:
        """
        Set the key to check

        Args:
            key: key name
        """
        self.key = key


@dataclass
class IsFalse(Condition):
    """
    Check false value node

    Check whether the boolean value in the blackboard is false.
    """

    key: str = ""

    async def evaluate(self, blackboard: Blackboard) -> bool:
        """
        Check boolean value

        Args:
            blackboard: blackboard system

        Returns:
            Whether the condition is met
        """
        if not self.key:
            return True  # If the key does not exist, treat as false

        value = blackboard.get(self.key, False)
        return not bool(value)

    def set_key(self, key: str) -> None:
        """
        Set the key to check

        Args:
            key: key name
        """
        self.key = key


@dataclass
class Compare(Condition):
    """
    Compare node

    Compare the value in the blackboard.
    """

    key: str = ""
    operator: str = "=="  # ==, !=, >, <, >=, <=
    value: any = None

    async def evaluate(self, blackboard: Blackboard) -> bool:
        """
        Execute comparison

        Args:
            blackboard: blackboard system

        Returns:
            Whether the condition is met
        """
        if not self.key:
            return False

        actual_value = blackboard.get(self.key)

        try:
            if self.operator == "==":
                return actual_value == self.value
            elif self.operator == "!=":
                return actual_value != self.value
            elif self.operator == ">":
                return actual_value > self.value
            elif self.operator == "<":
                return actual_value < self.value
            elif self.operator == ">=":
                return actual_value >= self.value
            elif self.operator == "<=":
                return actual_value <= self.value
            else:
                return False
        except (TypeError, ValueError):
            # Comparison failed, return False
            return False

    def set_comparison(self, key: str, operator: str, value: any) -> None:
        """
        Set comparison parameters

        Args:
            key: key name
            operator: operator
            value: comparison value
        """
        self.key = key
        self.operator = operator
        self.value = value


@dataclass
class AlwaysTrue(Condition):
    """
    Always true node

    Always returns True, used for testing or debugging.
    """

    async def evaluate(self, blackboard: Blackboard) -> bool:
        """
        Always return True

        Args:
            blackboard: blackboard system

        Returns:
            Always True
        """
        return True


@dataclass
class AlwaysFalse(Condition):
    """
    Always false node

    Always returns False, used for testing or debugging.
    """

    async def evaluate(self, blackboard: Blackboard) -> bool:
        """
        Always return False

        Args:
            blackboard: blackboard system

        Returns:
            Always False
        """
        return False
