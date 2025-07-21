#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 03: Selector Basics – Using the Selector Node

Demonstrates how to use the Selector node to implement conditional selection logic.
The Selector node tries its child nodes in order until one succeeds.

Key Learning Points:

    Usage of the Selector node

    Concept of conditional selection

    Priority handling

    Fallback mechanism on failure

    How to configure a Selector node using an XML string
"""

import asyncio
from abtree import BehaviorTree, Selector, Sequence, Action, Condition, register_node
from abtree.core import Status
from abtree.parser.xml_parser import XMLParser


class CheckNetworkCondition(Condition):
    """Check network connection status"""
    
    async def evaluate(self, blackboard):
        # Simulate network check
        network_available = blackboard.get("network_available", False)
        print(f"Checking network connection: {'Available' if network_available else 'Unavailable'}")
        return network_available


class CheckLocalStorageCondition(Condition):
    """Check local storage status"""
    
    async def evaluate(self, blackboard):
        # Simulate storage check
        storage_available = blackboard.get("storage_available", False)
        print(f"Checking local storage: {'Available' if storage_available else 'Unavailable'}")
        return storage_available


class NetworkAction(Action):
    """Network operation"""
    
    async def execute(self, blackboard):
        print("Executing network operation...")
        await asyncio.sleep(0.01)
        print("Network operation completed")
        return Status.SUCCESS


class LocalAction(Action):
    """Local operation"""
    
    async def execute(self, blackboard):
        print("Executing local operation...")
        await asyncio.sleep(0.01)
        print("Local operation completed")
        return Status.SUCCESS


class FallbackAction(Action):
    """Fallback operation"""
    
    async def execute(self, blackboard):
        print("Executing fallback operation...")
        await asyncio.sleep(0.01)
        print("Fallback operation completed")
        return Status.SUCCESS


async def main():
    """Main function - demonstrate Selector node usage"""
    
    print("=== ABTree Selector Basic Example ===\n")
    
    # Register custom node types
    register_node("CheckNetworkCondition", CheckNetworkCondition)
    register_node("CheckLocalStorageCondition", CheckLocalStorageCondition)
    register_node("NetworkAction", NetworkAction)
    register_node("LocalAction", LocalAction)
    register_node("FallbackAction", FallbackAction)
    
    # 1. Create Selector node
    selector = Selector("Data Retrieval Strategy")
    
    # 2. Add child nodes (ordered by priority)
    selector.add_child(Sequence("Network Strategy"))
    selector.children[0].add_child(CheckNetworkCondition("Check Network"))
    selector.children[0].add_child(NetworkAction("Network Operation"))
    
    selector.add_child(Sequence("Local Strategy"))
    selector.children[1].add_child(CheckLocalStorageCondition("Check Storage"))
    selector.children[1].add_child(LocalAction("Local Operation"))
    
    selector.add_child(FallbackAction("Fallback Strategy"))
    
    # 3. Create behavior tree
    tree = BehaviorTree()
    tree.load_from_node(selector)
    
    # 4. Test different scenarios
    scenarios = [
        {"name": "Network Available", "network_available": True, "storage_available": False},
        {"name": "Network Unavailable, Storage Available", "network_available": False, "storage_available": True},
        {"name": "Both Unavailable", "network_available": False, "storage_available": False},
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n--- Test Scenario {i}: {scenario['name']} ---")
        
        # Set blackboard data
        blackboard = tree.blackboard
        blackboard.set("network_available", scenario["network_available"])
        blackboard.set("storage_available", scenario["storage_available"])
        
        # Execute behavior tree
        result = await tree.tick()
        print(f"Execution result: {result}")   


if __name__ == "__main__":
    asyncio.run(main()) 