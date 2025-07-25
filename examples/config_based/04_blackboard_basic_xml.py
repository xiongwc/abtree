#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 04: Blackboard Basic - XML Configuration Version

Demonstrates {} parameter passing in XML configuration.
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
    
    async def evaluate(self, threshold=None):
        if not self.blackboard:
            return False
            
        if threshold is None:
            threshold = self.get_mapped_value("threshold", 50)
        value = self.blackboard.get("current_value", 0)
        
        print(f"Check: {value} > {threshold} = {value > threshold}")
        return value > threshold


class UpdateValueAction(Action):
    """Update value in blackboard"""
    
    def __init__(self, name: str = "", **kwargs):
        super().__init__(name)
        self.params = kwargs
    
    async def execute(self, increment=None):
        if increment is None:
            increment = self.get_mapped_value("increment", 10)
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
    
    async def execute(self, config_value=None):
        config_name = self.blackboard.get("config_name", "default")
        if config_value is None:
            config_value = self.get_mapped_value("config_value", {})
        
        self.blackboard.set(f"config_{config_name}", config_value)
        print(f"Set config '{config_name}': {config_value}")
        return Status.SUCCESS


def register_custom_nodes():
    """Register custom node types"""
    register_node("CheckValueCondition", CheckValueCondition)
    register_node("UpdateValueAction", UpdateValueAction)
    register_node("SetConfigAction", SetConfigAction)


async def main():
    """Demonstrate {} parameter passing in XML"""
    
    print("=== {} Parameter Passing Demo ===\n")
    
    register_custom_nodes()
    
    # XML with {} parameter substitution
    xml_config = '''
    <BehaviorTree name="ParamDemo">
        <Sequence name="Root">
            <UpdateValueAction increment="{increment}" />
            <CheckValueCondition threshold="{threshold}" />
            <UpdateValueAction increment="{float_increment}" />
            <SetConfigAction config_name="settings" config_value="{config_dict}" />
        </Sequence>
    </BehaviorTree>
    '''
    
    tree = BehaviorTree()
    tree.load_from_string(xml_config)
    blackboard = tree.blackboard
    
    # Set blackboard values for {} substitution
    blackboard.set("increment", 15)
    blackboard.set("threshold", 25)
    blackboard.set("float_increment", 5.5)
    blackboard.set("config_dict", {"enabled": True, "timeout": 30})
    blackboard.set("current_value", 0)
    
    print("XML Configuration :")
    print(xml_config.strip())
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


if __name__ == "__main__":
    asyncio.run(main()) 