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
from abtree.nodes.action import blackboard_binding


class GetValueAction(Action):
    """Update value in blackboard"""
    
    def __init__(self, name: str = "", value_a: str = ""):
        super().__init__(name)
        self.value_a = value_a
    
    @blackboard_binding
    async def execute(self, blackboard):
        print(f"GetValueAction - Mapping relationships: {self.get_param_mappings()}")
        print(f"GetValueAction - value_a before setting: {self.value_a}")
        
        # Set property, decorator will automatically sync to blackboard
        self.value_a = "1234567"
        
        print(f"GetValueAction - value_a after setting: {self.value_a}")
        
        return Status.SUCCESS

class SetValueAction(Action):
    """Set configuration in blackboard"""
    
    def __init__(self, name: str = "", value_b: str = ""):
        super().__init__(name)
        self.value_b = value_b
    
    @blackboard_binding
    async def execute(self, blackboard):     
        print(f"SetValueAction - Mapping relationships: {self.get_param_mappings()}")
        print(f"SetValueAction - value_b: {self.value_b}")
        
        value_b = blackboard.get("exchange_value")
        print(f"value_b from blackboard: {value_b}")
        value_b = self.value_b       
        print(f"Set value: {value_b}")
        return Status.SUCCESS


def register_custom_nodes():
    """Register custom node types"""
    register_node("GetValueAction", GetValueAction)
    register_node("SetValueAction", SetValueAction)


async def main():
    """Demonstrate {} parameter passing in XML"""
    
    print("=== {} Parameter Passing Demo ===\n")
    
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