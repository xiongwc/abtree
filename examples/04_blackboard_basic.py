#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 04: Blackboard Basics – Using the Blackboard System

Demonstrates how to use the blackboard system to share data between nodes.
The blackboard is the core mechanism for cross-node data sharing in ABTree.

Key Learning Points:

    Basic operations of the blackboard

    Data sharing mechanisms

    Interactions between condition nodes and the blackboard

    Modifying blackboard data in action nodes

    How to configure blackboard-related behavior trees using XML strings
"""

import asyncio
from abtree import BehaviorTree, Sequence, Action, Condition, register_node
from abtree.core import Status
from abtree.parser.xml_parser import XMLParser


# Register custom node types
def register_custom_nodes():
    """Register custom node types"""
    register_node("CheckBatteryCondition", CheckBatteryCondition)
    register_node("CheckDoorCondition", CheckDoorCondition)
    register_node("CloseDoorAction", CloseDoorAction)
    register_node("ChargeBatteryAction", ChargeBatteryAction)
    register_node("PatrolAction", PatrolAction)


class CheckBatteryCondition(Condition):
    """Check battery level"""
    
    async def evaluate(self, blackboard):
        battery_level = blackboard.get("battery_level", 100)
        print(f"Checking battery level: {battery_level}%")
        return battery_level > 20


class CheckDoorCondition(Condition):
    """Check door status"""
    
    async def evaluate(self, blackboard):
        door_open = blackboard.get("door_open", False)
        print(f"Checking door status: {'Open' if door_open else 'Closed'}")
        return door_open


class CloseDoorAction(Action):
    """Close door"""
    
    async def execute(self, blackboard):
        print("Executing door closing operation...")
        await asyncio.sleep(0.01)
        
        # Modify blackboard data
        blackboard.set("door_open", False)
        blackboard.set("last_action", "Close Door")
        blackboard.set("action_count", blackboard.get("action_count", 0) + 1)
        
        print("Door closed")
        return Status.SUCCESS


class ChargeBatteryAction(Action):
    """Charge battery"""
    
    async def execute(self, blackboard):
        print("Starting charging...")
        await asyncio.sleep(0.01)
        
        # Modify blackboard data
        current_battery = blackboard.get("battery_level", 0)
        new_battery = min(100, current_battery + 50)
        blackboard.set("battery_level", new_battery)
        blackboard.set("last_action", "Charge Battery")
        blackboard.set("action_count", blackboard.get("action_count", 0) + 1)
        
        print(f"Charging completed, current battery: {new_battery}%")
        return Status.SUCCESS


class PatrolAction(Action):
    """Patrol"""
    
    async def execute(self, blackboard):
        print("Starting patrol...")
        await asyncio.sleep(0.01)
        
        # Consume battery
        current_battery = blackboard.get("battery_level", 100)
        new_battery = max(0, current_battery - 10)
        blackboard.set("battery_level", new_battery)
        blackboard.set("last_action", "Patrol")
        blackboard.set("action_count", blackboard.get("action_count", 0) + 1)
        
        print(f"Patrol completed, remaining battery: {new_battery}%")
        return Status.SUCCESS


async def main():
    """Main function - demonstrate blackboard system usage"""
    
    # Register custom node types
    register_custom_nodes()
    
    print("=== ABTree Blackboard Basic Example ===\n")
    
    # 1. Create behavior tree
    root = Sequence("Robot Task")
    
    # 2. Add child nodes
    root.add_child(CheckBatteryCondition("Check Battery"))
    root.add_child(CheckDoorCondition("Check Door"))
    root.add_child(CloseDoorAction("Close Door"))
    root.add_child(PatrolAction("Patrol"))
    
    # 3. Create behavior tree
    tree = BehaviorTree()
    tree.load_from_node(root)
    blackboard = tree.blackboard
    
    # 4. Initialize blackboard data
    blackboard.set("battery_level", 80)
    blackboard.set("door_open", True)
    blackboard.set("action_count", 0)
    
    print("Initial state:")
    print(f"  Battery level: {blackboard.get('battery_level')}%")
    print(f"  Door status: {'Open' if blackboard.get('door_open') else 'Closed'}")
    print(f"  Action count: {blackboard.get('action_count')}")
    
    # 5. Execute behavior tree
    print("\nStarting task execution...")
    result = await tree.tick()
    
    # 6. Display final state
    print(f"\nExecution result: {result}")
    print("\nFinal state:")
    print(f"  Battery level: {blackboard.get('battery_level')}%")
    print(f"  Door status: {'Open' if blackboard.get('door_open') else 'Closed'}")
    print(f"  Last action: {blackboard.get('last_action')}")
    print(f"  Action count: {blackboard.get('action_count')}")
    
    # 7. Demonstrate low battery scenario
    print("\n=== Demonstrate Low Battery Scenario ===")
    blackboard.set("battery_level", 15)
    blackboard.set("door_open", False)
    
    print("Battery level low, should execute charging...")
    result2 = await tree.tick()
    print(f"Execution result: {result2}")
    print(f"Current battery: {blackboard.get('battery_level')}%")
    
    # 8. Demonstrate XML configuration method
    print("\n=== XML Configuration Method Demo ===")   


if __name__ == "__main__":
    asyncio.run(main()) 