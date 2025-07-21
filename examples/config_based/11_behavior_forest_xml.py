#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 11: Behavior Forest - XML Configuration Version

This is the XML configuration version of the Behavior Forest example.
It demonstrates how to configure behavior forests using XML.

Key Learning Points:
    - How to define behavior forests using XML
    - How to configure forest nodes and communication patterns
    - How to implement multi-agent collaboration with XML
    - Understanding forest management in XML configuration
"""

import asyncio
import random
from typing import Any, Dict, Set
from abtree import (
    BehaviorTree, Blackboard, EventSystem, Status,
    Sequence, Selector, Action, Condition, Log, Wait, SetBlackboard, CheckBlackboard,
    BehaviorForest, ForestNode, ForestNodeType, ForestManager, ForestConfig,
    PubSubMiddleware, ReqRespMiddleware, SharedBlackboardMiddleware,
    StateWatchingMiddleware, BehaviorCallMiddleware, TaskBoardMiddleware,
    register_node,
)


class RobotAction(Action):
    """Base robot action node"""
    
    def __init__(self, name: str, robot_id: str):
        self.name = name
        self.robot_id = robot_id
    
    async def execute(self, blackboard):
        print(f"🤖 {self.robot_id}: {self.name}")
        return Status.SUCCESS


class PatrolAction(RobotAction):
    """Patrol action for robots"""
    
    async def execute(self, blackboard):
        await super().execute(blackboard)
        print(f"   📍 {self.robot_id} is patrolling area")
        await asyncio.sleep(0.05)
        return Status.SUCCESS


class ChargeAction(RobotAction):
    """Charging action for robots"""
    
    async def execute(self, blackboard):
        await super().execute(blackboard)
        battery_level = blackboard.get("battery_level", 50)
        if battery_level < 30:
            print(f"   🔋 {self.robot_id} is charging (battery: {battery_level}%)")
            blackboard.set("battery_level", min(100, battery_level + 20))
            await asyncio.sleep(0.01)
            return Status.SUCCESS
        else:
            print(f"   ✅ {self.robot_id} battery is sufficient ({battery_level}%)")
            return Status.SUCCESS


class EmergencyResponseAction(RobotAction):
    """Emergency response action"""
    
    async def execute(self, blackboard):
        await super().execute(blackboard)
        print(f"   🚨 {self.robot_id} responding to emergency!")
        await asyncio.sleep(0.03)
        return Status.SUCCESS


class TaskExecutionAction(RobotAction):
    """Task execution action"""
    
    def __init__(self, name: str, robot_id: str, task_type: str):
        super().__init__(name, robot_id)
        self.task_type = task_type
    
    async def execute(self, blackboard):
        await super().execute(blackboard)
        print(f"   📋 {self.robot_id} executing {self.task_type} task")
        await asyncio.sleep(0.08)
        return Status.SUCCESS


class BatteryCheckCondition(Condition):
    """Check battery level condition"""
    
    def __init__(self, name: str, robot_id: str, threshold: int = 30):
        self.name = name
        self.robot_id = robot_id
        self.threshold = threshold
    
    async def evaluate(self, blackboard):
        battery_level = blackboard.get("battery_level", 50)
        is_low = battery_level < self.threshold
        print(f"   🔋 {self.robot_id} battery check: {battery_level}% (threshold: {self.threshold}%)")
        return is_low


class EmergencyCheckCondition(Condition):
    """Check for emergency condition"""
    
    def __init__(self, name: str, robot_id: str):
        self.name = name
        self.robot_id = robot_id
    
    async def evaluate(self, blackboard):
        emergency = blackboard.get("emergency", False)
        print(f"   🚨 {self.robot_id} emergency check: {emergency}")
        return emergency


class TaskAvailableCondition(Condition):
    """Check if task is available"""
    
    def __init__(self, name: str, robot_id: str):
        self.name = name
        self.robot_id = robot_id
    
    async def evaluate(self, blackboard):
        task_available = blackboard.get("task_available", False)
        print(f"   📋 {self.robot_id} task check: {task_available}")
        return task_available


def create_robot_forest_node(robot_id: str, capabilities: Set[str]) -> ForestNode:
    """Create a robot forest node"""
    
    # Create behavior tree for robot
    tree = BehaviorTree()
    
    # Define robot behavior based on capabilities
    if "patrol" in capabilities:
        root = Selector("Robot Behavior")
        
        # Emergency response (highest priority)
        emergency_sequence = Sequence("Emergency Response")
        emergency_sequence.add_child(EmergencyCheckCondition("Check Emergency", robot_id))
        emergency_sequence.add_child(EmergencyResponseAction("Emergency Response", robot_id))
        root.add_child(emergency_sequence)
        
        # Battery management
        battery_sequence = Sequence("Battery Management")
        battery_sequence.add_child(BatteryCheckCondition("Check Battery", robot_id))
        battery_sequence.add_child(ChargeAction("Charge", robot_id))
        root.add_child(battery_sequence)
        
        # Task execution
        task_sequence = Sequence("Task Execution")
        task_sequence.add_child(TaskAvailableCondition("Check Task", robot_id))
        task_sequence.add_child(TaskExecutionAction("Execute Task", robot_id, "general"))
        root.add_child(task_sequence)
        
        # Default patrol behavior
        patrol_sequence = Sequence("Patrol")
        patrol_sequence.add_child(PatrolAction("Patrol", robot_id))
        root.add_child(patrol_sequence)
        
        tree.load_from_root(root)
    
    return ForestNode(
        name=f"Robot_{robot_id}",
        node_type=ForestNodeType.WORKER,
        tree=tree,
        capabilities=capabilities
    )


def create_coordinator_forest_node() -> ForestNode:
    """Create a coordinator forest node"""
    
    # Create behavior tree for coordinator
    tree = BehaviorTree()
    
    # Simple coordinator behavior
    root = Sequence("Coordinator Behavior")
    root.add_child(Log("Coordinator Active"))
    root.add_child(Wait(1.0))
    
    tree.load_from_root(root)
    
    return ForestNode(
        name="Coordinator",
        node_type=ForestNodeType.COORDINATOR,
        tree=tree,
        capabilities={"coordinate", "monitor"}
    )


def create_monitor_forest_node() -> ForestNode:
    """Create a monitor forest node"""
    
    # Create behavior tree for monitor
    tree = BehaviorTree()
    
    # Simple monitor behavior
    root = Sequence("Monitor Behavior")
    root.add_child(Log("Monitor Active"))
    root.add_child(Wait(2.0))
    
    tree.load_from_root(root)
    
    return ForestNode(
        name="Monitor",
        node_type=ForestNodeType.MONITOR,
        tree=tree,
        capabilities={"monitor", "log"}
    )


async def demonstrate_pubsub_pattern(forest: BehaviorForest):
    """Demonstrate PubSub communication pattern"""
    print("\n=== PubSub Communication Pattern ===")
    
    # Get pub/sub middleware
    pubsub = None
    for middleware in forest.middleware:
        if isinstance(middleware, PubSubMiddleware):
            pubsub = middleware
            break
    
    if not pubsub:
        print("❌ Pub/Sub middleware not found")
        return
    
    # Register event handlers
    def emergency_handler(event):
        print(f"📡 PubSub: Emergency event received: {event}")
    
    def task_handler(event):
        print(f"📡 PubSub: Task event received: {event}")
    
    # Subscribe to events
    pubsub.subscribe("emergency", emergency_handler)
    pubsub.subscribe("task", task_handler)
    
    # Publish events
    await pubsub.publish("emergency", {"location": "Zone A", "severity": "high"}, "Coordinator")
    await pubsub.publish("task", {"type": "patrol", "area": "Zone B"}, "Coordinator")


async def demonstrate_reqresp_pattern(forest: BehaviorForest):
    """Demonstrate Request-Response communication pattern"""
    print("\n=== Request-Response Communication Pattern ===")
    
    # Get req/resp middleware
    reqresp = None
    for middleware in forest.middleware:
        if isinstance(middleware, ReqRespMiddleware):
            reqresp = middleware
            break
    
    if not reqresp:
        print("❌ Req/Resp middleware not found")
        return
    
    # Register request handlers
    async def get_battery_status(params, source):
        print(f"📡 ReqResp: Battery status request from {source}")
        return {"battery_level": 75, "charging": False}
    
    async def get_task_status(params, source):
        print(f"📡 ReqResp: Task status request from {source}")
        return {"task_count": 3, "completed": 1}
    
    # Register handlers
    reqresp.register_service("get_battery_status", get_battery_status)
    reqresp.register_service("get_task_status", get_task_status)
    
    # Make requests
    battery_response = await reqresp.request("get_battery_status", {}, "Robot_001")
    task_response = await reqresp.request("get_task_status", {}, "Coordinator")
    
    print(f"📡 ReqResp: Battery response: {battery_response}")
    print(f"📡 ReqResp: Task response: {task_response}")


async def demonstrate_shared_blackboard_pattern(forest: BehaviorForest):
    """Demonstrate Shared Blackboard communication pattern"""
    print("\n=== Shared Blackboard Communication Pattern ===")
    
    # Get shared blackboard middleware
    shared_bb = None
    for middleware in forest.middleware:
        if isinstance(middleware, SharedBlackboardMiddleware):
            shared_bb = middleware
            break
    
    if not shared_bb:
        print("❌ Shared Blackboard middleware not found")
        return
    
    # Set shared data
    shared_bb.set("system_status", "operational", "Coordinator")
    shared_bb.set("active_robots", 3, "Coordinator")
    shared_bb.set("emergency_level", "normal", "Coordinator")
    
    # Read shared data
    system_status = shared_bb.get("system_status", "unknown", "Robot_001")
    active_robots = shared_bb.get("active_robots", 0, "Robot_002")
    emergency_level = shared_bb.get("emergency_level", "unknown", "Monitor")
    
    print(f"📊 Shared data - System: {system_status}, Robots: {active_robots}, Emergency: {emergency_level}")


async def demonstrate_state_watching_pattern(forest: BehaviorForest):
    """Demonstrate State Watching communication pattern"""
    print("\n=== State Watching Communication Pattern ===")
    
    # Get state watching middleware
    state_watch = None
    for middleware in forest.middleware:
        if isinstance(middleware, StateWatchingMiddleware):
            state_watch = middleware
            break
    
    if not state_watch:
        print("❌ State Watching middleware not found")
        return
    
    # Watch for state changes
    def emergency_state_handler(key, old_value, new_value, source):
        print(f"🚨 Emergency state changed: {old_value} -> {new_value} (from {source})")
    
    def battery_state_handler(key, old_value, new_value, source):
        print(f"🔋 Battery state changed: {old_value} -> {new_value} (from {source})")
    
    state_watch.watch_state("emergency_level", emergency_state_handler, "Monitor")
    state_watch.watch_state("battery_level", battery_state_handler, "Monitor")
    
    # Update states
    await state_watch.update_state("emergency_level", "high", "Coordinator")
    await state_watch.update_state("battery_level", 15, "Robot_001")
    await state_watch.update_state("emergency_level", "critical", "Coordinator")


async def demonstrate_behavior_call_pattern(forest: BehaviorForest):
    """Demonstrate Behavior Call communication pattern"""
    print("\n=== Behavior Call Communication Pattern ===")
    
    # Get behavior call middleware
    behavior_call = None
    for middleware in forest.middleware:
        if isinstance(middleware, BehaviorCallMiddleware):
            behavior_call = middleware
            break
    
    if not behavior_call:
        print("❌ Behavior Call middleware not found")
        return
    
    # Register behaviors
    async def patrol_behavior(params):
        print(f"📡 BehaviorCall: Patrol behavior called with params: {params}")
        return {"status": "patrolling", "area": params.get("area", "default")}
    
    async def charge_behavior(params):
        print(f"📡 BehaviorCall: Charge behavior called with params: {params}")
        return {"status": "charging", "duration": params.get("duration", 60)}
    
    behavior_call.register_behavior("patrol", patrol_behavior)
    behavior_call.register_behavior("charge", charge_behavior)
    
    # Call behaviors
    patrol_result = await behavior_call.call_behavior("patrol", {"area": "Zone A"}, "Coordinator")
    charge_result = await behavior_call.call_behavior("charge", {"duration": 120}, "Robot_001")
    
    print(f"📡 BehaviorCall: Patrol result: {patrol_result}")
    print(f"📡 BehaviorCall: Charge result: {charge_result}")


async def demonstrate_task_board_pattern(forest: BehaviorForest):
    """Demonstrate Task Board communication pattern"""
    print("\n=== Task Board Communication Pattern ===")
    
    # Get task board middleware
    task_board = None
    for middleware in forest.middleware:
        if isinstance(middleware, TaskBoardMiddleware):
            task_board = middleware
            break
    
    if not task_board:
        print("❌ Task Board middleware not found")
        return
    
    # Post tasks
    task_board.post_task("patrol", {"area": "Zone A", "priority": "high"})
    task_board.post_task("charge", {"duration": 60, "priority": "medium"})
    task_board.post_task("maintenance", {"type": "routine", "priority": "low"})
    
    # Get available tasks
    available_tasks = task_board.get_available_tasks()
    print(f"📡 TaskBoard: Available tasks: {available_tasks}")
    
    # Claim task
    claimed_task = task_board.claim_task("Robot_001", "patrol")
    print(f"📡 TaskBoard: Robot_001 claimed task: {claimed_task}")
    
    # Complete task
    task_board.complete_task("Robot_001", "patrol", {"result": "success"})
    print("📡 TaskBoard: Task completed")


def register_custom_nodes():
    """Register custom node types for XML parsing"""
    register_node("RobotAction", RobotAction)
    register_node("PatrolAction", PatrolAction)
    register_node("ChargeAction", ChargeAction)
    register_node("EmergencyResponseAction", EmergencyResponseAction)
    register_node("TaskExecutionAction", TaskExecutionAction)
    register_node("BatteryCheckCondition", BatteryCheckCondition)
    register_node("EmergencyCheckCondition", EmergencyCheckCondition)
    register_node("TaskAvailableCondition", TaskAvailableCondition)


async def main():
    """Main function - demonstrate XML-based behavior forest configuration"""
    
    print("=== ABTree Behavior Forest XML Configuration Example ===\n")
    
    # Register custom node types for XML parsing
    register_custom_nodes()
    
    # Create forest configuration
    config = ForestConfig(
        name="Robot Forest",
        tick_rate=1.0
    )
    
    # Create behavior forest
    forest = BehaviorForest(config)
    
    # Create forest nodes
    robot1_node = create_robot_forest_node("001", {"patrol", "charge", "emergency"})
    robot2_node = create_robot_forest_node("002", {"patrol", "task"})
    coordinator_node = create_coordinator_forest_node()
    monitor_node = create_monitor_forest_node()
    
    # Add nodes to forest
    forest.add_node(robot1_node)
    forest.add_node(robot2_node)
    forest.add_node(coordinator_node)
    forest.add_node(monitor_node)
    
    print("Behavior forest configured with XML-compatible nodes:")
    print(f"  - {robot1_node.name} (capabilities: {robot1_node.capabilities})")
    print(f"  - {robot2_node.name} (capabilities: {robot2_node.capabilities})")
    print(f"  - {coordinator_node.name} (capabilities: {coordinator_node.capabilities})")
    print(f"  - {monitor_node.name} (capabilities: {monitor_node.capabilities})")
    
    # Demonstrate communication patterns
    await demonstrate_pubsub_pattern(forest)
    await demonstrate_reqresp_pattern(forest)
    await demonstrate_shared_blackboard_pattern(forest)
    await demonstrate_state_watching_pattern(forest)
    await demonstrate_behavior_call_pattern(forest)
    await demonstrate_task_board_pattern(forest)
    
    print("\n=== Forest Execution ===")
    print("Starting behavior forest execution...")
    
    # Start forest
    await forest.start()
    
    # Run for a few ticks
    for i in range(3):
        print(f"\n--- Forest Tick {i+1} ---")
        await asyncio.sleep(0.01)
    
    # Stop forest
    await forest.stop()
    
    print("\nBehavior forest execution completed!")


if __name__ == "__main__":
    asyncio.run(main()) 