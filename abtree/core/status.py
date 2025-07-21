"""
Status and policy enumeration definitions
"""

from enum import Enum, auto
from typing import Any


class Status(Enum):
    """
    Behavior tree node execution status enumeration

    Defines the three possible states that a behavior tree node can return after execution:
    - SUCCESS: Node execution succeeded
    - FAILURE: Node execution failed
    - RUNNING: Node is currently executing
    """

    SUCCESS = auto()
    FAILURE = auto()
    RUNNING = auto()

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Status.{self.name}"


class Policy(Enum):
    """
    Parallel node execution policy enumeration

    Defines the policy used by parallel nodes when executing child nodes:
    - SUCCEED_ON_ONE: One child node succeeds, then succeed
    - SUCCEED_ON_ALL: All child nodes must succeed to succeed
    - FAIL_ON_ONE: One child node fails, then fail
    - FAIL_ON_ALL: All child nodes must fail to fail
    """

    SUCCEED_ON_ONE = auto()
    SUCCEED_ON_ALL = auto()
    FAIL_ON_ONE = auto()
    FAIL_ON_ALL = auto()

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Policy.{self.name}"
