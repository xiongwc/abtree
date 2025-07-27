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
import tempfile
import os
from typing import Any, Dict, Set
from abtree import (
    BehaviorTree, Blackboard, EventDispatcher, Status,
    Sequence, Selector, Action, Condition, Log, Wait, SetBlackboard, CheckBlackboard,
    BehaviorForest, ForestNode, ForestNodeType, ForestManager,
    register_node,
)
from abtree.parser.xml_parser import XMLParser
from abtree.forest.communication import (
    CommunicationMiddleware,
    CommunicationType,
    Message,
    Request,
    Response,
    Task,
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


def create_robot_forest_xml() -> str:
    """Create XML configuration for robot behavior forest"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<BehaviorForest name="RobotForest" description="Robot Behavior Forest">
    
    <!-- Robot 001 Behavior Tree -->
    <BehaviorTree name="Robot_001" description="Robot 001 Service">
        <Selector name="Robot 001 Decision">
            <Sequence name="Emergency Response">
                <EmergencyCheckCondition name="Check Emergency" robot_id="001" />
                <EmergencyResponseAction name="Emergency Response" robot_id="001" />
            </Sequence>
            <Sequence name="Battery Management">
                <BatteryCheckCondition name="Check Battery" robot_id="001" threshold="30" />
                <ChargeAction name="Charge" robot_id="001" />
            </Sequence>
            <Sequence name="Task Execution">
                <TaskAvailableCondition name="Check Task" robot_id="001" />
                <TaskExecutionAction name="Execute Task" robot_id="001" task_type="general" />
            </Sequence>
            <PatrolAction name="Patrol" robot_id="001" />
        </Selector>
    </BehaviorTree>
    
    <!-- Robot 002 Behavior Tree -->
    <BehaviorTree name="Robot_002" description="Robot 002 Service">
        <Selector name="Robot 002 Decision">
            <Sequence name="Emergency Response">
                <EmergencyCheckCondition name="Check Emergency" robot_id="002" />
                <EmergencyResponseAction name="Emergency Response" robot_id="002" />
            </Sequence>
            <Sequence name="Battery Management">
                <BatteryCheckCondition name="Check Battery" robot_id="002" threshold="30" />
                <ChargeAction name="Charge" robot_id="002" />
            </Sequence>
            <Sequence name="Task Execution">
                <TaskAvailableCondition name="Check Task" robot_id="002" />
                <TaskExecutionAction name="Execute Task" robot_id="002" task_type="general" />
            </Sequence>
            <PatrolAction name="Patrol" robot_id="002" />
        </Selector>
    </BehaviorTree>
    
    <!-- Coordinator Behavior Tree -->
    <BehaviorTree name="Coordinator" description="Coordinator Service">
        <Sequence name="Coordinator Behavior">
            <Log name="Coordinator Active" message="Coordinator is active" />
            <Wait name="Coordinator Wait" duration="1.0" />
        </Sequence>
    </BehaviorTree>
    
    <!-- Monitor Behavior Tree -->
    <BehaviorTree name="Monitor" description="Monitor Service">
        <Sequence name="Monitor Behavior">
            <Log name="Monitor Active" message="Monitor is active" />
            <Wait name="Monitor Wait" duration="2.0" />
        </Sequence>
    </BehaviorTree>   
 
    
</BehaviorForest>'''


async def demonstrate_pubsub_pattern(forest: BehaviorForest):
    """Demonstrate PubSub communication pattern"""
    print("\n=== PubSub Communication Pattern ===")
    
    # Get communication middleware
    comm_middleware = None
    for middleware in forest.middleware:
        if isinstance(middleware, CommunicationMiddleware):
            comm_middleware = middleware
            break
    
    if not comm_middleware:
        print("❌ Communication middleware not found")
        return
    
    # Register event handlers
    def emergency_handler(event):
        print(f"📡 PubSub: Emergency event received: {event}")
    
    def task_handler(event):
        print(f"📡 PubSub: Task event received: {event}")
    
    # Subscribe to events
    comm_middleware.subscribe("emergency_events", emergency_handler)
    comm_middleware.subscribe("task_events", task_handler)
    
    # Publish events
    await comm_middleware.publish("emergency_events", {"location": "Zone A", "severity": "high"}, "Coordinator")
    await comm_middleware.publish("task_events", {"type": "patrol", "area": "Zone B"}, "Coordinator")


async def demonstrate_reqresp_pattern(forest: BehaviorForest):
    """Demonstrate Request-Response communication pattern"""
    print("\n=== Request-Response Communication Pattern ===")
    
    # Get communication middleware
    comm_middleware = None
    for middleware in forest.middleware:
        if isinstance(middleware, CommunicationMiddleware):
            comm_middleware = middleware
            break
    
    if not comm_middleware:
        print("❌ Communication middleware not found")
        return
    
    # Register request handlers
    async def get_battery_status(params, source):
        print(f"📡 ReqResp: Battery status request from {source}")
        return {"battery_level": 75, "charging": False}
    
    async def get_task_status(params, source):
        print(f"📡 ReqResp: Task status request from {source}")
        return {"task_count": 3, "completed": 1}
    
    # Register handlers
    comm_middleware.register_service("battery_status", get_battery_status)
    comm_middleware.register_service("task_status", get_task_status)
    
    # Make requests
    battery_response = await comm_middleware.request("battery_status", {}, "Robot_001")
    task_response = await comm_middleware.request("task_status", {}, "Coordinator")
    
    print(f"📡 ReqResp: Battery response: {battery_response}")
    print(f"📡 ReqResp: Task response: {task_response}")


async def demonstrate_shared_blackboard_pattern(forest: BehaviorForest):
    """Demonstrate Shared Blackboard communication pattern"""
    print("\n=== Shared Blackboard Communication Pattern ===")
    
    # Get communication middleware
    comm_middleware = None
    for middleware in forest.middleware:
        if isinstance(middleware, CommunicationMiddleware):
            comm_middleware = middleware
            break
    
    if not comm_middleware:
        print("❌ Communication middleware not found")
        return
    
    # Set shared data
    comm_middleware.set("system_status", "operational", "Coordinator")
    comm_middleware.set("emergency", False, "Coordinator")
    comm_middleware.set("battery_level", 85, "Robot_001")
    comm_middleware.set("task_available", True, "Coordinator")
    
    # Read shared data
    system_status = comm_middleware.get("system_status", "unknown", "Robot_001")
    emergency = comm_middleware.get("emergency", False, "Robot_002")
    battery_level = comm_middleware.get("battery_level", 0, "Monitor")
    task_available = comm_middleware.get("task_available", False, "Monitor")
    
    print(f"📊 Shared data - System: {system_status}, Emergency: {emergency}")
    print(f"📊 Shared data - Battery: {battery_level}%, Task available: {task_available}")


async def demonstrate_state_watching_pattern(forest: BehaviorForest):
    """Demonstrate State Watching communication pattern"""
    print("\n=== State Watching Communication Pattern ===")
    
    # Get communication middleware
    comm_middleware = None
    for middleware in forest.middleware:
        if isinstance(middleware, CommunicationMiddleware):
            comm_middleware = middleware
            break
    
    if not comm_middleware:
        print("❌ Communication middleware not found")
        return
    
    # Watch for state changes
    def emergency_state_handler(key, old_value, new_value, source):
        print(f"🚨 Emergency state changed: {old_value} -> {new_value} (from {source})")
    
    def battery_state_handler(key, old_value, new_value, source):
        print(f"🔋 Battery state changed: {old_value} -> {new_value} (from {source})")
    
    comm_middleware.watch_state("emergency_state", emergency_state_handler, "Monitor")
    comm_middleware.watch_state("battery_state", battery_state_handler, "Monitor")
    
    # Update states
    await comm_middleware.update_state("emergency_state", True, "Coordinator")
    await comm_middleware.update_state("battery_state", 15, "Robot_001")
    await comm_middleware.update_state("emergency_state", False, "Coordinator")


async def demonstrate_behavior_call_pattern(forest: BehaviorForest):
    """Demonstrate Behavior Call communication pattern"""
    print("\n=== Behavior Call Communication Pattern ===")
    
    # Get communication middleware
    comm_middleware = None
    for middleware in forest.middleware:
        if isinstance(middleware, CommunicationMiddleware):
            comm_middleware = middleware
            break
    
    if not comm_middleware:
        print("❌ Communication middleware not found")
        return
    
    # Register behaviors
    async def patrol_behavior(params):
        print(f"📡 BehaviorCall: Patrol behavior called with params: {params}")
        return {"status": "patrolling", "area": params.get("area", "default")}
    
    async def charge_behavior(params):
        print(f"📡 BehaviorCall: Charge behavior called with params: {params}")
        return {"status": "charging", "duration": params.get("duration", 60)}
    
    comm_middleware.register_behavior("patrol_behavior", patrol_behavior)
    comm_middleware.register_behavior("charge_behavior", charge_behavior)
    
    # Call behaviors
    patrol_result = await comm_middleware.call_behavior("patrol_behavior", {"area": "Zone A"}, "Coordinator")
    charge_result = await comm_middleware.call_behavior("charge_behavior", {"duration": 120}, "Robot_001")
    
    print(f"📡 BehaviorCall: Patrol result: {patrol_result}")
    print(f"📡 BehaviorCall: Charge result: {charge_result}")


async def demonstrate_task_board_pattern(forest: BehaviorForest):
    """Demonstrate Task Board communication pattern"""
    print("\n=== Task Board Communication Pattern ===")
    
    # Get communication middleware
    comm_middleware = None
    for middleware in forest.middleware:
        if isinstance(middleware, CommunicationMiddleware):
            comm_middleware = middleware
            break
    
    if not comm_middleware:
        print("❌ Communication middleware not found")
        return
    
    # Publish tasks
    comm_middleware.publish_task("patrol_task", "Patrol area", {"patrol"}, 0, {"area": "Zone A", "priority": "high"})
    comm_middleware.publish_task("maintenance_task", "Perform maintenance", {"maintenance"}, 0, {"type": "routine", "priority": "medium"})
    
    # Get available tasks
    available_tasks = comm_middleware.get_available_tasks({"patrol", "maintenance"})
    print(f"📡 TaskBoard: Available tasks: {len(available_tasks)}")
    
    # Claim task
    if available_tasks:
        task = available_tasks[0]
        claimed = comm_middleware.claim_task(task.id, "Robot_001", {"patrol", "maintenance"})
        print(f"📡 TaskBoard: Robot_001 claimed task: {claimed}")
        
        if claimed:
            # Complete task
            comm_middleware.complete_task(task.id, {"result": "success"})
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
    
    # Create XML configuration
    xml_config = create_robot_forest_xml()
    
    # Create temporary XML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        f.write(xml_config)
        xml_file_path = f.name
    
    try:
        # Initialize XML parser
        parser = XMLParser()
        
        # Load behavior forest from XML
        print("Loading behavior forest from XML configuration...")
        forest = parser.parse_file(xml_file_path)
        
        print(f"Successfully loaded forest: {forest.name}")
        print(f"Forest contains {len(forest.nodes)} behavior trees:")
        
        for node_name, node in forest.nodes.items():
            print(f"  - {node_name} ({node.node_type.name})")
        
        print(f"\nForest middleware: {len(forest.middleware)} middleware components")
        
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
        
    finally:
        # Clean up temporary file
        os.unlink(xml_file_path)


if __name__ == "__main__":
    asyncio.run(main()) 