#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 08: Composite Nodes in Depth – Using Various Composite Nodes

Demonstrates how to create and use different types of composite nodes.
Composite nodes combine multiple child nodes to implement complex control logic.

Key Learning Points:

    Basic structure of composite nodes

    Parallel execution mechanisms

    Priority handling

    Child node management

    Complex combination logic

    How to configure composite nodes using XML strings
"""

import asyncio
import random
from abtree import BehaviorTree, Sequence, Selector, Action, Condition, register_node
from abtree.core import Status
from abtree.parser.xml_parser import XMLParser


# Register custom node types
def register_custom_nodes():
    """Register custom node types"""
    register_node("TestAction", TestAction)
    register_node("TestCondition", TestCondition)


class ParallelNode:
    """Parallel node - execute multiple child nodes simultaneously"""
    
    def __init__(self, name, children=None, success_policy="ALL", failure_policy="ANY"):
        self.name = name
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


class PriorityNode:
    """Priority node - execute child nodes in priority order"""
    
    def __init__(self, name, children=None):
        self.name = name
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
                print(f"Priority node {self.name}: child node {i} succeeded, reset index")
                self.current_index = 0
                return Status.SUCCESS
            elif result == Status.RUNNING:
                print(f"Priority node {self.name}: child node {i} is running, keep index")
                self.current_index = i
                return Status.RUNNING
            else:  # FAILURE
                print(f"Priority node {self.name}: child node {i} failed, try next")
                continue
        
        # All child nodes failed
        print(f"Priority node {self.name}: all child nodes failed")
        self.current_index = 0
        return Status.FAILURE


class RandomSelector:
    """Random selector - randomly select a child node to execute"""
    
    def __init__(self, name, children=None):
        self.name = name
        self.children = children or []
    
    def add_child(self, child):
        self.children.append(child)
    
    async def tick(self, blackboard):
        if not self.children:
            return Status.FAILURE
        
        # Randomly select a child node
        selected_child = random.choice(self.children)
        print(f"Random selector {self.name}: selected child node {selected_child.name}")
        
        result = await selected_child.tick(blackboard)
        print(f"Random selector {self.name}: child node returned {result}")
        
        return result


class MemorySequence:
    """Memory sequence - remember the last executed position"""
    
    def __init__(self, name, children=None):
        self.name = name
        self.children = children or []
        self.current_index = 0
    
    def add_child(self, child):
        self.children.append(child)
    
    async def tick(self, blackboard):
        print(f"Memory sequence {self.name}: starting from position {self.current_index}")
        
        # Execute child nodes from remembered position
        for i in range(self.current_index, len(self.children)):
            child = self.children[i]
            print(f"Memory sequence {self.name}: executing child node {i}: {child.name}")
            
            result = await child.tick(blackboard)
            
            if result == Status.SUCCESS:
                print(f"Memory sequence {self.name}: child node {i} succeeded, continue next")
                continue
            elif result == Status.RUNNING:
                print(f"Memory sequence {self.name}: child node {i} is running, remember position")
                self.current_index = i
                return Status.RUNNING
            else:  # FAILURE
                print(f"Memory sequence {self.name}: child node {i} failed, reset position")
                self.current_index = 0
                return Status.FAILURE
        
        # All child nodes succeeded
        print(f"Memory sequence {self.name}: all child nodes succeeded, reset position")
        self.current_index = 0
        return Status.SUCCESS


class WeightedSelector:
    """Weighted selector - select child nodes based on weights"""
    
    def __init__(self, name, children=None, weights=None):
        self.name = name
        self.children = children or []
        self.weights = weights or [1] * len(self.children)
    
    def add_child(self, child, weight=1):
        self.children.append(child)
        self.weights.append(weight)
    
    async def tick(self, blackboard):
        if not self.children:
            return Status.FAILURE
        
        # Randomly select based on weights
        total_weight = sum(self.weights)
        rand_val = random.uniform(0, total_weight)
        
        cumulative_weight = 0
        selected_index = 0
        
        for i, weight in enumerate(self.weights):
            cumulative_weight += weight
            if rand_val <= cumulative_weight:
                selected_index = i
                break
        
        selected_child = self.children[selected_index]
        print(f"Weighted selector {self.name}: selected child node {selected_child.name} (weight: {self.weights[selected_index]})")
        
        result = await selected_child.tick(blackboard)
        print(f"Weighted selector {self.name}: child node returned {result}")
        
        return result


# Test action and condition nodes
class TestAction(Action):
    """Test action node"""
    
    def __init__(self, name, success_rate=0.8, duration=0.5):
        super().__init__(name)
        self.success_rate = success_rate
        self.duration = duration
    
    async def execute(self, blackboard):
        print(f"Executing test action: {self.name}")
        await asyncio.sleep(self.duration)
        
        success = random.random() < self.success_rate
        result = Status.SUCCESS if success else Status.FAILURE
        print(f"Test action {self.name}: {'success' if success else 'failure'}")
        
        return result


class TestCondition(Condition):
    """Test condition node"""
    
    def __init__(self, name, success_rate=0.7):
        super().__init__(name)
        self.success_rate = success_rate
    
    async def evaluate(self, blackboard):
        print(f"Checking test condition: {self.name}")
        
        success = random.random() < self.success_rate
        print(f"Test condition {self.name}: {'satisfied' if success else 'unsatisfied'}")
        
        return success


async def main():
    """Main function - demonstrate various composite node usage"""
    
    # Register custom node types
    register_custom_nodes()
    
    print("=== ABTree Composite Nodes Detailed Example ===\n")
    
    # 1. Test parallel node
    print("=== Parallel Node Test ===")
    parallel = ParallelNode("Parallel Test", success_policy="ANY", failure_policy="ANY")
    parallel.add_child(TestAction("Parallel Action 1", 0.8, 0.3))
    parallel.add_child(TestAction("Parallel Action 2", 0.6, 0.4))
    parallel.add_child(TestAction("Parallel Action 3", 0.9, 0.2))
    
    tree1 = BehaviorTree()
    tree1.load_from_node(parallel)
    result1 = await tree1.tick()
    print(f"Parallel node result: {result1}\n")
    
    # 2. Test priority node
    print("=== Priority Node Test ===")
    priority = PriorityNode("Priority Test")
    priority.add_child(TestAction("High Priority Action", 0.3, 0.2))  # Low success rate
    priority.add_child(TestAction("Medium Priority Action", 0.7, 0.2))
    priority.add_child(TestAction("Low Priority Action", 0.9, 0.2))
    
    tree2 = BehaviorTree()
    tree2.load_from_node(priority)
    result2 = await tree2.tick()
    print(f"Priority node result: {result2}\n")
    
    # 3. Test random selector
    print("=== Random Selector Test ===")
    random_selector = RandomSelector("Random Test")
    random_selector.add_child(TestAction("Random Action 1", 0.8, 0.2))
    random_selector.add_child(TestAction("Random Action 2", 0.8, 0.2))
    random_selector.add_child(TestAction("Random Action 3", 0.8, 0.2))
    
    tree3 = BehaviorTree()
    tree3.load_from_node(random_selector)
    result3 = await tree3.tick()
    print(f"Random selector result: {result3}\n")
    
    # 4. Test memory sequence
    print("=== Memory Sequence Test ===")
    memory_sequence = MemorySequence("Memory Test")
    memory_sequence.add_child(TestAction("Memory Action 1", 0.9, 0.2))
    memory_sequence.add_child(TestAction("Memory Action 2", 0.9, 0.2))
    memory_sequence.add_child(TestAction("Memory Action 3", 0.9, 0.2))
    
    tree4 = BehaviorTree()
    tree4.load_from_node(memory_sequence)
    result4 = await tree4.tick()
    print(f"Memory sequence result: {result4}\n")
    
    # 5. Test weighted selector
    print("=== Weighted Selector Test ===")
    weighted_selector = WeightedSelector("Weighted Test")
    weighted_selector.add_child(TestAction("High Weight Action", 0.8, 0.2), 3)
    weighted_selector.add_child(TestAction("Medium Weight Action", 0.8, 0.2), 2)
    weighted_selector.add_child(TestAction("Low Weight Action", 0.8, 0.2), 1)
    
    tree5 = BehaviorTree()
    tree5.load_from_node(weighted_selector)
    result5 = await tree5.tick()
    print(f"Weighted selector result: {result5}\n")
    
    print("All composite nodes test completed!") 
  


if __name__ == "__main__":
    asyncio.run(main()) 