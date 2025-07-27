#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 06: Condition Nodes - XML Configuration Version

This is the XML configuration version of the Condition Nodes example.
It demonstrates how to configure various condition nodes using XML.

Key Learning Points:
    - How to define different types of condition nodes using XML
    - How to register custom condition node types
    - How to parse XML configuration with complex condition logic
    - Understanding condition evaluation patterns in XML
"""

import asyncio
import time
from abtree import BehaviorTree, Action, Condition, register_node
from abtree.core import Status


class SimpleCondition(Condition):
    """Simple condition node - always returns True"""
    
    async def evaluate(self):
        print(f"Checking simple condition: {self.name}")
        return True


class ThresholdCondition(Condition):
    """Threshold condition node - checks if value exceeds threshold"""
    
    def __init__(self, name, key, threshold, operator=">"):
        self.name = name
        self.key = key
        self.threshold = threshold
        self.operator = operator
    
    async def evaluate(self):
        value = self.blackboard.get(self.key, 0)
        print(f"Checking threshold condition: {self.name} - {self.key}={value} {self.operator} {self.threshold}")
        
        if self.operator == ">":
            return value > self.threshold
        elif self.operator == ">=":
            return value >= self.threshold
        elif self.operator == "<":
            return value < self.threshold
        elif self.operator == "<=":
            return value <= self.threshold
        elif self.operator == "==":
            return value == self.threshold
        else:
            return False


class TimeBasedCondition(Condition):
    """Time-based condition node"""
    
    def __init__(self, name, start_time=None, end_time=None):
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
    
    async def evaluate(self):
        current_time = time.time()
        
        # Check if within specified time range
        if self.start_time and current_time < self.start_time:
            print(f"Time condition {self.name}: Not yet start time")
            return False
        
        if self.end_time and current_time > self.end_time:
            print(f"Time condition {self.name}: Past end time")
            return False
        
        print(f"Time condition {self.name}: Within valid time range")
        return True


class CompositeCondition(Condition):
    """Composite condition node - combines multiple conditions"""
    
    def __init__(self, name, conditions, logic="AND"):
        self.name = name
        self.conditions = conditions
        self.logic = logic
    
    async def evaluate(self, blackboard):
        print(f"Evaluating composite condition: {self.name}")
        
        results = []
        for condition in self.conditions:
            result = await condition.evaluate(blackboard)
            results.append(result)
        
        if self.logic == "AND":
            final_result = all(results)
        elif self.logic == "OR":
            final_result = any(results)
        else:
            final_result = False
        
        print(f"Composite condition {self.name} result: {final_result}")
        return final_result


class StateCheckCondition(Condition):
    """State check condition node"""
    
    def __init__(self, name, state_key, expected_value):
        self.name = name
        self.state_key = state_key
        self.expected_value = expected_value
    
    async def evaluate(self, blackboard):
        current_state = blackboard.get(self.state_key, None)
        result = current_state == self.expected_value
        print(f"State check {self.name}: {self.state_key}={current_state}, expected={self.expected_value}, result={result}")
        return result


class DynamicCondition(Condition):
    """Dynamic condition node - uses modifier from blackboard"""
    
    def __init__(self, name, base_key, modifier_key="modifier"):
        self.name = name
        self.base_key = base_key
        self.modifier_key = modifier_key
    
    async def evaluate(self, blackboard):
        base_value = blackboard.get(self.base_key, 0)
        modifier = blackboard.get(self.modifier_key, 1.0)
        adjusted_value = base_value * modifier
        
        result = adjusted_value > 50  # Example threshold
        print(f"Dynamic condition {self.name}: base={base_value}, modifier={modifier}, adjusted={adjusted_value}, result={result}")
        return result


class Action1(Action):
    """Simple action for demonstration"""
    
    async def execute(self, blackboard):
        print(f"Executing action: {self.name}")
        await asyncio.sleep(0.02)
        return Status.SUCCESS


class Action2(Action):
    """Another simple action for demonstration"""
    
    async def execute(self, blackboard):
        print(f"Executing action: {self.name}")
        await asyncio.sleep(0.02)
        return Status.SUCCESS


def register_custom_nodes():
    """Register custom node types for XML parsing"""
    register_node("SimpleCondition", SimpleCondition)
    register_node("ThresholdCondition", ThresholdCondition)
    register_node("TimeBasedCondition", TimeBasedCondition)
    register_node("CompositeCondition", CompositeCondition)
    register_node("StateCheckCondition", StateCheckCondition)
    register_node("DynamicCondition", DynamicCondition)
    register_node("Action1", Action1)
    register_node("Action2", Action2)


async def main():
    """Main function - demonstrate XML-based condition node configuration"""
    
    print("=== ABTree Condition Nodes XML Configuration Example ===\n")
    
    # Register custom node types for XML parsing
    register_custom_nodes()
    
    # XML string configuration
    xml_config = '''
    <BehaviorTree name="ConditionNodes" description="Condition nodes example with XML configuration">
        <Sequence name="Root Sequence">
            <Selector name="Condition Tests">
                <Sequence name="Simple Condition Test">
                    <SimpleCondition name="Always True" />
                    <Action1 name="Action After Simple" />
                </Sequence>
                <Sequence name="Threshold Condition Test">
                    <ThresholdCondition name="Check High Value" key="test_value" threshold="50" operator=">" />
                    <Action1 name="Action After Threshold" />
                </Sequence>
                <Sequence name="State Condition Test">
                    <StateCheckCondition name="Check System State" state_key="system_state" expected_value="ready" />
                    <Action2 name="Action After State" />
                </Sequence>
                <Sequence name="Dynamic Condition Test">
                    <DynamicCondition name="Check Dynamic Value" base_key="dynamic_value" modifier_key="multiplier" />
                    <Action1 name="Action After Dynamic" />
                </Sequence>
            </Selector>
        </Sequence>
    </BehaviorTree>
    '''
    
    # Parse XML configuration
    xml_tree = BehaviorTree()
    xml_tree.load_from_string(xml_config)
    xml_blackboard = xml_tree.blackboard
    
    # Initialize test data
    xml_blackboard.set("test_value", 75)
    xml_blackboard.set("system_state", "ready")
    xml_blackboard.set("dynamic_value", 30)
    xml_blackboard.set("multiplier", 2.0)
    
    print("Behavior tree configured by XML string:")
    print(xml_config.strip())
    print("\nStarting execution of XML-configured behavior tree...")
    
    # Execute behavior tree
    xml_result = await xml_tree.tick()
    
    print(f"\nXML configuration execution completed! Result: {xml_result}")
    print(f"Test value: {xml_blackboard.get('test_value')}")
    print(f"System state: {xml_blackboard.get('system_state')}")
    print(f"Dynamic value: {xml_blackboard.get('dynamic_value')}")
    print(f"Multiplier: {xml_blackboard.get('multiplier')}")


if __name__ == "__main__":
    asyncio.run(main()) 