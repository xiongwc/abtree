"""
Tick Manager - Behavior Tree Periodic Scheduling and Status Progression

Tick Manager is responsible for controlling the execution frequency and status progression of the behavior tree,
providing both automatic execution and manual control modes.
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..nodes.base import BaseNode
from .blackboard import Blackboard
from ..core.status import Status


@dataclass
class TickManager:
    """
    Tick Manager

    Responsible for controlling the execution frequency and status progression of the behavior tree,
    supporting both automatic execution and manual control modes.

    Attributes:
        tick_rate: Execution frequency (times per second)
        running: Whether the manager is running
        root_node: Root node
        blackboard: Blackboard system
        on_tick: Tick callback function
        on_status_change: Status change callback function
        _task: Asynchronous task
        _last_tick_time: Last execution time
        _tick_count: Execution count statistics
    """

    tick_rate: float = 60.0  # Default 60 FPS
    running: bool = False
    root_node: Optional[BaseNode] = None
    blackboard: Optional[Blackboard] = None
    on_tick: Optional[Callable[[Status], None]] = None
    on_status_change: Optional[Callable[[Status, Status], None]] = None
    _task: Optional[asyncio.Task] = None
    _last_tick_time: float = field(default=0.0, init=False)
    _tick_count: int = field(default=0, init=False)
    _last_status: Status = field(default=Status.FAILURE, init=False)

    def __post_init__(self):
        """Initialize the blackboard after initialization"""
        if self.blackboard is None:
            self.blackboard = Blackboard()

    async def start(self, root_node: Optional[BaseNode] = None) -> None:
        """
        Start the Tick Manager

        Args:
            root_node: Root node, if None then use the current root node
        """
        if root_node is not None:
            self.root_node = root_node

        if self.root_node is None:
            raise ValueError("Root node must be specified")

        if self.running:
            return

        self.running = True
        self._last_tick_time = time.time()
        self._tick_count = 0
        self._last_status = Status.FAILURE

        # Reset root node status
        self.root_node.reset()

        # Create asynchronous task
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        """Stop the Tick Manager"""
        if not self.running:
            return

        self.running = False

        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def tick_once(self) -> Status:
        """
        Execute one Tick

        Returns:
            Execution result status
        """
        if self.root_node is None:
            raise ValueError("Root node is not set")

        if self.blackboard is None:
            raise ValueError("Blackboard system is not set")

        # Execute the root node
        status = await self.root_node.tick(self.blackboard)

        # Update statistics
        self._tick_count += 1
        self._last_tick_time = time.time()

        # Check status change
        if status != self._last_status:
            if self.on_status_change:
                self.on_status_change(self._last_status, status)
            self._last_status = status

        # Call Tick callback
        if self.on_tick:
            self.on_tick(status)

        return status

    async def _run(self) -> None:
        """Internal running loop"""
        tick_interval = 1.0 / self.tick_rate

        while self.running:
            try:
                start_time = time.time()

                # Execute one Tick
                await self.tick_once()

                # Calculate the time to wait
                elapsed = time.time() - start_time
                wait_time = max(0, tick_interval - elapsed)

                if wait_time > 0:
                    await asyncio.sleep(wait_time)

            except asyncio.CancelledError:
                break
            except Exception as e:
                # Record error but continue running
                print(f"Tick execution error: {e}")
                await asyncio.sleep(tick_interval)

    def set_tick_rate(self, rate: float) -> None:
        """
        Set execution frequency

        Args:
            rate: Times per second
        """
        if rate <= 0:
            raise ValueError("Execution frequency must be greater than 0")
        self.tick_rate = rate

    def set_root_node(self, root_node: BaseNode) -> None:
        """
        Set root node

        Args:
            root_node: New root node
        """
        self.root_node = root_node
        if self.running:
            # If running, reset the state
            root_node.reset()

    def set_blackboard(self, blackboard: Blackboard) -> None:
        """
        Set blackboard system

        Args:
            blackboard: Blackboard system
        """
        self.blackboard = blackboard

    def set_on_tick_callback(self, callback: Callable[[Status], None]) -> None:
        """
        Set Tick callback function

        Args:
            callback: Callback function, receive execution status as parameter
        """
        self.on_tick = callback

    def set_on_status_change_callback(
        self, callback: Callable[[Status, Status], None]
    ) -> None:
        """
        Set status change callback function

        Args:
            callback: Callback function, receive old status and new status as parameters
        """
        self.on_status_change = callback

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics

        Returns:
            Statistics dictionary
        """
        return {
            "running": self.running,
            "tick_rate": self.tick_rate,
            "tick_count": self._tick_count,
            "last_tick_time": self._last_tick_time,
            "last_status": self._last_status.name,
            "has_root_node": self.root_node is not None,
            "has_blackboard": self.blackboard is not None,
        }

    def reset_stats(self) -> None:
        """Reset statistics"""
        self._tick_count = 0
        self._last_tick_time = 0.0
        self._last_status = Status.FAILURE

    def is_running(self) -> bool:
        """
        Check if the manager is running

        Returns:
            True if running, False otherwise
        """
        return self.running

    def get_tick_count(self) -> int:
        """
        Get execution count

        Returns:
            Execution count
        """
        return self._tick_count

    def get_last_tick_time(self) -> float:
        """
        Get last execution time

        Returns:
            Last execution timestamp
        """
        return self._last_tick_time

    def get_last_status(self) -> Status:
        """
        Get last execution status

        Returns:
            Last execution status
        """
        return self._last_status

    async def __aenter__(self):
        """Async context manager entry"""
        if self.root_node is not None:
            await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop()

    def __repr__(self) -> str:
        """String representation of the tick manager"""
        stats = self.get_stats()
        return f"TickManager(running={stats['running']}, tick_rate={stats['tick_rate']}, tick_count={stats['tick_count']})"
