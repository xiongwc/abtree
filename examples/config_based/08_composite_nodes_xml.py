#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 08: Composite Nodes - XML Configuration Version

This is the XML configuration version of the Composite Nodes example.
It demonstrates how to configure various composite nodes using XML.

Key Learning Points:
    - How to define different types of composite nodes using XML
    - How to register custom composite node types
    - How to parse XML configuration with complex composite logic
    - Understanding composite node execution patterns in XML
"""

import asyncio
import random
from abtree import BehaviorTree, Action, register_node, Condition
from abtree.nodes.composite import CompositeNode
from abtree.core import Status


class ParallelNode(CompositeNode):
    """Parallel node - execute multiple child nodes simultaneously"""
    
    def __init__(self, name, children=None, success_policy="ALL", failure_policy="ANY"):
        super().__init__(name)
        self.children = children or []
        self.success_policy = success_policy  # "ALL", "ANY", "MAJORITY"
        self.failure_policy = failure_policy  # "ALL", "ANY", "MAJORITY"
    
    def add_child(self, child):
        self.children.append(child)
    
    async def tick(self, blackboard):
        print(f"Parallel node {self.name}: executing {len(self.children)} child nodes")
        
        # Execute all child nodes simultaneously
        tasks = [child.tick(blackboard) for child in self.children]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count results
        success_count = sum(1 for r in results if r == Status.SUCCESS)
        failure_count = sum(1 for r in results if r == Status.FAILURE)
        running_count = sum(1 for r in results if r == Status.RUNNING)
        
        print(f"Parallel node {self.name}: success={success_count}, failure={failure_count}, running={running_count}")
        
        # Determine final result based on policy
        if self.success_policy == "ALL":
            success = success_count == len(self.children)
        elif self.success_policy == "ANY":
            success = success_count > 0
        elif self.success_policy == "MAJORITY":
            success = success_count > len(self.children) // 2
        else:
            success = False
        
        if self.failure_policy == "ALL":
            failure = failure_count == len(self.children)
        elif self.failure_policy == "ANY":
            failure = failure_count > 0
        elif self.failure_policy == "MAJORITY":
            failure = failure_count > len(self.children) // 2
        else:
            failure = False
        
        if failure:
            return Status.FAILURE
        elif success:
            return Status.SUCCESS
        else:
            return Status.RUNNING


class PriorityNode(CompositeNode):
    """Priority node - execute child nodes in priority order"""
    
    def __init__(self, name, children=None):
        super().__init__(name)
        self.children = children or []
        self.current_index = 0
    
    def add_child(self, child):
        self.children.append(child)
    
    async def tick(self, blackboard):
        print(f"Priority node {self.name}: current index {self.current_index}")
        
        # Try executing child nodes starting from current index
        for i in range(self.current_index, len(self.children)):
            child = self.children[i]
            print(f"Priority node {self.name}: trying to execute child node {i}: {child.name}")
            
            result = await child.tick(blackboard)
            
            if result == Status.SUCCESS:
                print(f"Priority node {self.name}: child {i} succeeded, resetting index")
                self.current_index = 0
                return Status.SUCCESS
            elif result == Status.RUNNING:
                print(f"Priority node {self.name}: child {i} running, keeping index")
                self.current_index = i
                return Status.RUNNING
        
        # All children failed
        print(f"Priority node {self.name}: all children failed, resetting index")
        self.current_index = 0
        return Status.FAILURE


class RandomSelector(CompositeNode):
    """Random selector - randomly choose one child to execute"""
    
    def __init__(self, name, children=None):
        super().__init__(name)
        self.children = children or []
    
    def add_child(self, child):
        self.children.append(child)
    
    async def tick(self, blackboard):
        if not self.children:
            return Status.FAILURE
        
        # Randomly select a child
        selected_child = random.choice(self.children)
        print(f"Random selector {self.name}: selected child '{selected_child.name}'")
        
        return await selected_child.tick(blackboard)


class MemorySequence(CompositeNode):
    """Memory sequence - remembers the last executed child"""
    
    def __init__(self, name, children=None):
        super().__init__(name)
        self.children = children or []
        self.current_index = 0
    
    def add_child(self, child):
        self.children.append(child)
    
    async def tick(self, blackboard):
        print(f"Memory sequence {self.name}: current index {self.current_index}")
        
        # Execute children from current index
        for i in range(self.current_index, len(self.children)):
            child = self.children[i]
            print(f"Memory sequence {self.name}: executing child {i}: {child.name}")
            
            result = await child.tick(blackboard)
            
            if result == Status.SUCCESS:
                print(f"Memory sequence {self.name}: child {i} succeeded, continuing")
                continue
            elif result == Status.RUNNING:
                print(f"Memory sequence {self.name}: child {i} running, staying at index {i}")
                self.current_index = i
                return Status.RUNNING
            else:  # FAILURE
                print(f"Memory sequence {self.name}: child {i} failed, resetting to beginning")
                self.current_index = 0
                return Status.FAILURE
        
        # All children succeeded
        print(f"Memory sequence {self.name}: all children succeeded, resetting to beginning")
        self.current_index = 0
        return Status.SUCCESS


class WeightedSelector(CompositeNode):
    """Weighted selector - choose child based on weights"""
    
    def __init__(self, name, children=None, weights=None):
        super().__init__(name)
        self.children = children or []
        self.weights = weights or []
    
    def add_child(self, child, weight=1):
        self.children.append(child)
        self.weights.append(weight)
    
    async def tick(self, blackboard):
        if not self.children:
            return Status.FAILURE
        
        # Calculate total weight
        total_weight = sum(self.weights)
        if total_weight == 0:
            return Status.FAILURE
        
        # Generate random value
        random_value = random.uniform(0, total_weight)
        
        # Select child based on weights
        cumulative_weight = 0
        selected_index = 0
        for i, weight in enumerate(self.weights):
            cumulative_weight += weight
            if random_value <= cumulative_weight:
                selected_index = i
                break
        
        selected_child = self.children[selected_index]
        print(f"Weighted selector {self.name}: selected child '{selected_child.name}' (weight={self.weights[selected_index]})")
        
        return await selected_child.tick(blackboard)


class TestAction(Action):
    """Test action for demonstration"""
    
    def __init__(self, name, success_rate=0.8, duration=0.1):  # Reduced duration from 0.5
        self.name = name
        self.success_rate = success_rate
        self.duration = duration
    
    async def execute(self, blackboard):
        print(f"Executing test action: {self.name}")
        await asyncio.sleep(self.duration)
        
        if random.random() < self.success_rate:
            print(f"  {self.name} succeeded")
            return Status.SUCCESS
        else:
            print(f"  {self.name} failed")
            return Status.FAILURE


class TestCondition(Condition):
    """Test condition for demonstration"""
    
    def __init__(self, name, success_rate=0.7):
        self.name = name
        self.success_rate = success_rate
    
    async def evaluate(self, blackboard):
        print(f"Evaluating test condition: {self.name}")
        await asyncio.sleep(0.02)  # Reduced from 0.1
        
        if random.random() < self.success_rate:
            print(f"  {self.name} condition met")
            return True
        else:
            print(f"  {self.name} condition not met")
            return False


def register_custom_nodes():
    """Register custom node types for XML parsing"""
    register_node("ParallelNode", ParallelNode)
    register_node("PriorityNode", PriorityNode)
    register_node("RandomSelector", RandomSelector)
    register_node("MemorySequence", MemorySequence)
    register_node("WeightedSelector", WeightedSelector)
    register_node("TestAction", TestAction)
    register_node("TestCondition", TestCondition)


async def main():
    """Main function - demonstrate XML-based composite node configuration"""
    
    print("=== ABTree Composite Nodes XML Configuration Example ===\n")
    
    # Register custom node types for XML parsing
    register_custom_nodes()
    
    # XML string configuration
    xml_config = '''
    <BehaviorTree name="CompositeNodesXML" description="Composite nodes example with XML configuration">
        <Sequence name="Root Sequence">
            <Sequence name="Parallel Node Test">
                <ParallelNode name="Parallel Test" success_policy="ANY" failure_policy="ANY">
                    <TestAction name="Parallel Action 1" success_rate="0.6" duration="0.05" />
                    <TestAction name="Parallel Action 2" success_rate="0.7" duration="0.05" />
                    <TestAction name="Parallel Action 3" success_rate="0.8" duration="0.05" />
                </ParallelNode>
            </Sequence>
            <Sequence name="Priority Node Test">
                <PriorityNode name="Priority Test">
                    <TestAction name="Priority Action 1" success_rate="0.9" duration="0.03" />
                    <TestAction name="Priority Action 2" success_rate="0.8" duration="0.03" />
                    <TestAction name="Priority Action 3" success_rate="0.7" duration="0.03" />
                </PriorityNode>
            </Sequence>
            <Sequence name="Random Selector Test">
                <RandomSelector name="Random Test">
                    <TestAction name="Random Action 1" success_rate="0.6" duration="0.03" />
                    <TestAction name="Random Action 2" success_rate="0.7" duration="0.03" />
                    <TestAction name="Random Action 3" success_rate="0.8" duration="0.03" />
                </RandomSelector>
            </Sequence>
            <Sequence name="Memory Sequence Test">
                <MemorySequence name="Memory Test">
                    <TestAction name="Memory Action 1" success_rate="0.9" duration="0.03" />
                    <TestAction name="Memory Action 2" success_rate="0.8" duration="0.03" />
                    <TestAction name="Memory Action 3" success_rate="0.7" duration="0.03" />
                </MemorySequence>
            </Sequence>
            <Sequence name="Weighted Selector Test">
                <WeightedSelector name="Weighted Test">
                    <TestAction name="Weighted Action 1" success_rate="0.6" duration="0.03" />
                    <TestAction name="Weighted Action 2" success_rate="0.7" duration="0.03" />
                    <TestAction name="Weighted Action 3" success_rate="0.8" duration="0.03" />
                </WeightedSelector>
            </Sequence>
        </Sequence>
    </BehaviorTree>
    '''
    
    # Parse XML configuration
    xml_tree = BehaviorTree()
    xml_tree.load_from_string(xml_config)
    
    print("Behavior tree configured by XML string:")
    print(xml_config.strip())
    print("\nStarting execution of XML-configured behavior tree...")
    
    # Execute behavior tree
    xml_result = await xml_tree.tick()
    
    print(f"\nXML configuration execution completed! Result: {xml_result}")


if __name__ == "__main__":
    asyncio.run(main()) 