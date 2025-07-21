#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 02: Simple Sequence - XML Configuration Version

This is the XML configuration version of the Simple Sequence example.
It demonstrates how to configure sequence nodes using XML instead of code.

Key Learning Points:
    - How to define sequence nodes using XML
    - How to register custom action node types
    - How to parse XML configuration with multiple actions
    - Understanding sequence execution order in XML
"""

import asyncio
from abtree import BehaviorTree, Action, register_node
from abtree.core import Status


class Step1Action(Action):
    """First step in the sequence"""
    
    async def execute(self, blackboard):
        print("Step 1: Checking system status...")
        await asyncio.sleep(0.01)  # Reduced from 0.5
        print("System status check completed")
        return Status.SUCCESS


class Step2Action(Action):
    """Second step in the sequence"""
    
    async def execute(self, blackboard):
        print("Step 2: Initializing system...")
        await asyncio.sleep(0.01)  # Reduced from 0.5
        print("System initialization completed")
        return Status.SUCCESS


class Step3Action(Action):
    """Third step in the sequence"""
    
    async def execute(self, blackboard):
        print("Step 3: Starting services...")
        await asyncio.sleep(0.01)  # Reduced from 0.5
        print("Services started successfully")
        return Status.SUCCESS


async def main():
    """Main function - demonstrate XML-based sequence configuration"""
    
    print("=== ABTree Simple Sequence XML Configuration Example ===\n")
    
    # Register custom node types for XML parsing
    register_node("Step1Action", Step1Action)
    register_node("Step2Action", Step2Action)
    register_node("Step3Action", Step3Action)
    
    # XML string configuration
    xml_config = '''
    <BehaviorTree name="SimpleSequenceXML" description="Simple sequence example with XML configuration">
        <Sequence name="Root Sequence">
            <Sequence name="System Startup Sequence">
                <Step1Action name="Check Status" />
                <Step2Action name="Initialize" />
                <Step3Action name="Start Services" />
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
    print(f"Status description: {xml_result.name}")


if __name__ == "__main__":
    asyncio.run(main()) 