#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 03: Selector Basic - XML Configuration Version

This is the XML configuration version of the Selector Basic example.
It demonstrates how to configure selector nodes using XML instead of code.

Key Learning Points:
    - How to define selector nodes using XML
    - How to register custom condition and action node types
    - How to parse XML configuration with fallback strategies
    - Understanding selector execution order in XML
"""

import asyncio
from abtree import BehaviorTree, Action, Condition, register_node
from abtree.core import Status


class CheckNetworkCondition(Condition):
    """Check if network is available"""
    
    async def evaluate(self, blackboard):
        # Simulate network check
        network_available = blackboard.get("network_available", False)
        print(f"Checking network availability: {network_available}")
        return network_available


class CheckLocalStorageCondition(Condition):
    """Check if local storage is available"""
    
    async def evaluate(self, blackboard):
        # Simulate storage check
        storage_available = blackboard.get("storage_available", False)
        print(f"Checking local storage availability: {storage_available}")
        return storage_available


class NetworkAction(Action):
    """Action to retrieve data from network"""
    
    async def execute(self, blackboard):
        print("Executing network operation...")
        await asyncio.sleep(0.01)
        print("Network operation completed")
        return Status.SUCCESS


class LocalAction(Action):
    """Action to retrieve data from local storage"""
    
    async def execute(self, blackboard):
        print("Executing local storage operation...")
        await asyncio.sleep(0.01)
        print("Local storage operation completed")
        return Status.SUCCESS


class FallbackAction(Action):
    """Fallback operation"""
    
    async def execute(self, blackboard):
        print("Executing fallback operation...")
        await asyncio.sleep(0.01)
        print("Fallback operation completed")
        return Status.SUCCESS


async def main():
    """Main function - demonstrate XML-based selector configuration"""
    
    print("=== ABTree Selector Basic XML Configuration Example ===\n")
    
    # Register custom node types for XML parsing
    register_node("CheckNetworkCondition", CheckNetworkCondition)
    register_node("CheckLocalStorageCondition", CheckLocalStorageCondition)
    register_node("NetworkAction", NetworkAction)
    register_node("LocalAction", LocalAction)
    register_node("FallbackAction", FallbackAction)
    
    # XML string configuration
    xml_config = '''
    <BehaviorTree name="SelectorBasicXML" description="Selector basic example with XML configuration">
        <Sequence name="Root Sequence">
            <Selector name="Data Retrieval Strategy">
                <Sequence name="Network Strategy">
                    <CheckNetworkCondition name="Check Network" />
                    <NetworkAction name="Network Operation" />
                </Sequence>
                <Sequence name="Local Strategy">
                    <CheckLocalStorageCondition name="Check Storage" />
                    <LocalAction name="Local Operation" />
                </Sequence>
                <FallbackAction name="Fallback Strategy" />
            </Selector>
        </Sequence>
    </BehaviorTree>
    '''
    
    # Parse XML configuration
    xml_tree = BehaviorTree()
    xml_tree.load_from_string(xml_config)
    
    print("Behavior tree configured by XML string:")
    print(xml_config.strip())
    print("\nStarting execution of XML-configured behavior tree...")
    
    # Test different scenarios
    scenarios = [
        {"name": "Network Available", "network_available": True, "storage_available": False},
        {"name": "Network Unavailable, Storage Available", "network_available": False, "storage_available": True},
        {"name": "Both Unavailable", "network_available": False, "storage_available": False},
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n--- Test Scenario {i}: {scenario['name']} ---")
        
        # Set blackboard data
        blackboard = xml_tree.blackboard
        blackboard.set("network_available", scenario["network_available"])
        blackboard.set("storage_available", scenario["storage_available"])
        
        # Execute behavior tree
        result = await xml_tree.tick()
        print(f"Execution result: {result}")


if __name__ == "__main__":
    asyncio.run(main()) 