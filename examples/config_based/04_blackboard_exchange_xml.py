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


class GetValueAction(Action):
    """Update value in blackboard"""
    
    def __init__(self, name: str = ""):
        super().__init__(name)
        # Don't store value_a as instance attribute, it will be passed to execute method
    
    async def execute(self, value_a):
        print(f"GetValueAction - Mapping relationships: {self.get_param_mappings()}")
        print(f"GetValueAction - value_a received: {value_a}")
        print(f"GetValueAction - blackboard: {self.blackboard}")
        if self.blackboard:
            print(f"GetValueAction - blackboard content: {self.blackboard._data}")

        # Set value using setPort method
        value_a = 100
        self.setPort(value_a)
        print(f"Set value_a to 100 using setPort")
        
        return Status.SUCCESS

class SetValueAction(Action):
    """Set configuration in blackboard"""
    
    def __init__(self, name: str = ""):
        super().__init__(name)
    
    async def execute(self, value_b):     
        print(f"SetValueAction - Mapping relationships: {self.get_param_mappings()}")
        print(f"SetValueAction - value_b received: {value_b}")
        print(f"SetValueAction - blackboard: {self.blackboard}")
        if self.blackboard:
            print(f"SetValueAction - blackboard content: {self.blackboard._data}")
        
        # Get value using getPort method
        received_value = self.getPort()
        print(f"Get value_b using getPort: {received_value}")
        
        print(f"Set value: {received_value}")
        return Status.SUCCESS


def register_custom_nodes():
    """Register custom node types"""
    register_node("GetValueAction", GetValueAction)
    register_node("SetValueAction", SetValueAction)


async def main():
    """Demonstrate {} parameter passing in XML"""
    
    print("=== {} Parameter Passing Demo ===\n")
    
    # Register custom nodes BEFORE creating the tree
    register_custom_nodes()
    
    # XML with {} parameter substitution
    xml_config = '''
    <BehaviorTree name="ParamDemo">
        <Sequence name="Root">
            <GetValueAction value_a="{exchange_value}" />
            <SetValueAction value_b="{exchange_value}" />
        </Sequence>
    </BehaviorTree>
    '''
    
    tree = BehaviorTree()
    tree.load_from_string(xml_config)

    await tree.tick() 


if __name__ == "__main__":
    asyncio.run(main()) 