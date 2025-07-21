#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 02: Simple Sequence - Using the Sequence Node

Demonstrates how to use a Sequence node to execute multiple actions in order.
The Sequence node runs all its child nodes sequentially, and if any one of them fails, the entire sequence fails.

Key Learning Points:

    Usage of the Sequence node

    Adding child nodes

    Concept of sequential execution

    Failure handling mechanism

    How to configure a Sequence node using an XML string
"""

import asyncio
from abtree import BehaviorTree, Sequence, Action, register_node
from abtree.core import Status
from abtree.parser.xml_parser import XMLParser


class Step1Action(Action):
    """First step action"""
    
    async def execute(self, blackboard):
        print("Step 1: Check system status")
        await asyncio.sleep(0.01)  # Simulate processing time
        return Status.SUCCESS


class Step2Action(Action):
    """Second step action"""
    
    async def execute(self, blackboard):
        print("Step 2: Initialize components")
        await asyncio.sleep(0.01)
        return Status.SUCCESS


class Step3Action(Action):
    """Third step action"""
    
    async def execute(self, blackboard):
        print("Step 3: Start services")
        await asyncio.sleep(0.01)
        return Status.SUCCESS


class SuccessAction(Action):
    """Action that always succeeds"""
    
    async def execute(self, blackboard):
        print("Success action executed")
        return Status.SUCCESS


class FailAction(Action):
    """Action that always fails"""
    
    async def execute(self, blackboard):
        print("Fail action executed")
        return Status.FAILURE


async def main():
    """Main function - demonstrate Sequence node usage"""
    
    print("=== ABTree Simple Sequence Example ===\n")
    
    # Register custom node types
    register_node("Step1Action", Step1Action)
    register_node("Step2Action", Step2Action)
    register_node("Step3Action", Step3Action)
    
    # 1. Create Sequence node
    sequence = Sequence("System Startup Sequence")
    
    # 2. Add child nodes
    sequence.add_child(Step1Action("Check Status"))
    sequence.add_child(Step2Action("Initialize"))
    sequence.add_child(Step3Action("Start Services"))
    
    # 3. Create behavior tree
    tree = BehaviorTree()
    tree.load_from_node(sequence)
    
    # 4. Execute behavior tree
    print("Start executing behavior tree...")
    result = await tree.tick()
    
    # 5. Output result
    print(f"\nExecution completed! Result: {result}")
    print(f"Status description: {result.name}")
    
    # 6. Demonstrate failure scenario
    print("\n=== Failure scenario demonstration ===")
    
    # Create a sequence that will fail
    fail_sequence = Sequence("FailSequence")
    success_action = SuccessAction("SuccessAction")
    fail_action = FailAction("FailAction")
    final_action = SuccessAction("FinalAction")
    
    fail_sequence.add_child(success_action)
    fail_sequence.add_child(fail_action)  # This will cause the sequence to fail
    fail_sequence.add_child(final_action)  # This will not execute
    
    # Create behavior tree for failure scenario
    fail_tree = BehaviorTree()
    fail_tree.load_from_node(fail_sequence)
    
    # Execute failure scenario
    print("Start executing failure scenario...")
    fail_result = await fail_tree.tick()
    print(f"Failure scenario result: {fail_result}")   


if __name__ == "__main__":
    asyncio.run(main()) 