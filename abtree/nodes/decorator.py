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

    async def tick(self, blackboard: Blackboard) -> Status:
        """
        Execute decorator node

        Default implementation that delegates to the child node.

        Args:
            blackboard: Blackboard system

        Returns:
            Execution status
        """
        if not self.child:
            return Status.FAILURE
        
        return await self.child.tick(blackboard)


@dataclass
class Inverter(DecoratorNode):
    """
    Inverter node

    Invert the result of the child node:
    - SUCCESS -> FAILURE
    - FAILURE -> SUCCESS
    - RUNNING -> RUNNING
    """

    async def tick(self, blackboard: Blackboard) -> Status:
        """
        Execute inverter node

        Execute the child node and invert its result.

        Args:
            blackboard: blackboard system

        Returns:
            Inverted execution status
        """
        if not self.child:
            return Status.FAILURE

        child_status = await self.child.tick(blackboard)

        if child_status == Status.SUCCESS:
            self.status = Status.FAILURE
            return Status.FAILURE
        elif child_status == Status.FAILURE:
            self.status = Status.SUCCESS
            return Status.SUCCESS
        else:  # RUNNING
            self.status = Status.RUNNING
            return Status.RUNNING


@dataclass
class Repeater(DecoratorNode):
    """
    Repeater node

    Repeat the execution of the child node a specified number of times, or repeat indefinitely.
    """

    repeat_count: int = -1  # -1 表示无限重复
    current_count: int = 0

    async def tick(self, blackboard: Blackboard) -> Status:
        """
        执行重复节点

        重复执行子节点指定次数。

        Args:
            blackboard: 黑板系统

        Returns:
            执行状态
        """
        if not self.child:
            return Status.FAILURE

        # 检查是否达到重复次数限制
        if self.repeat_count > 0 and self.current_count >= self.repeat_count:
            self.status = Status.SUCCESS
            return Status.SUCCESS

        # 执行子节点
        child_status = await self.child.tick(blackboard)

        if child_status == Status.SUCCESS:
            self.current_count += 1

            # 检查是否需要继续重复
            if self.repeat_count == -1 or self.current_count < self.repeat_count:
                # 重置子节点状态，准备下次执行
                self.child.reset()
                self.status = Status.RUNNING
                return Status.RUNNING
            else:
                # 达到重复次数，返回成功
                self.status = Status.SUCCESS
                return Status.SUCCESS

        elif child_status == Status.FAILURE:
            # 子节点失败，重置计数并返回失败
            self.current_count = 0
            self.status = Status.FAILURE
            return Status.FAILURE

        else:  # RUNNING
            self.status = Status.RUNNING
            return Status.RUNNING

    def reset(self) -> None:
        """重置节点状态"""
        super().reset()
        self.current_count = 0

    def set_repeat_count(self, count: int) -> None:
        """
        设置重复次数

        Args:
            count: 重复次数，-1 表示无限重复
        """
        self.repeat_count = count


@dataclass
class UntilSuccess(DecoratorNode):
    """
    直到成功节点

    重复执行子节点直到成功为止。
    """

    async def tick(self, blackboard: Blackboard) -> Status:
        """
        执行直到成功节点

        重复执行子节点直到成功为止。

        Args:
            blackboard: 黑板系统

        Returns:
            执行状态
        """
        if not self.child:
            return Status.FAILURE

        child_status = await self.child.tick(blackboard)

        if child_status == Status.SUCCESS:
            self.status = Status.SUCCESS
            return Status.SUCCESS
        elif child_status == Status.FAILURE:
            # 子节点失败，重置其状态并继续执行
            self.child.reset()
            self.status = Status.RUNNING
            return Status.RUNNING
        else:  # RUNNING
            self.status = Status.RUNNING
            return Status.RUNNING


@dataclass
class UntilFailure(DecoratorNode):
    """
    直到失败节点

    重复执行子节点直到失败为止。
    """

    async def tick(self, blackboard: Blackboard) -> Status:
        """
        执行直到失败节点

        重复执行子节点直到失败为止。

        Args:
            blackboard: 黑板系统

        Returns:
            执行状态
        """
        if not self.child:
            return Status.FAILURE

        child_status = await self.child.tick(blackboard)

        if child_status == Status.FAILURE:
            self.status = Status.SUCCESS
            return Status.SUCCESS
        elif child_status == Status.SUCCESS:
            # 子节点成功，重置其状态并继续执行
            self.child.reset()
            self.status = Status.RUNNING
            return Status.RUNNING
        else:  # RUNNING
            self.status = Status.RUNNING
            return Status.RUNNING

# 为了向后兼容性，提供Decorator作为DecoratorNode的别名
Decorator = DecoratorNode
