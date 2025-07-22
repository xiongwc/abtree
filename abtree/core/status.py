"""
Status and policy enumeration definitions
"""

from enum import IntEnum
from typing import Any


class Status(IntEnum):
    """
    Behavior tree node execution status enumeration

    Defines the three possible states that a behavior tree node can return after execution:
    - SUCCESS: Node execution succeeded
    - FAILURE: Node execution failed
    - RUNNING: Node is currently executing
    """

    SUCCESS = 1
    FAILURE = 0
    RUNNING = 2

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Status.{self.name}"


class Policy(IntEnum):
    """
    Parallel node execution policy enumeration

    Defines the policy used by parallel nodes when executing child nodes:
    - SUCCEED_ON_ONE: One child node succeeds, then succeed
    - SUCCEED_ON_ALL: All child nodes must succeed to succeed
    - FAIL_ON_ONE: One child node fails, then fail
    - FAIL_ON_ALL: All child nodes must fail to fail
    """

    SUCCEED_ON_ONE = 1
    SUCCEED_ON_ALL = 2
    FAIL_ON_ONE = 3
    FAIL_ON_ALL = 4

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Policy.{self.name}"
