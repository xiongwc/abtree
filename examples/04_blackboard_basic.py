#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 04: Blackboard Basic - {} Parameter Passing Demo

Demonstrates {} parameter passing in node configuration.
Shows how variables from blackboard are substituted into node parameters.
"""

import asyncio
from abtree import BehaviorTree, Action, Condition, register_node
from abtree.core import Status


class CheckValueCondition(Condition):
    """Check if value exceeds threshold"""
    
    def __init__(self, name: str = "", **kwargs):
        super().__init__(name)
        self.params = kwargs
    
    async def evaluate(self):
        threshold = self.blackboard.get("threshold", 50)
        value = self.blackboard.get("current_value", 0)
        
        print(f"Check: {value} > {threshold} = {value > threshold}")
        return value > threshold


class UpdateValueAction(Action):
    """Update value in blackboard"""
    
    def __init__(self, name: str = "", **kwargs):
        super().__init__(name)
        self.params = kwargs
    
    async def execute(self):
        increment = self.blackboard.get("increment", 10)
        current = self.blackboard.get("current_value", 0)
        
        new_value = current + increment
        self.blackboard.set("current_value", new_value)
        
        print(f"Update: {current} + {increment} = {new_value}")
        return Status.SUCCESS


class SetConfigAction(Action):
    """Set configuration in blackboard"""
    
    def __init__(self, name: str = "", **kwargs):
        super().__init__(name)
        self.params = kwargs
    
    async def execute(self):
        config_name = self.blackboard.get("config_name", "default")
        config_value = self.blackboard.get("config_value", {})
        
        self.blackboard.set(f"config_{config_name}", config_value)
        print(f"Set config '{config_name}': {config_value}")
        return Status.SUCCESS


def register_custom_nodes():
    """Register custom node types"""
    register_node("CheckValueCondition", CheckValueCondition)
    register_node("UpdateValueAction", UpdateValueAction)
    register_node("SetConfigAction", SetConfigAction)


async def main():
    """Demonstrate {} parameter passing"""
    
    print("=== {} Parameter Passing Demo ===\n")
    
    register_custom_nodes()
    
    # Create behavior tree with {} parameter substitution
    tree = BehaviorTree()
    blackboard = tree.blackboard
    
    # Set blackboard values for {} substitution
    blackboard.set("increment", 15)
    blackboard.set("threshold", 25)
    blackboard.set("float_increment", 5.5)
    blackboard.set("config_dict", {"enabled": True, "timeout": 30})
    blackboard.set("current_value", 0)
    
    # Create nodes with {} parameter substitution
    update_action1 = UpdateValueAction("Update1", increment="{increment}")
    check_condition = CheckValueCondition("Check", threshold="{threshold}")
    update_action2 = UpdateValueAction("Update2", increment="{float_increment}")
    set_config_action = SetConfigAction("SetConfig", config_name="settings", config_value="{config_dict}")
    
    # Build tree structure
    from abtree.nodes.composite import Sequence
    sequence = Sequence("Root")
    sequence.add_child(update_action1)
    sequence.add_child(check_condition)
    sequence.add_child(update_action2)
    sequence.add_child(set_config_action)
    
    tree.load_from_node(sequence)
    
    print("Tree Configuration:")
    print("  Sequence(Root)")
    print("    ├── UpdateValueAction(increment='{increment}')")
    print("    ├── CheckValueCondition(threshold='{threshold}')")
    print("    ├── UpdateValueAction(increment='{float_increment}')")
    print("    └── SetConfigAction(config_name='settings', config_value='{config_dict}')")
    
    print("\nBlackboard values for substitution:")
    print(f"  increment: {blackboard.get('increment')}")
    print(f"  threshold: {blackboard.get('threshold')}")
    print(f"  float_increment: {blackboard.get('float_increment')}")
    print(f"  config_dict: {blackboard.get('config_dict')}")
    
    print("\nExecuting...")
    result = await tree.tick()
    
    print(f"\nResult: {result}")
    print(f"Final value: {blackboard.get('current_value')}")
    print(f"Config set: {blackboard.get('config_settings')}")
    
    # Demonstrate parameter substitution in different scenarios
    print("\n=== Parameter Substitution Scenarios ===")
    
    # Scenario 1: Different threshold
    print("\nScenario 1: Higher threshold")
    blackboard.set("threshold", 40)
    blackboard.set("current_value", 35)
    result2 = await tree.tick()
    print(f"Result: {result2}")
    
    # Scenario 2: Different increment
    print("\nScenario 2: Larger increment")
    blackboard.set("increment", 25)
    blackboard.set("current_value", 10)
    result3 = await tree.tick()
    print(f"Result: {result3}")
    
    # Scenario 3: Different config
    print("\nScenario 3: New config")
    blackboard.set("config_dict", {"mode": "debug", "level": 3})
    result4 = await tree.tick()
    print(f"Result: {result4}")
    print(f"New config: {blackboard.get('config_settings')}")


if __name__ == "__main__":
    asyncio.run(main()) 