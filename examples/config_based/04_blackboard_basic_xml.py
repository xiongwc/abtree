#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 04: Blackboard Basic - XML Configuration Version

This is the XML configuration version of the Blackboard Basic example.
It demonstrates how to configure blackboard-based behavior trees using XML.

Key Learning Points:
    - How to define blackboard-based nodes using XML
    - How to register custom condition and action node types
    - How to parse XML configuration with blackboard operations
    - Understanding blackboard data flow in XML configuration
"""

import asyncio
from abtree import BehaviorTree, Action, Condition, register_node
from abtree.core import Status


class CheckBatteryCondition(Condition):
    """Check if battery level is sufficient"""
    
    async def evaluate(self, blackboard):
        battery_level = blackboard.get("battery_level", 100)
        print(f"Checking battery level: {battery_level}%")
        
        if battery_level < 20:
            print("Battery level too low, need charging")
            return False
        else:
            print("Battery level sufficient")
            return True


class CheckDoorCondition(Condition):
    """Check if door is open"""
    
    async def evaluate(self, blackboard):
        door_open = blackboard.get("door_open", False)
        print(f"Checking door status: {'Open' if door_open else 'Closed'}")
        return door_open


class CloseDoorAction(Action):
    """Action to close the door"""
    
    async def execute(self, blackboard):
        print("Closing door...")
        await asyncio.sleep(0.01)
        
        blackboard.set("door_open", False)
        blackboard.set("last_action", "Close Door")
        blackboard.set("action_count", blackboard.get("action_count", 0) + 1)
        
        print("Door closed successfully")
        return Status.SUCCESS


class ChargeBatteryAction(Action):
    """Action to charge battery"""
    
    async def execute(self, blackboard):
        print("Charging battery...")
        await asyncio.sleep(0.01)
        
        current_battery = blackboard.get("battery_level", 0)
        new_battery = min(100, current_battery + 30)
        blackboard.set("battery_level", new_battery)
        blackboard.set("last_action", "Charge Battery")
        blackboard.set("action_count", blackboard.get("action_count", 0) + 1)
        
        print(f"Battery charged to {new_battery}%")
        return Status.SUCCESS


class PatrolAction(Action):
    """Action to patrol the area"""
    
    async def execute(self, blackboard):
        print("Patrolling area...")
        await asyncio.sleep(0.01)
        
        current_battery = blackboard.get("battery_level", 100)
        new_battery = max(0, current_battery - 10)
        blackboard.set("battery_level", new_battery)
        blackboard.set("last_action", "Patrol")
        blackboard.set("action_count", blackboard.get("action_count", 0) + 1)
        
        print(f"Patrol completed, remaining battery: {new_battery}%")
        return Status.SUCCESS


def register_custom_nodes():
    """Register custom node types for XML parsing"""
    register_node("CheckBatteryCondition", CheckBatteryCondition)
    register_node("CheckDoorCondition", CheckDoorCondition)
    register_node("CloseDoorAction", CloseDoorAction)
    register_node("ChargeBatteryAction", ChargeBatteryAction)
    register_node("PatrolAction", PatrolAction)


async def main():
    """Main function - demonstrate XML-based blackboard configuration"""
    
    print("=== ABTree Blackboard Basic XML Configuration Example ===\n")
    
    # Register custom node types for XML parsing
    register_custom_nodes()
    
    # XML string configuration
    xml_config = '''
    <BehaviorTree name="BlackboardBasicXML" description="Blackboard basic example with XML configuration">
        <Sequence name="Root Sequence">
            <Sequence name="Robot Task">
                <CheckBatteryCondition name="Check Battery" />
                <CheckDoorCondition name="Check Door" />
                <CloseDoorAction name="Close Door" />
                <PatrolAction name="Patrol" />
            </Sequence>
        </Sequence>
    </BehaviorTree>
    '''
    
    # Parse XML configuration
    xml_tree = BehaviorTree()
    xml_tree.load_from_string(xml_config)
    xml_blackboard = xml_tree.blackboard
    
    # Initialize XML-configured blackboard data
    xml_blackboard.set("battery_level", 90)
    xml_blackboard.set("door_open", True)
    xml_blackboard.set("action_count", 0)
    
    print("Behavior tree configured by XML string:")
    print(xml_config.strip())
    print("\nInitial state:")
    print(f"  Battery level: {xml_blackboard.get('battery_level')}%")
    print(f"  Door status: {'Open' if xml_blackboard.get('door_open') else 'Closed'}")
    print(f"  Action count: {xml_blackboard.get('action_count')}")
    
    print("\nStarting execution of XML-configured behavior tree...")
    xml_result = await xml_tree.tick()
    
    print(f"\nXML configuration execution completed! Result: {xml_result}")
    print("\nFinal state:")
    print(f"  Battery level: {xml_blackboard.get('battery_level')}%")
    print(f"  Door status: {'Open' if xml_blackboard.get('door_open') else 'Closed'}")
    print(f"  Last action: {xml_blackboard.get('last_action')}")
    print(f"  Action count: {xml_blackboard.get('action_count')}")
    
    # Demonstrate low battery scenario
    print("\n=== Demonstrate Low Battery Scenario ===")
    xml_blackboard.set("battery_level", 15)
    xml_blackboard.set("door_open", False)
    
    print("Battery level low, should execute charging...")
    result2 = await xml_tree.tick()
    print(f"Execution result: {result2}")
    print(f"Current battery: {xml_blackboard.get('battery_level')}%")


if __name__ == "__main__":
    asyncio.run(main()) 