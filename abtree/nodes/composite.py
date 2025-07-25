"""
Composite node - a node type that contains multiple child nodes

Composite nodes are used to organize and control the execution of multiple child nodes,
including sequence, selector, parallel, etc.
"""

import asyncio
from enum import Enum
from typing import List, Optional

from ..core.status import Status
from ..engine.blackboard import Blackboard
from .base import BaseNode


class Policy(Enum):
    """Parallel execution policy"""

    SUCCEED_ON_ALL = "succeed_on_all"  # Succeed only if all children succeed
    SUCCEED_ON_ONE = "succeed_on_one"  # Succeed if any child succeeds
    FAIL_ON_ALL = "fail_on_all"        # Fail only if all children fail
    FAIL_ON_ONE = "fail_on_one"        # Fail if any child fails


class CompositeNode(BaseNode):
    """
    Composite node base class

    All nodes that contain multiple child nodes inherit from this class,
    providing basic functionality for child node management and execution.
    """

    def add_child(self, child: BaseNode) -> None:
        """Add child node"""
        super().add_child(child)

    def remove_child(self, child: BaseNode) -> bool:
        """Remove child node"""
        return super().remove_child(child)

    def get_child(self, index: int) -> Optional[BaseNode]:
        """Get child node at specified index"""
        return super().get_child(index)

    def get_child_count(self) -> int:
        """Get number of child nodes"""
        return super().get_child_count()

    def has_children(self) -> bool:
        """Check if node has children"""
        return super().has_children()


class Sequence(CompositeNode):
    """
    Sequence node

    Execute all child nodes in sequence, only return success if all child nodes succeed.
    If any child node fails, the sequence fails.
    """

    async def tick(self) -> Status:
        """
        Execute sequence node

        Execute all child nodes in sequence, return failure immediately if any child node fails,
        return success only if all child nodes succeed.

        Returns:
            execution status
        """
        if not self.children:
            return Status.SUCCESS

        for child in self.children:
            child_status = await child.tick()

            if child_status == Status.FAILURE:
                self.status = Status.FAILURE
                return Status.FAILURE
            elif child_status == Status.RUNNING:
                self.status = Status.RUNNING
                return Status.RUNNING

        self.status = Status.SUCCESS
        return Status.SUCCESS


class Selector(CompositeNode):
    """
    Selector node

    Execute child nodes in sequence, return success immediately if any child node succeeds.
    If all child nodes fail, the selector fails.
    """

    async def tick(self) -> Status:
        """
        Execute selector node

        Execute child nodes in sequence, return success immediately if any child node succeeds.
        If all child nodes fail, the selector fails.

        Returns:
            execution status
        """
        if not self.children:
            return Status.FAILURE

        for child in self.children:
            child_status = await child.tick()

            if child_status == Status.SUCCESS:
                self.status = Status.SUCCESS
                return Status.SUCCESS
            elif child_status == Status.RUNNING:
                self.status = Status.RUNNING
                return Status.RUNNING

        self.status = Status.FAILURE
        return Status.FAILURE


class Parallel(CompositeNode):
    """
    Parallel node

    Execute all child nodes concurrently, determine the final result based on the policy.
    Support multiple execution strategies.
    """

    def __init__(self, name: str, children: Optional[List[BaseNode]] = None, policy: Policy = Policy.SUCCEED_ON_ALL):
        super().__init__(name, children)
        self.policy = policy

    async def tick(self) -> Status:
        """
        Execute parallel node

        Execute all child nodes concurrently, determine the final result based on the policy.

        Returns:
            execution status
        """
        if not self.children:
            return Status.SUCCESS

        # Execute all child nodes concurrently
        tasks = [child.tick() for child in self.children]
        results = await asyncio.gather(*tasks)

        # Count results
        success_count = sum(1 for status in results if status == Status.SUCCESS)
        failure_count = sum(1 for status in results if status == Status.FAILURE)
        running_count = sum(1 for status in results if status == Status.RUNNING)

        # Determine final status according to policy
        if self.policy == Policy.SUCCEED_ON_ALL:
            if running_count > 0:
                self.status = Status.RUNNING
                return Status.RUNNING
            elif failure_count > 0:
                self.status = Status.FAILURE
                return Status.FAILURE
            else:
                self.status = Status.SUCCESS
                return Status.SUCCESS

        elif self.policy == Policy.SUCCEED_ON_ONE:
            if success_count > 0:
                self.status = Status.SUCCESS
                return Status.SUCCESS
            elif running_count > 0:
                self.status = Status.RUNNING
                return Status.RUNNING
            else:
                self.status = Status.FAILURE
                return Status.FAILURE

        elif self.policy == Policy.FAIL_ON_ALL:
            if running_count > 0:
                self.status = Status.RUNNING
                return Status.RUNNING
            elif success_count > 0:
                self.status = Status.SUCCESS
                return Status.SUCCESS
            else:
                self.status = Status.FAILURE
                return Status.FAILURE

        elif self.policy == Policy.FAIL_ON_ONE:
            if failure_count > 0:
                self.status = Status.FAILURE
                return Status.FAILURE
            elif running_count > 0:
                self.status = Status.RUNNING
                return Status.RUNNING
            else:
                self.status = Status.SUCCESS
                return Status.SUCCESS

    def set_policy(self, policy: Policy) -> None:
        """
        Set execution policy

        Args:
            policy: Execution policy
        """
        self.policy = policy
