"""
Decorator node - a node type that modifies the behavior of child nodes

Decorator nodes are used to modify the execution behavior of child nodes, including:
- Inverter: Invert the result of the child node
- Repeater: Repeat the execution of the child node
- UntilSuccess: Until success
- UntilFailure: Until failure
"""

from dataclasses import dataclass
from typing import List, Optional

from ..core.status import Status
from ..engine.blackboard import Blackboard
from .base import BaseNode


@dataclass
class DecoratorNode(BaseNode):
    """
    Decorator node base class

    All decorator nodes inherit from this class, used to modify the behavior of child nodes.
    Decorator nodes can only have one child node.
    """

    child: Optional[BaseNode] = None

    def __init__(self, name: str, child: Optional[BaseNode] = None, children: Optional[List[BaseNode]] = None):
        """
        Initialize decorator node

        Args:
            name: Node name
            child: Single child node (preferred for decorators)
            children: List of child nodes (for compatibility)
        """
        if child is not None:
            # If child is provided, use it as the single child
            children = [child]
        elif children is None:
            children = []
        
        super().__init__(name=name, children=children)
        if children and len(children) == 1:
            self.child = children[0]

    def __post_init__(self) -> None:
        """Set child node after initialization"""
        if hasattr(super(), '__post_init__'):
            super().__post_init__()
        if self.children and len(self.children) == 1:
            self.child = self.children[0]

    def add_child(self, child: BaseNode) -> None:
        """
        Add child node

        Decorator nodes can only have one child node, if there is already a child node, replace it.

        Args:
            child: child node
        """
        # Clear existing child nodes
        self.children.clear()
        super().add_child(child)
        self.child = child

    def remove_child(self, child: BaseNode) -> bool:
        """
        Remove child node

        Args:
            child: child node to remove

        Returns:
            True if the child node is found and removed, False otherwise
        """
        result = super().remove_child(child)
        if result and self.child == child:
            self.child = None
        return result

    def has_child(self) -> bool:
        """
        Check if there is a child node

        Returns:
            True if there is a child node, False otherwise
        """
        return self.child is not None

    async def tick(self) -> Status:
        """
        Execute decorator node

        Default implementation that delegates to the child node.

        Returns:
            Execution status
        """
        if not self.child:
            return Status.FAILURE
        
        return await self.child.tick()


class Inverter(DecoratorNode):
    """
    Inverter node

    Invert the result of the child node:
    - SUCCESS -> FAILURE
    - FAILURE -> SUCCESS
    - RUNNING -> RUNNING
    """

    async def tick(self) -> Status:
        """
        Execute inverter node

        Execute the child node and invert its result.

        Returns:
            Inverted execution status
        """
        if not self.child:
            return Status.FAILURE

        child_status = await self.child.tick()

        if child_status == Status.SUCCESS:
            self.status = Status.FAILURE
            return Status.FAILURE
        elif child_status == Status.FAILURE:
            self.status = Status.SUCCESS
            return Status.SUCCESS
        else:  # RUNNING
            self.status = Status.RUNNING
            return Status.RUNNING


class Repeater(DecoratorNode):
    """
    Repeater node

    Repeat the execution of the child node a specified number of times, or repeat indefinitely.
    """

    def __init__(self, name: str, child: Optional[BaseNode] = None, repeat_count: int = -1):
        super().__init__(name, child)
        self.repeat_count = repeat_count
        self.current_count = 0

    async def tick(self) -> Status:
        """
        Execute repeater node

        Repeat the execution of the child node a specified number of times.

        Returns:
            Execution status
        """
        if not self.child:
            return Status.FAILURE

        # Check if repeat count limit is reached
        if self.repeat_count > 0 and self.current_count >= self.repeat_count:
            self.status = Status.SUCCESS
            return Status.SUCCESS

        # Execute child node
        child_status = await self.child.tick()

        if child_status == Status.SUCCESS:
            self.current_count += 1

            # Check if need to continue repeating
            if self.repeat_count == -1 or self.current_count < self.repeat_count:
                # Reset child node status, prepare for next execution
                self.child.reset()
                self.status = Status.RUNNING
                return Status.RUNNING
            else:
                # Reached repeat count, return success
                self.status = Status.SUCCESS
                return Status.SUCCESS

        elif child_status == Status.FAILURE:
            # Child node failed, reset count and return failure
            self.current_count = 0
            self.status = Status.FAILURE
            return Status.FAILURE

        else:  # RUNNING
            self.status = Status.RUNNING
            return Status.RUNNING

    def reset(self) -> None:
        """Reset node status"""
        super().reset()
        self.current_count = 0

    def set_repeat_count(self, count: int) -> None:
        """
        Set repeat count

        Args:
            count: Repeat count, -1 means infinite repeat
        """
        self.repeat_count = count


class UntilSuccess(DecoratorNode):
    """
    Until success node

    Repeat the execution of the child node until it succeeds.
    """

    async def tick(self) -> Status:
        """
        Execute until success node

        Repeat the execution of the child node until it succeeds.

        Returns:
            Execution status
        """
        if not self.child:
            return Status.FAILURE

        child_status = await self.child.tick()

        if child_status == Status.SUCCESS:
            self.status = Status.SUCCESS
            return Status.SUCCESS
        elif child_status == Status.FAILURE:
            # Child node failed, reset its status and continue execution
            self.child.reset()
            self.status = Status.RUNNING
            return Status.RUNNING
        else:  # RUNNING
            self.status = Status.RUNNING
            return Status.RUNNING


class UntilFailure(DecoratorNode):
    """
    Until failure node

    Repeat the execution of the child node until it fails.
    """

    async def tick(self) -> Status:
        """
        Execute until failure node

        Repeat the execution of the child node until it fails.

        Returns:
            Execution status
        """
        if not self.child:
            return Status.FAILURE

        child_status = await self.child.tick()

        if child_status == Status.FAILURE:
            self.status = Status.SUCCESS
            return Status.SUCCESS
        elif child_status == Status.SUCCESS:
            # Child node succeeded, reset its status and continue execution
            self.child.reset()
            self.status = Status.RUNNING
            return Status.RUNNING
        else:  # RUNNING
            self.status = Status.RUNNING
            return Status.RUNNING

# For backward compatibility, provide Decorator as an alias for DecoratorNode
Decorator = DecoratorNode
