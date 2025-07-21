#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 06: Condition Nodes in Depth – Using Various Condition Nodes

Demonstrates how to create and use different types of condition nodes.
Condition nodes determine whether specific conditions are met and serve as decision points in a behavior tree.

Key Learning Points:

    Basic structure of condition nodes

    Complex condition evaluations

    Blackboard data inspection

    Dynamic condition checking

    How to configure condition nodes using XML strings
"""

import asyncio
import time
from abtree import BehaviorTree, Sequence, Selector, Action, Condition, register_node
from abtree.core import Status
from abtree.parser.xml_parser import XMLParser


# 注册自定义节点类型
def register_custom_nodes():
    """注册自定义节点类型"""
    register_node("SimpleCondition", SimpleCondition)
    register_node("ThresholdCondition", ThresholdCondition)
    register_node("TimeBasedCondition", TimeBasedCondition)
    register_node("CompositeCondition", CompositeCondition)
    register_node("StateCheckCondition", StateCheckCondition)
    register_node("DynamicCondition", DynamicCondition)
    register_node("Action1", Action1)
    register_node("Action2", Action2)


class SimpleCondition(Condition):
    """Simple condition node - always returns True"""
    
    async def evaluate(self, blackboard):
        print(f"Checking simple condition: {self.name}")
        return True


class ThresholdCondition(Condition):
    """Threshold condition node - checks if value exceeds threshold"""
    
    def __init__(self, name, key, threshold, operator=">"):
        super().__init__(name)
        self.key = key
        self.threshold = threshold
        self.operator = operator
    
    async def evaluate(self, blackboard):
        value = blackboard.get(self.key, 0)
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
        super().__init__(name)
        self.start_time = start_time
        self.end_time = end_time
    
    async def evaluate(self, blackboard):
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
        super().__init__(name)
        self.conditions = conditions
        self.logic = logic  # "AND" or "OR"
    
    async def evaluate(self, blackboard):
        print(f"Checking composite condition: {self.name} ({self.logic})")
        
        results = []
        for condition in self.conditions:
            result = await condition.evaluate(blackboard)
            results.append(result)
            print(f"  Sub-condition {condition.name}: {result}")
        
        if self.logic == "AND":
            final_result = all(results)
        else:  # OR
            final_result = any(results)
        
        print(f"Composite condition result: {final_result}")
        return final_result


class StateCheckCondition(Condition):
    """State check condition node"""
    
    def __init__(self, name, state_key, expected_value):
        super().__init__(name)
        self.state_key = state_key
        self.expected_value = expected_value
    
    async def evaluate(self, blackboard):
        current_state = blackboard.get(self.state_key, None)
        result = current_state == self.expected_value
        
        print(f"State check {self.name}: {self.state_key}={current_state} == {self.expected_value} = {result}")
        return result


class DynamicCondition(Condition):
    """Dynamic condition node - adjusts conditions based on blackboard data"""
    
    def __init__(self, name, base_key, modifier_key="modifier"):
        super().__init__(name)
        self.base_key = base_key
        self.modifier_key = modifier_key
    
    async def evaluate(self, blackboard):
        base_value = blackboard.get(self.base_key, 0)
        modifier = blackboard.get(self.modifier_key, 1.0)
        
        # Dynamically adjust threshold
        adjusted_value = base_value * modifier
        threshold = 50  # Fixed threshold
        
        result = adjusted_value > threshold
        
        print(f"Dynamic condition {self.name}: {base_value} * {modifier} = {adjusted_value} > {threshold} = {result}")
        return result


class Action1(Action):
    """Test action 1"""
    
    async def execute(self, blackboard):
        print(f"Executing action: {self.name}")
        blackboard.set("counter", blackboard.get("counter", 0) + 1)
        return Status.SUCCESS


class Action2(Action):
    """Test action 2"""
    
    async def execute(self, blackboard):
        print(f"Executing action: {self.name}")
        blackboard.set("state", "completed")
        return Status.SUCCESS


async def main():
    """Main function - demonstrate various condition node usage"""
    
    # 注册自定义节点类型
    register_custom_nodes()
    
    print("=== ABTree Condition Nodes Detailed Example ===\n")
    
    # 1. Create behavior tree
    root = Selector("Condition Node Test")
    
    # 2. Create various condition nodes
    # Threshold conditions
    battery_condition = ThresholdCondition("Battery Check", "battery_level", 20, ">")
    temperature_condition = ThresholdCondition("Temperature Check", "temperature", 30, "<")
    
    # Time condition
    time_condition = TimeBasedCondition("Time Check", start_time=time.time(), end_time=time.time() + 10)
    
    # State condition
    state_condition = StateCheckCondition("State Check", "system_state", "ready")
    
    # Dynamic condition
    dynamic_condition = DynamicCondition("Dynamic Check", "base_value", "multiplier")
    
    # Composite condition
    composite_condition = CompositeCondition("Composite Check", [battery_condition, temperature_condition], "AND")
    
    # 3. Create test sequences
    # Simple condition test
    simple_test = Sequence("Simple Condition Test")
    simple_test.add_child(SimpleCondition("Always True"))
    simple_test.add_child(Action1("Action 1"))
    
    # Threshold condition test
    threshold_test = Sequence("Threshold Condition Test")
    threshold_test.add_child(battery_condition)
    threshold_test.add_child(Action1("Battery Action"))
    
    # Composite condition test
    composite_test = Sequence("Composite Condition Test")
    composite_test.add_child(composite_condition)
    composite_test.add_child(Action2("Composite Action"))
    
    # State condition test
    state_test = Sequence("State Condition Test")
    state_test.add_child(state_condition)
    state_test.add_child(Action2("State Action"))
    
    # 4. Add to root node
    root.add_child(simple_test)
    root.add_child(threshold_test)
    root.add_child(composite_test)
    root.add_child(state_test)
    
    # 3. Create behavior tree
    tree = BehaviorTree()
    tree.load_from_root(root)
    blackboard = tree.blackboard
    
    # 6. Set test data
    blackboard.set("battery_level", 80)
    blackboard.set("temperature", 25)
    blackboard.set("system_state", "ready")
    blackboard.set("base_value", 30)
    blackboard.set("multiplier", 2.0)
    blackboard.set("counter", 0)
    
    print("Initial state:")
    print(f"  Battery level: {blackboard.get('battery_level')}%")
    print(f"  Temperature: {blackboard.get('temperature')}°C")
    print(f"  System state: {blackboard.get('system_state')}")
    print(f"  Base value: {blackboard.get('base_value')}")
    print(f"  Multiplier: {blackboard.get('multiplier')}")
    
    print("\nStarting condition node test...")
    print("=" * 50)
    
    # 7. Execute behavior tree
    result = await tree.tick()
    
    # 8. Display results
    print("=" * 50)
    print(f"Execution result: {result}")
    print(f"Counter: {blackboard.get('counter')}")
    print(f"Final state: {blackboard.get('state', 'unknown')}")
    
    # 9. Demonstrate XML configuration method
    print("\n=== XML Configuration Method Demo ===")
    
    # XML string configuration
    xml_config = '''
    <BehaviorTree name="ConditionNodesXML" description="Condition nodes example with XML configuration">
        <Sequence name="Root Sequence">
            <Selector name="Condition Node Test">
                <Sequence name="Simple Condition Test">
                    <SimpleCondition name="Always True" />
                    <Action1 name="Action 1" />
                </Sequence>
                <Sequence name="Threshold Condition Test">
                    <ThresholdCondition name="Battery Check" key="battery_level" threshold="20" operator=">" />
                    <Action1 name="Battery Action" />
                </Sequence>
                <Sequence name="State Condition Test">
                    <StateCheckCondition name="State Check" state_key="system_state" expected_value="ready" />
                    <Action2 name="State Action" />
                </Sequence>
            </Selector>
        </Sequence>
    </BehaviorTree>
    '''
    
    # Parse XML configuration
    xml_tree = BehaviorTree()
    xml_tree.load_from_string(xml_config)
    xml_blackboard = xml_tree.blackboard
    
    # Set XML configuration test data
    xml_blackboard.set("battery_level", 90)
    xml_blackboard.set("system_state", "ready")
    xml_blackboard.set("counter", 0)
    
    print("Behavior tree configured by XML string:")
    print(xml_config.strip())
    print("\nStarting execution of XML-configured behavior tree...")
    xml_result = await xml_tree.tick()
    print(f"XML configuration execution completed! Result: {xml_result}")
    print(f"XML configuration counter: {xml_blackboard.get('counter')}")


if __name__ == "__main__":
    asyncio.run(main()) 